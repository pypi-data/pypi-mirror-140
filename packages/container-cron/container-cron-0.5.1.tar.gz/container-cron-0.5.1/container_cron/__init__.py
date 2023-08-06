import os
import sys
import logging
import grpc
import json
import threading
import time
import getopt
import shlex

from typing import Tuple
from datetime import datetime

from crontab import CronTab
# from dotenv import dotenv_values
# from io import StringIO

from containerd.services.containers.v1 import containers_pb2_grpc, containers_pb2
from containerd.services.events.v1 import unwrap, events_pb2, events_pb2_grpc
from containerd.services.tasks.v1 import tasks_pb2, tasks_pb2_grpc

from apscheduler.schedulers.base import BaseScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger

SPECIALS = {"reboot":   '@reboot',
            "hourly":   '0 * * * *',
            "daily":    '0 0 * * *',
            "weekly":   '0 0 * * 0',
            "monthly":  '0 0 1 * *',
            "yearly":   '0 0 1 1 *',
            "annually": '0 0 1 1 *',
            "midnight": '0 0 * * *'}

METADATA = (('containerd-namespace', 'k8s.io'),)

FIFO_DIR = '/tmp/containerd-fifo'


def rmfifo(exec_id: str):
    fifo = FIFO_DIR + '/' + exec_id
    try:
        os.unlink(fifo)
    except:
        pass
    return fifo


def mkfifo(exec_id: str):
    fifo = rmfifo(exec_id)
    os.mkfifo(fifo)
    return fifo


class ReadTask(threading.Thread):
    abort_event: threading.Event
    output: bytearray
    exec_id: str
    fifo: str

    @staticmethod
    def target(self):
        with open(self.fifo, 'rb') as f:
            while not self.abort_event.is_set():
                self.output += f.read()
                time.sleep(0.1)

    def __init__(self, exec_id: str) -> None:
        self.abort_event = threading.Event()
        self.open_event = threading.Event()
        self.exec_id = exec_id
        self.fifo = mkfifo(exec_id)
        self.output = bytearray()
        super().__init__(target=ReadTask.target, args=(self,))

    def result(self) -> bytearray:
        self.abort_event.set()
        if self.is_alive():
            # make sure fifo was operated to avoid blocking behavior
            try:
                open(self.fifo, 'wb').close()
            except:
                pass
            self.join()
        rmfifo(self.exec_id)
        return self.output


def get_container_spec(channel: grpc.Channel, container_id: str):
    containers_stub = containers_pb2_grpc.ContainersStub(channel)
    container = containers_stub.Get(containers_pb2.GetContainerRequest(
        id=container_id), metadata=METADATA).container
    return json.loads(container.spec.value)


running_tasks = {}
running_tasks_lock = threading.RLock()


def create_task(channel: grpc.Channel, container_id: str, desc='*'):
    global running_tasks, running_tasks_lock

    task = ReadTask(exec_id="exec-" + os.urandom(16).hex())

    running_tasks_lock.acquire()
    now = datetime.timestamp(datetime.now())
    running_tasks[task.exec_id] = {
        'container_id': container_id, 'timeout': now + 300, 'desc': desc}
    running_tasks_lock.release()
    return task


def close_task(task: ReadTask):
    global running_tasks, running_tasks_lock
    running_tasks_lock.acquire()
    if task.exec_id in running_tasks:
        del running_tasks[task.exec_id]
    running_tasks_lock.release()


def cleanup_timeout_tasks(channel: grpc.Channel):
    global running_tasks, running_tasks_lock
    running_tasks_lock.acquire()
    # clean up timeout tasks
    now = datetime.timestamp(datetime.now())
    tasks_stub = tasks_pb2_grpc.TasksStub(channel)
    killed = 0
    for exec_id in list(running_tasks.keys()):
        task = running_tasks[exec_id]
        if task['timeout'] < now:
            logging.getLogger('cron').warn(
                "TIMEOUT {desc}".format(desc=task['desc']))
            try:
                tasks_stub.Kill(tasks_pb2.KillRequest(
                    container_id=task['container_id'], exec_id=exec_id),  metadata=METADATA)
            except:
                logging.getLogger('cron').error(
                    "KILL FAILED {desc}".format(desc=task['desc']))
            del running_tasks[exec_id]
            killed += 1
    remains = len(running_tasks)
    if killed > 0 or remains > 0:
        logging.getLogger('cron').warn(
            "{killed} killed, and {remains} remains".format(killed=killed, remains=remains))
    running_tasks_lock.release()


def run_command(channel: grpc.Channel, container_id: str, args, desc='*') -> Tuple[int, str]:

    cleanup_timeout_tasks(channel)

    container_spec = get_container_spec(channel, container_id)
    container_process = container_spec['process']

    process = {
        'args': args,
        'cwd': container_process['cwd'],
        'terminal': False,
        'env': container_process['env'],
        'user': container_process['user']
    }

    spec = {
        'type_url': 'types.containerd.io/opencontainers/runtime-spec/1/Spec',
        'value': json.dumps(process).encode('utf-8')
    }

    read_task = create_task(channel, container_id, desc)

    # remove previous conflict process
    try:
        tasks_stub = tasks_pb2_grpc.TasksStub(channel)
        tasks_stub.DeleteProcess(tasks_pb2.DeleteProcessRequest(
            container_id=container_id,
            exec_id=read_task.exec_id
        ), metadata=METADATA)
    except:
        pass

    try:
        tasks_stub = tasks_pb2_grpc.TasksStub(channel)
        tasks_stub.Exec(tasks_pb2.ExecProcessRequest(
            container_id=container_id,
            exec_id=read_task.exec_id,
            stdin=os.devnull, stdout=read_task.fifo, stderr=os.devnull,
            terminal=False,
            spec=spec
        ), metadata=METADATA)
        read_task.start()
        tasks_stub.Start(tasks_pb2.StartRequest(
            container_id=container_id, exec_id=read_task.exec_id), metadata=METADATA)
        exit_status = tasks_stub.Wait(tasks_pb2.WaitRequest(
            container_id=container_id, exec_id=read_task.exec_id),  metadata=METADATA).exit_status
    except:
        exit_status = 1

    result = read_task.result()
    close_task(read_task)
    return exit_status, result


def run_schedule(channel: grpc.Channel, container_id: str, args):
    schedule_id = os.urandom(4).hex()
    command = ' '.join(shlex.quote(arg) for arg in args)
    logging.getLogger('cron').info(
        "{schedule_id}: running {command}...".format(schedule_id=schedule_id, command=command))
    exit_code, _ = run_command(channel, container_id, args, desc=command)
    logging.getLogger('cron').info(
        "{schedule_id}: return {code}".format(schedule_id=schedule_id, code=exit_code))
    return exit_code


# def get_os_id(channel: grpc.Channel, container_id: str):
#     exit_code, output = run_command(
#         channel, container_id, ["cat", "/etc/os-release"])
#     if exit_code != 0:
#         return
#     release = dotenv_values(stream=StringIO(output.decode('utf8')))
#     return release['ID']


def get_current_user(channel: grpc.Channel, container_id: str) -> str:
    exit_code, output = run_command(
        channel, container_id, ['whoami'])
    if exit_code == 0:
        return output.decode('utf8').replace('\n', '')
    return 'root'


def get_user_crontab(channel: grpc.Channel, container_id: str, user: str) -> CronTab:
    exit_code, output = run_command(
        channel, container_id, ['cat', '/etc/crontabs/{user}'.format(user=user)])
    if exit_code != 0:
        return None
    tab = output.decode('utf8').replace('\t', ' ')
    return CronTab(tab=tab, user=user)


def get_system_crontab(channel: grpc.Channel, container_id: str) -> CronTab:
    exit_code, output = run_command(channel, container_id, ["/bin/sh", "-c",
                                                            '[ -d /etc/cron.d ] && find /etc/cron.d ! -name \".*\" -type f -exec cat \{\} \;'])
    if exit_code != 0:
        return None
    tab = output.decode('utf8').replace('\t', ' ')
    return CronTab(tab=tab, user=False)


def parse_args(command: str):
    return shlex.split(command)


def get_container_name(spec, default: str):
    if 'process' in spec:
        process = spec['process']
        if 'env' in process:
            hostname_var: str = next(
                filter(lambda v: v.startswith('HOSTNAME='), process['env']), None)
            if hostname_var:
                _, hostname = hostname_var.split('=', 2)
                if hostname:
                    return hostname
    if 'annotations' in spec:
        annotations = spec['annotations']
        if 'io.kubernetes.cri.container-name' in annotations:
            return annotations['io.kubernetes.cri.container-name']
    if 'hostname' in spec:
        return spec['hostname']
    if 'id' in spec:
        return spec['id']
    return default


def crontab_to_schedule(channel: grpc.Channel, container_id: str, crontab: CronTab, scheduler: BaseScheduler):
    logger = logging.getLogger('cron')
    added = 0
    for job in crontab:
        if not job.is_enabled():
            continue
        slices = str(job.slices)
        if slices.startswith('@'):
            slices = SPECIALS[slices.lstrip('@')]
        scheduler.add_job(run_schedule,
                          CronTrigger.from_crontab(slices),
                          args=[channel, container_id,
                                parse_args(job.command)],
                          name=job.command)
        logger.debug(
            'found {job}.'.format(job=job.command))
        added += 1
    return added


def load_container_schedules(channel: grpc.Channel, container_id: str, scheduler: BaseScheduler):
    logger = logging.getLogger('cron')
    container_spec = get_container_spec(channel, container_id)
    container_name = get_container_name(container_spec, container_id)

    added = 0
    user = get_current_user(channel, container_id)
    user_crontab = get_user_crontab(channel, container_id, user)
    if user_crontab:
        added += crontab_to_schedule(channel,
                                     container_id, user_crontab, scheduler)

    system_crontab = get_system_crontab(channel, container_id)
    if system_crontab:
        added += crontab_to_schedule(channel,
                                     container_id, filter(lambda it: it.user == user, system_crontab), scheduler)

    if added > 0:
        logger.info(
            'loaded {added} schedules from [{container_name}], {total} in total.'.format(
                added=added, container_name=container_name, total=len(scheduler.get_jobs())))


def unload_container_schedules(channel: grpc.Channel, container_id: str, scheduler: BaseScheduler):
    jobs = scheduler.get_jobs()
    job_count = len(jobs)
    for job in jobs:
        # 若存储器中的任务所属容器当前不存在，则在存储请中删除此任务
        if job.args[1] == container_id:
            scheduler.remove_job(job_id=job.id)
            job_count -= 1
    logging.getLogger('cron').info(
        'some schedules removed, {job_count} left.'.format(job_count=job_count))


def main():
    global METADATA, FIFO_DIR

    try:
        opts, _ = getopt.getopt(sys.argv[1:], 's:n:', [
            'cri-socket=', 'namespace=', 'fifo-dir='])
    except getopt.GetoptError as e:
        print('Usage: --cri-socket|-s <SOCKET> --namespace|-n <NAMESPACE>')
        exit(1)

    cri_socket = 'unix:///run/containerd/containerd.sock'
    namespace = 'k8s.io'  # moby for docker

    for k, v in opts:
        if k == '--cri-socket' or k == '-s':
            cri_socket = 'unix://' + v if v.startswith('/') else v
        elif k == '--namespace' or k == '-n':
            namespace = v
        elif k == '--fifo-dir':
            FIFO_DIR = v

    METADATA = (('containerd-namespace', namespace),)
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Shanghai')

    os.makedirs(FIFO_DIR, exist_ok=True)

    logging.basicConfig(stream=sys.stdout)
    logging.getLogger('apscheduler').setLevel(logging.ERROR)
    logging.getLogger('cron').setLevel(logging.INFO)

    scheduler = BackgroundScheduler(
        executors={'default': ThreadPoolExecutor(40)}, timezone=TIMEZONE)
    scheduler.start()

    with grpc.insecure_channel(cri_socket) as channel:
        tasks_stub = tasks_pb2_grpc.TasksStub(channel)
        tasks = tasks_stub.List(tasks_pb2.ListTasksRequest(
            filter='{.status=RUNNING}'), metadata=METADATA).tasks
        for task in tasks:
            load_container_schedules(channel, task.id, scheduler)

        events_stub = events_pb2_grpc.EventsStub(channel)
        for ev in events_stub.Subscribe(events_pb2.SubscribeRequest()):
            v = unwrap(ev)
            if ev.event.type_url == 'containerd.events.TaskCreate':
                load_container_schedules(channel, v.container_id, scheduler)
            elif ev.event.type_url == 'containerd.events.TaskDelete':
                unload_container_schedules(channel, v.container_id, scheduler)


if __name__ == "__main__":
    main()
