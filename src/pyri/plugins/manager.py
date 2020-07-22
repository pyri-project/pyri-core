from ..parameters import ParameterBucket
from . import loader
from typing import Dict, List, TYPE_CHECKING
from .loader import find_plugin_factories
import threading
from .types import PyriPluginInfo

if TYPE_CHECKING:
    from ..core import PyriCore

class PyriPluginManager:

    def __init__(self, core: "PyriCore"):
        self._core = core
        self._factories = None
        self._lock = threading.RLock()

    async def get_plugin_parameter_buckets(self) -> Dict[str,ParameterBucket]:
        pass

    async def get_webui_wheel_names(self) -> List[str]:
        pass

    async def get_webui_wheel(self,name: str) -> bytearray:
        pass

    async def load_plugins(self, blacklist: List[str] = None):
        with self._lock:
            self._factories = find_plugin_factories(blacklist)

            #TODO: Load in plugin functions

            for f in self._factories:
                print("Found factory: {}".format(f.get_info().name))

    async def get_plugins_info(self) -> List[PyriPluginInfo]:
        with self._lock:
            if self._factories is None:
                return []

            return [p.get_info() for p in self._factories]
    