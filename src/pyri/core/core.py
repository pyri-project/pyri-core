import sys
from appdirs import AppDirs
import os.path
import argparse
from pathlib import Path
from ..parameters import YamlParameterBucket, ParameterBucketScope
import importlib.resources as resources
import asyncio
import sanic
import RobotRaconteur as RR
import importlib.resources
from RobotRaconteurCompanion.Util import RobDef as rr_util
from ..plugins.manager import PyriPluginManager

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
        self._robotraconteur_nodename = None
        self._sanic = None
        self._sanic_server = None
        self._robotraconteur_node = None
        self._robotraconteur_node_setup = None
        self._robotraconteur_core = None
        self._plugin_manager = None

        # The rest of the setup is done in start_core because async required

        self._loop = asyncio.get_event_loop()
        
    async def start_core(self):
        self._core_params = await self._param_bucket.get_group("core")
        self._start_http_ = await self._core_params.get_param_or_default("http_start")
        if self._start_http_:
            self._http_port = await self._core_params.get_param_or_default("http_port")
        self._robotraconteur_port = await self._core_params.get_param_or_default("robotraconteur_port")
        self._robotraconteur_nodename = await self._core_params.get_param_or_default("robotraconteur_nodename")
        self._plugin_blacklist = await self._core_params.get_param_or_default("plugin_blacklist", [])

        await self._load_plugins()

        await self._start_robotraconteur()
        await self._start_http()
        
        
    async def _load_plugins(self):
        self._plugin_manager = PyriPluginManager(self)        
        await self._plugin_manager.load_plugins(self._plugin_blacklist)

        #TODO: remove print
        plugins_info = await self._plugin_manager.get_plugins_info()
        print(plugins_info)

    async def _start_http(self):
        if not self._start_http_:
            return

        self._sanic = sanic.Sanic(__name__)
        serv_coro = self._sanic.create_server(host="0.0.0.0", port = self._http_port, return_asyncio_server=True)
        serv_task = asyncio.ensure_future(serv_coro, loop=self._loop)
        self._sanic_server = await serv_task
        self._sanic_server.after_start()
        from .. import webui
        with importlib.resources.path(webui,"static") as webui_static_dir:
            self._sanic.static("/", str(webui_static_dir))
            self._sanic.static("/", os.path.join(str(webui_static_dir),"index.html"))


    async def _start_robotraconteur(self):
        
        from .rr import RRPyriCore

        self._robotraconteur_node = RR.RobotRaconteurNode.s
        #self._robotraconteur_node.Init()

        rr_util.register_standard_robdef(self._robotraconteur_node)
        
        from .. import core as core_pkg

        rr_util.register_service_types_from_resources(
            self._robotraconteur_node,
            [
                (core_pkg,"tech.pyri.core")
            ]
        )

        self._robotraconteur_node_setup = RR.ServerNodeSetup(self._robotraconteur_nodename, 
            self._robotraconteur_port, self._robotraconteur_node)

        self._robotraconteur_core = RRPyriCore(self)
        
        self._robotraconteur_node.RegisterService("pyri", "tech.pyri.core.PyriCore", self._robotraconteur_core)
        

    async def stop_core(self):
        pass

    def run(self):
        self._loop.run_until_complete(self.start_core())
        self._loop.run_forever()

    def get_sanic(self):
        return self._sanic

    def get_robotraconteur(self):
        return self._robotraconteur_node

    def http_add_route(self, *args, **kwargs):
        return self._sanic.add_route(*args, **kwargs)

    def http_add_static(self, *args, **kwargs):
        return self._sanic.static(*args, **kwargs)

    def get_loop(self):
        return self._loop

def _get_default_config_dir():
    dirs = AppDirs("pyri", "pyri-project")
    config_dir = Path(dirs.user_data_dir).joinpath("config")
    return config_dir


def main():

    parser = argparse.ArgumentParser(description="Pyri Teach Pendant Core Runtime")
    parser.add_argument("--config-dir", type=str, default=None, help="configuration directory")
    parser.add_argument("--wait-debugger", action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args()

    if args.wait_debugger:
        print("PyRI PID: {}".format(os.getpid()))
        input("Press enter to continue")

    pyri_core = PyriCore(args.config_dir)
    pyri_core.run()