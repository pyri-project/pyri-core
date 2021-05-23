from ctypes import ArgumentError
import asyncio
import yaml
from typing import NamedTuple, List
from enum import Enum
import threading
import traceback
import appdirs
from pathlib import Path
import uuid
import sys
from datetime import datetime

from pyri.util.subprocess_management import get_subprocess_watch_dir

class ServiceNodeLaunch(NamedTuple):
    name: str
    module_main: str
    args: List[str]
    depends: List[str]
    depends_backoff: float = 1
    restart: bool = False
    restart_backoff: float = 5

# Based on MS Windows service states
class ProcessState(Enum):
    STOPPED = 0x1
    START_PENDING = 0x2
    STOP_PENDING = 0x3
    RUNNING = 0x4
    CONTINUE_PENDING = 0x5
    PAUSE_PENDING = 0x6
    PAUSED = 0x7

#TODO: Don't hard code services to start
service_node_launch = [
    ServiceNodeLaunch("variable_storage", "pyri.variable_storage",["--db-file=test3.db", ],[]),
    ServiceNodeLaunch("device_manager","pyri.device_manager",[],["variable_storage"]),
    ServiceNodeLaunch("devices_states","pyri.devices_states",[],["device_manager"]),
    ServiceNodeLaunch("sandbox","pyri.sandbox", [],["device_manager"]),
    ServiceNodeLaunch("program_master","pyri.program_master",[],["device_manager"]),
    ServiceNodeLaunch("robotics_jog","pyri.robotics.robotics_jog_service",[],["device_manager"]),
    ServiceNodeLaunch("robotics_motion","pyri.robotics.robotics_motion_service",[],["device_manager"]),
    ServiceNodeLaunch("webui_server","pyri.webui_server", ["--device-manager-url=rr+tcp://{{ HOSTNAME }}:59902?service=device_manager"],["device_manager"])
]


class PyriProcess:
    def __init__(self, parent, service_node_launch, subprocess_dir, log_dir, loop):
        self.parent = parent
        self.service_node_launch = service_node_launch
        self.subprocess_dir = subprocess_dir
        self.log_dir = log_dir
        self.loop = loop
        self._keep_going = True
        self._process = None
    
    async def run(self):
        s = self.service_node_launch
        stdout_log_fname = self.log_dir.joinpath(f"{s.name}.txt")
        stderr_log_fname = self.log_dir.joinpath(f"{s.name}.stderr.txt")
        with open(stdout_log_fname,"w") as stdout_log, open(stderr_log_fname,"w") as stderr_log:
            while self._keep_going:
                try:
                    self.parent.process_state_changed(s.name,ProcessState.START_PENDING)
                    stderr_log.write(f"Starting process {s.name}...\n")
                    self._process = await asyncio.create_subprocess_exec(sys.executable,*(["-m", s.module_main] + s.args),stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
                    stderr_log.write(f"Process {s.name} started\n\n")                   
                    self.parent.process_state_changed(s.name,ProcessState.RUNNING)
                    stdout_read_task = asyncio.ensure_future(self._process.stdout.readline())
                    stderr_read_task = asyncio.ensure_future(self._process.stderr.readline())
                    while self._keep_going:
                        wait_tasks = list(filter(lambda x: x is not None, [stdout_read_task, stderr_read_task]))
                        if len(wait_tasks) == 0:
                            break
                        done, pending = await asyncio.wait(wait_tasks,return_when=asyncio.FIRST_COMPLETED)
                        if stderr_read_task in done:
                            stderr_line = await stderr_read_task
                            if len(stderr_line) == 0:
                                stderr_read_task = None
                            else:
                                stderr_log.write(stderr_line.decode("utf-8")) 
                                stderr_log.flush()
                                stderr_read_task = asyncio.ensure_future(self._process.stderr.readline())
                        if stdout_read_task in done:
                            stdout_line = await stdout_read_task
                            if len(stdout_line) == 0:
                                stdout_read_task = None
                            else:
                                stdout_log.write(stdout_line.decode("utf-8"))
                                stdout_log.flush()
                                stdout_read_task = asyncio.ensure_future(self._process.stdout.readline())
                    await self._process.wait()
                    self.parent.process_state_changed(s.name,ProcessState.STOPPED)
                except:
                    self._process = None
                    self.parent.process_state_changed(s.name,ProcessState.STOPPED)
                    traceback.print_exc()
                    stderr_log.write(f"\nProcess {s.name} error:\n")
                    stderr_log.write(traceback.format_exc())
                if not s.restart:
                    break
                if self._keep_going:
                    await asyncio.sleep(s.restart_backoff)

    @property
    def process_state(self):
        pass

    def close(self):
        self._keep_going = False

class PyriCore:
    def __init__(self, device_info, service_node_launches, subprocess_dir, log_dir, loop):
        self.device_info = device_info
        self.service_node_launches = dict()
        self._closed = False
        for s in service_node_launches:
            self.service_node_launches[s.name] = s
        self.subprocess_dir = subprocess_dir
        self.log_dir = log_dir
        self._loop = loop        

        self._subprocesses = dict()
        self._lock = threading.Lock()

    def _do_start(self,s):
        p = PyriProcess(self, s, self.subprocess_dir, self.log_dir, self._loop)
        self._subprocesses[s.name] = p
        self._loop.create_task(p.run())

    def start_all(self):
        with self._lock:
            for name,s in self.service_node_launches.items():
                if name not in self._subprocesses:
                    self._do_start(s)

    def start(self, name):
        with self._lock:
            if self._closed:
                assert False, "Already closed"
            try:
                s = self.service_node_launches[name]
            except KeyError:
                raise ArgumentError(f"Invalid service requested: {name}")
            if name not in self._subprocesses:
                self._do_start(s)

    def process_state_changed(self, process_name, state):
        print(f"Process changed {process_name} {state}")
        if self._closed:
            if state == ProcessState.STOPPED:
                if process_name in self._subprocesses:
                    del self._subprocesses[process_name]
            if len(self._subprocesses) == 0:
                self._loop.stop()

    def check_deps_status(self, deps):
        return True

    def close(self):
        with self._lock:
            self._closed = True

            for p in self._subprocesses.values():
                try:
                    p.close()
                except Exception:
                    traceback.print_exc()
                    pass


def main():
    try:
        timestamp = datetime.now().strftime("pyri-core-%Y-%m-%d--%H-%M-%S")
        log_dir = Path(appdirs.user_log_dir(appname="pyri-project")).joinpath(timestamp)
        log_dir.mkdir(parents=True, exist_ok=True)
        subprocess_dir = get_subprocess_watch_dir()
        subprocess_dir.mkdir(parents=True, exist_ok=True)
        loop = asyncio.get_event_loop()
        core = PyriCore(None, service_node_launch, subprocess_dir, log_dir, loop)
        core.start_all()
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    try:
        print("Shutting down...")
        core.close()
        loop.run_forever()
    except Exception:
        traceback.print_exc()
    


if __name__ == "__main__":
    main()