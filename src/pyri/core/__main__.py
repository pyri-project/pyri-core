import argparse
from ctypes import ArgumentError
import asyncio
import yaml
from typing import NamedTuple, List
from enum import Enum
import threading
import traceback
import appdirs
from pathlib import Path
import sys
from datetime import datetime
import os
import time
import signal
from . import subprocess_impl
from pyri.util.wait_exit import wait_exit
from pyri.plugins.service_node_launch import get_all_service_node_launches
from pyri.device_manager_client import _DeviceManagerConnectFilter
from RobotRaconteur.Client import *
from RobotRaconteurCompanion.Util.IdentifierUtil import IdentifierUtil

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
# service_node_launch = [
#     ServiceNodeLaunch("variable_storage", "pyri.variable_storage",["--db-file=test3.db"],[]),
#     ServiceNodeLaunch("device_manager","pyri.device_manager",[],["variable_storage"]),
#     ServiceNodeLaunch("devices_states","pyri.devices_states",[],["device_manager"]),
#     ServiceNodeLaunch("sandbox","pyri.sandbox", [],["device_manager"]),
#     ServiceNodeLaunch("program_master","pyri.program_master",[],["device_manager"]),
#     ServiceNodeLaunch("robotics_jog","pyri.robotics.robotics_jog_service",[],["device_manager"]),
#     ServiceNodeLaunch("robotics_motion","pyri.robotics.robotics_motion_service",[],["device_manager"]),
#     ServiceNodeLaunch("webui_server","pyri.webui_server", ["--device-manager-url=rr+tcp://{{ HOSTNAME }}:59902?service=device_manager"],["device_manager"])
# ]

class PyriProcess:
    def __init__(self, parent, service_node_launch, parser_results, log_dir, loop):
        self.parent = parent
        self.service_node_launch = service_node_launch
        self.parser_results = parser_results
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
                    args = s.prepare_service_args(self.parser_results)
                    python_exe = sys.executable
                    self._process = await subprocess_impl.create_subprocess_exec(python_exe,(["-m", s.module_main] + args))
                    # print(f"process pid: {self._process.pid}")
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
                self._process = None
                if not s.restart:
                    break
                if self._keep_going:
                    await asyncio.sleep(s.restart_backoff)

    @property
    def process_state(self):
        pass

    @property
    def stopped(self):
        return self._process == None

    def close(self):
        self._keep_going = False
        if self._process:
            self._process.send_term()
    
    def kill(self):
        p = self._process
        if p is None:
            return
        try:
            self._process.kill()
        except:
            traceback.print_exc()

class PyriCore:
    def __init__(self, device_info, service_node_launches, parser_results, log_dir, loop):
        self.device_info = device_info
        self.service_node_launches = dict()
        self._closed = False
        for s in service_node_launches:
            self.service_node_launches[s.name] = s
        self.log_dir = log_dir
        self._loop = loop
        self._parser_results = parser_results

        self._subprocesses = dict()
        self._lock = threading.RLock()

    def _do_start(self,s):
        p = PyriProcess(self, s, self._parser_results, self.log_dir, self._loop)
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
                with self._lock:
                    if process_name in self._subprocesses:
                        del self._subprocesses[process_name]

    def check_deps_status(self, deps):
        return True

    def close(self):
        with self._lock:
            if self._closed:
                return
            self._closed = True

            for p in self._subprocesses.values():
                try:
                    p.close()
                except Exception:
                    traceback.print_exc()
                    pass

        self._wait_all_closed()
    
    def _wait_all_closed(self):
        try:
            t1 = time.time()
            t_last_sent_close = 0
            while True:
                t_diff = time.time() - t1
                if t_diff > 15:
                    break
                running_count = 0
                with self._lock:
                    for p in self._subprocesses.values():
                        if not p.stopped:
                            running_count += 1
                if running_count == 0:
                    break
                time.sleep(0.1)
                if t_diff > t_last_sent_close + 1:
                    t_last_sent_close = t_diff
                    with self._lock:
                        for p in self._subprocesses.values():
                            if not p.stopped:
                                try:
                                    p.close()
                                except Exception:
                                    traceback.print_exc()
                                    pass
            
            running_count = 0
            with self._lock:
                for p in self._subprocesses.values():
                    if not p.stopped:
                        running_count += 1
                        try:
                            p.kill()
                        except Exception:
                            traceback.print_exc()
                        
            if running_count != 0:
                print("Sending processes still running SIGKILL")                
                time.sleep(2)               

            self._loop.stop()
        except:
            traceback.print_exc()

    def add_default_devices(self, delay_seconds=5):
        self._loop.create_task(self._do_add_default_devices(delay_seconds))
    
    async def _do_add_default_devices(self, delay_seconds):

        default_devices = []
        for l in self.service_node_launches.values():
            if l.default_devices is not None and len(l.default_devices) > 0:
                default_devices.extend(l.default_devices)
        if len(default_devices) == 0:
            return

        filter = _DeviceManagerConnectFilter(RRN, "pyri_device_manager")
        device_manager_sub = RRN.SubscribeServiceByType("tech.pyri.device_manager.DeviceManager", filter.get_filter())
        if delay_seconds > 0:            
            await asyncio.sleep(delay_seconds)

        a, f = await self._do_add_default_devices2(default_devices, device_manager_sub)

        while f is None or len(f) > 0:
            print("Retrying add default devices...")
            await asyncio.sleep(5)
            a, f = await self._do_add_default_devices2(default_devices, device_manager_sub)

    async def _do_add_default_devices2(self, default_devices, device_manager_sub):

        res, c = device_manager_sub.TryGetDefaultClient()
        if not res:
            print("Warning: could not connect to device manager to add default devices")
            return None, None

        active_devices = await c.async_getf_active_devices(None)
        active_device_names = [a.local_device_name for a in active_devices]

        ident_util = IdentifierUtil(client_obj = c)

        added_devices = []
        failed_devices = []

        for d in default_devices:
            try:
                if d[1] not in active_device_names:
                    d_ident = ident_util.CreateIdentifierFromName(d[0])
                    await c.async_add_device(d_ident,d[1],[],None)
                    added_devices.append(d[1])
            except Exception as e:
                print(f"Warning: could not add default device {d[1]}: {str(e)}")
                failed_devices.append(d[1])
        if len(added_devices) > 0:
            print(f"Added default devices: {added_devices}")

        return added_devices, failed_devices

def main():
    try:
        
        service_node_launch_dict = get_all_service_node_launches()
        service_node_launch = []
        for l in service_node_launch_dict.values():
            service_node_launch.extend(l)
        parser = argparse.ArgumentParser("PyRI Core Launcher")
        parser.add_argument("--no-add-default-devices",action='store_true',default=False,help="Don't add default devices")
        for l in service_node_launch:
            if l.add_arg_parser_options is not None:
                l.add_arg_parser_options(parser)

        parser_results, _ = parser.parse_known_args()

        timestamp = datetime.now().strftime("pyri-core-%Y-%m-%d--%H-%M-%S")
        log_dir = Path(appdirs.user_log_dir(appname="pyri-project")).joinpath(timestamp)
        log_dir.mkdir(parents=True, exist_ok=True)
        def loop_in_thread(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()
            print("Exited loop!")
        loop = asyncio.new_event_loop()
        t = threading.Thread(target=loop_in_thread, args=(loop,), daemon=True)
        t.start()
                
        core = PyriCore(None, service_node_launch, parser_results, log_dir, loop)
        loop.call_soon_threadsafe(lambda: core.start_all())
        if not parser_results.no_add_default_devices:
            loop.call_soon_threadsafe(lambda: core.add_default_devices())
        def ctrl_c_pressed(signum, frame):
            loop.call_soon_threadsafe(lambda: core.close())
        signal.signal(signal.SIGINT, ctrl_c_pressed)
        signal.signal(signal.SIGTERM, ctrl_c_pressed)
        #loop.run_forever()
        wait_exit()
        core.close()
        
        print("Done")
    except Exception:
        traceback.print_exc()
    


if __name__ == "__main__":
    main()