import sys
from appdirs import AppDirs
import os.path
import argparse
from pathlib import Path
from ..parameters import YamlParameterBucket, ParameterBucketScope
import importlib.resources as resources
import asyncio
import sanic

_pkg_name = 'pyri.core'

class PyriCore():
    def __init__(self, config_dir = None):
        if config_dir is None:
            self._config_dir = _get_default_config_dir()
        else:
            self._config_dir = config_dir

        self._core_config_dir = self._config_dir.joinpath("core")
        self._core_config_dir.mkdir(parents=True, exist_ok=True)
        bucket_info = resources.read_text(_pkg_name,"core_parameter_bucket.yml")
        self._param_bucket = YamlParameterBucket(bucket_info, str(self._core_config_dir), ParameterBucketScope.CORE)
        self._core_params = None
        self._start_http_ = False
        self._http_port = None
        self._robotraconteur_port = None
        self._robotraconteur_node_name = None
        self._sanic = None
        self._sanic_server = None

        # The rest of the setup is done in start_core because async required

        self._loop = asyncio.get_event_loop()
        
    async def start_core(self):
        self._core_params = await self._param_bucket.get_group("core")
        self._start_http_ = await self._core_params.get_param_or_default("http_start")
        if self._start_http_:
            self._http_port = await self._core_params.get_param_or_default("http_port")
        self._robotraconteur_port = await self._core_params.get_param_or_default("robotraconteur_port")
        self._robotraconteur_nodename = await self._core_params.get_param_or_default("robotraconteur_nodename")

        await self._start_robotraconteur()
        await self._start_http()
        
        
    async def _start_http(self):
        if not self._start_http_:
            return

        self._sanic = sanic.Sanic(__name__)
        serv_coro = self._sanic.create_server(host="0.0.0.0", port = self._http_port, return_asyncio_server=True)
        serv_task = asyncio.ensure_future(serv_coro, loop=self._loop)
        self._sanic_server = await serv_task
        self._sanic_server.after_start()
        self._sanic.add_route(self.http_route_root, "/")

    async def _start_robotraconteur(self):
        pass

    async def stop_core(self):
        pass

    async def http_route_root(self,request):
        return sanic.response.text("Hello World!")

    def run(self):
        self._loop.run_until_complete(self.start_core())
        self._loop.run_forever()

def _get_default_config_dir():
    dirs = AppDirs("pyri", "pyri_project")
    config_dir = Path(dirs.user_data_dir).joinpath("config")
    return config_dir


def main():

    parser = argparse.ArgumentParser(description="Pyri Teach Pendant Core Runtime")
    parser.add_argument("--config-dir", type=str, default=None, help="configuration directory")

    args = parser.parse_args()
    pyri_core = PyriCore(args.config_dir)
    pyri_core.run()