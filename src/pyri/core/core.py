import sys
from appdirs import AppDirs
import os.path
import argparse
from pathlib import Path
from ..parameters import YamlParameterBucket, ParameterBucketScope
import importlib.resources as resources

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
        self._http_port = None
        self._robotraconteur_port = None
        self._robotraconteur_node_name = None

        # The rest of the setup is done in start_core because async required
        
    async def start_core(self):
        pass

    async def stop_core(self):
        pass

    def run(self):
        pass

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