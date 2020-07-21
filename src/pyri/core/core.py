import sys
from appdirs import AppDirs
import os.path

class PyriCore():
    def __init__(self, config_dir = None):
        if config_dir is None:
            self._config_dir = _get_default_config_dir()
        else:
            self._config_dir = config_dir


    


    def run(self):
        pass

def _get_default_config_dir():
    dirs = AppDirs("pyri", "pyri_project")
    config_dir = os.path.join(dirs.user_data_dir, "config")
    return config_dir