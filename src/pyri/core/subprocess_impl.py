from ctypes.wintypes import WIN32_FIND_DATAW
import sys
import asyncio


if sys.platform == "win32":
    from . import subprocess_impl_win32


async def create_subprocess_exec(process, args, env=None):
    if sys.platform == "win32":
        job_handle = subprocess_impl_win32.win32_create_job_object()

        process = await asyncio.create_subprocess_exec(process,*args, \
            stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE,\
            env=env, creationflags=subprocess_impl_win32.CREATE_SUSPENDED,close_fds=True)

        subprocess_impl_win32.win32_attach_job_and_resume_process(process, job_handle)

        return PyriSubprocessImpl(process,job_handle)

    else:
        #TODO: Use "start_new_session=True" arg for new process
        raise NotImplementedError()


class PyriSubprocessImpl:
    def __init__(self, asyncio_subprocess, job_handle = None):
        self._process = asyncio_subprocess
        self._job_handle = job_handle
        # TODO: Linux

    @property
    def process(self):
        return self._process

    @property
    def stdout(self):
        return self._process.stdout

    @property
    def stderr(self):
        return self._process.stderr

    @property
    def pid(self):
        return self._process.pid

    def wait(self):
        return self._process.wait()

    def send_term(self):
        if sys.platform == "win32":
            subprocess_impl_win32.win32_send_job_wm_close(self._job_handle)

    def close(self):
        if sys.platform == "win32":            
            subprocess_impl_win32.win32_close_job_object(self._job_handle)