from .factory import PyriPluginFactory
from ..parameters import YamlParameterBucket
from importlib.metadata import entry_points
import traceback
from typing import List, Tuple, Dict
from pathlib import Path

def find_plugin_factories(blacklist: str = None) -> List[PyriPluginFactory]:
    all_eps = entry_points()
    if "pyri.plugins.factory" not in all_eps:
        return []

    factories = []
    eps = all_eps["pyri.plugins.factory"]
    for ep in eps:
        ep_func = ep.load()
        try:
            factory = ep_func()
        except:
            # TODO: Log the plugin error
            traceback.print_exc()
        else:
            factories.append(factory)

    return factories


def find_plugin_wheel_files(factories: List[PyriPluginFactory]) -> List[Tuple[Path,dict]]:
    pass

def load_parameter_buckets(factories: List[PyriPluginFactory]) -> List[YamlParameterBucket]:
    pass
