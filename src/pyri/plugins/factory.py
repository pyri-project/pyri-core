from typing import List, Dict, Tuple, Callable, Any, NamedTuple, TYPE_CHECKING
from pathlib import Path
from .types import PyriPluginInfo

if TYPE_CHECKING:
    from ..core import PyriCore

class PyriPluginFactory:
    def __init__(self):
        super().__init__()

    def get_info(self) -> PyriPluginInfo:
        pass

    def get_core_plugins(self) -> List[Tuple[Callable[['PyriCore'],None],Dict]]:
        pass

    def get_webui_wheels(self) -> Dict[str,Tuple[Path,dict]]:
        return []

    def get_parameter_buckets(self) -> Dict[str,Tuple[str,dict]]:
        return {}

    def get_blockly_blocks(self) -> Dict[str,Tuple[str,dict]]:
        return {}

    def get_pyri_procs(self) -> Dict[str,Tuple[str,dict]]:
        return {}

    def get_pyri_funcs(self) -> Dict[str,Tuple[str,dict]]:
        return {}

    def get_pyri_object_factories(self) -> Dict[str,Tuple[Any,dict]]:
        return {}

    def get_pyri_structure_types(self) -> Dict[str,Tuple[Any,dict]]:
        return {}