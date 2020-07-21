import re
from typing import Union, List, NamedTuple, Any, Tuple
from enum import Enum
from uuid import UUID
from packaging.version import Version

ParameterTypes = Union[int, float, str, list, dict]

class ParameterVisibility(Enum):
    HIDDEN = 1
    ADVANCED = 2
    NORMAL = 3
    DEFAULT = 3

class ParameterAccess(Enum):
    READONLY = 1
    PROTECTED = 2
    ALL = 3
    DEFAULT = 3

class ParameterBucketScope(Enum):
    CORE = 1
    PLUGIN = 2
    USER_PROGRAM = 3

class ParameterBucketInfo(NamedTuple):
    name: str
    scope: ParameterBucketScope
    uuid: UUID
    version: Version
    description: str
    long_description: str
    help_url: str
    tags: List[str]
    group_names: List[str]

class ParameterInfo(NamedTuple):
    name: str
    decription: str
    long_description: str
    help_url: str
    tags: List[str]
    visibility: ParameterVisibility
    access: ParameterAccess
    secret: bool
    type_schema: Any
    default_value: Any

class ParameterGroupInfo(NamedTuple):
    name: str
    uuid: UUID
    version: Version
    description: str
    long_description: str
    help_url: str
    tags: List[str]
    visibility: ParameterVisibility
    access: ParameterAccess
    allow_new_parameters: bool
    parameters: List[ParameterInfo]
    
class ParameterGroup:

    async def get_name(self) -> str:
        raise NotImplementedError()

    async def get_group_info(self) -> str:
        raise NotImplementedError()

    async def get_param(self, name: str) -> ParameterTypes:
        raise NotImplementedError()

    async def try_get_param(self, name: str) -> Tuple[bool, ParameterTypes]:
        raise NotImplementedError()

    async def get_param_or_default(self, name: str, default: ParameterTypes) -> ParameterTypes:
        raise NotImplementedError()

    async def set_param(self, name: str, param: ParameterTypes) -> None:
        raise NotImplementedError()
    
    async def set_or_add_param(self, name: str, param: ParameterTypes) -> None:
        raise NotImplementedError()

    async def get_param_info(self, name: str) -> ParameterInfo:
        raise NotImplementedError()

    async def get_param_item(self, name: str,index: Union[str,int]) -> ParameterTypes:
        raise NotImplementedError()

    async def try_get_param_item(self, name: str, index: Union[str,int]) -> Tuple[bool, ParameterTypes]:
        raise NotImplementedError()

    async def get_param_item_or_default(self, name: str, index: Union[str,int], default: ParameterTypes) -> ParameterTypes:
        raise NotImplementedError()

    async def set_param_item(self, name: str, index: Union[str,int], value: ParameterTypes):
        raise NotImplementedError()

    async def append_param_item(self, name: str, value: ParameterTypes):
        raise NotImplementedError()

    async def del_param_item(self, name: str, index: Union[str,int]):
        raise NotImplementedError()

    async def get_param_item_count(self, name: str) -> int:
        raise NotImplementedError()

class ParameterBucket:

    async def get_bucket_info(self) -> ParameterBucketInfo:
        raise NotImplementedError()

    async def get_groups_info(self) -> List[ParameterGroupInfo]:
        raise NotImplementedError()

    async def get_group(self, name : str) -> ParameterGroup:
        raise NotImplementedError()

