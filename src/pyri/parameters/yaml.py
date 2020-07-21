import yaml
import yamale
import yamale.readers
import yamale.schema
import yamale.validators
import yamale.validators.constraints
import importlib.resources as resources
import re
from typing import Union, List, Dict, Tuple, Any, NamedTuple
from itertools import chain
import re
import urllib.parse
from uuid import UUID
from packaging import version
import copy
import io
import threading
import re
import os.path

from .parameters import ParameterVisibility, ParameterAccess, ParameterBucket, \
     ParameterBucketInfo, ParameterGroup, ParameterGroupInfo, \
     ParameterInfo, ParameterBucketScope, ParameterTypes

_pkg_name = 'pyri.parameters'

class YamlGroupInfoWithSchema(NamedTuple):
    info: ParameterGroupInfo
    group_schema: yamale.schema.Schema
    parameters_schema: Dict[str,yamale.schema.Schema]

class YamlParameterBucket(ParameterBucket):
    def __init__(self, config: Union[io.IOBase, str, Tuple[ParameterBucketInfo,Dict[str,YamlGroupInfoWithSchema]]], data_dir: str, scope: ParameterBucketScope):
        super().__init__()

        self._lock = threading.RLock()

        if isinstance(config, tuple):
            self._info, self._group_info = config
        elif isinstance(config, io.IOBase):
            self._info, self._group_info = _load_bucket_info(config.read())
        elif isinstance(config, str):
            self._info, self._group_info = _load_bucket_info(config)
        else:
            raise ValueError("config is invalid type")

        self._groups = dict()

        for g in self._group_info.values():
            g_fp = open(os.path.join(data_dir, g.info.name + ".yml"), "a+")
            self._groups[g.info.name] = YamlParameterGroup(g, g_fp)

    def close(self):
        with self._lock:
            for g in self._groups:
                g.close()

    async def get_bucket_info(self) -> ParameterBucketInfo:
        with self._lock:
            return self._info

    async def get_groups_info(self) -> List[ParameterGroupInfo]:
        with self._lock:
            return [x.info for x in self._group_info.values()]

    async def get_group(self, name : str) -> ParameterGroup:
        with self._lock:
            return self._groups[name]

        

class YamlParameterGroup(ParameterGroup):
    def __init__(self, info: YamlGroupInfoWithSchema, fp: io.IOBase):
        super().__init__()

        self._lock = threading.RLock()
        self._info = info.info
        self._fp = fp
        self._group_schema = info.group_schema
        self._params_schema = info.parameters_schema

        self._params = dict()
        
        if not fp.readable() or not fp.writable() or not fp.readable():
            raise ValueError("fp must be readable, writable, and seekable")

        self._load_from_stream()
        
    def _load_from_stream(self):
        with self._lock:
            self._fp.seek(0)
            params = yaml.safe_load(self._fp)
            if params is None:
                params = dict()
            yamale.validate(self._group_schema, params)
            self._params = params

    def _save_to_stream(self):
        with self._lock:
            params2 = copy.deepcopy(self._params)
            self._group_schema.validate(params2,None,not self._info.allow_new_parameters)
            self._fp.seek(0)
            self._fp.truncate()
            yaml.dump(params2,self._fp)
            self._fp.truncate()

    def _find_param_info(self, name):
        param_info = [x for x in self._info.parameters if x.name == name]
        if len(param_info) == 0:
            return False, None
        else:
            return True, param_info[0]

    async def close(self):
        self._fp.close()
    
    async def get_name(self):
        return self._info.name

    async def get_group_info(self):
        return self._info

    async def get_param(self, name: str) -> ParameterTypes:
        with self._lock:
            if name not in self._params:
                if name in self._params_schema:
                    raise ValueError("Parameter {} has not been set".format(name))
                else:
                    raise KeyError("Invalid parameter name {}".format(name))
            return copy.deepcopy(self._params[name])
    
    async def try_get_param(self, name: str) -> Tuple[bool, ParameterTypes]:
        with self._lock:
            if name not in self._params:
                return False, None
            return True, copy.deepcopy(self._params[name])

    async def get_param_or_default(self, name: str, default_value: ParameterTypes = None) -> ParameterTypes:
        with self._lock:
            if name not in self._params:
                if default_value is None:
                    param_info_res, param_info = self._find_param_info(name)
                    if param_info_res:
                        return copy.deepcopy(param_info.default_value)
                    else:
                        return copy.deepcopy(default_value)
                else:
                    return copy.deepcopy(default_value)
            return copy.deepcopy(self._params[name])

    async def set_param(self, name: str, value: ParameterTypes) -> None:
        with self._lock:
            if name in self._params_schema:
                self._params_schema[name].validate(value,None,True)
                self._params[name] = copy.deepcopy(value)
                self._save_to_stream()
            else:
                raise ValueError("Invalid parameter name {}".format(name))

    
    async def set_or_add_param(self, name: str, value: ParameterTypes) -> None:
        with self._lock:
            if name in self._params_schema:
                yamale.validate(self._params_schema[name], value)
                self._params[name] = copy.deepcopy(value)
                self._save_to_stream()
            else:
                if self._info.allow_new_parameters:
                    if re.match(r"^(?:[a-zA-Z](?:\w*[a-zA-Z0-9])?)$", name) is None:
                        raise ValueError("Invalid parameter name".format(name))
                    self._params[name] = copy.deepcopy(value)
                    self._save_to_stream()
                else:
                    raise ValueError("Invalid parameter name {}".format(name))

    async def get_param_info(self, name: str) -> ParameterInfo:
        param_info_res, param_info = self._find_param_info(name)
        if not param_info_res:
            raise ValueError("Invalid parameter name: {}".format(name))
        return param_info

    async def get_param_item(self, name: str, index: Union[str,int]) -> ParameterTypes:
        with self._lock:
            if name not in self._params:
                if name in self._params_schema:
                    raise ValueError("Parameter {} has not been set".format(name))
                else:
                    raise KeyError("Invalid parameter name {}".format(name))            
            param = self._params[name]
            if isinstance(param,list):
                return copy.deepcopy(param[index])
            elif isinstance(param,dict):
                return copy.deepcopy(param[index])
            else:
                raise ValueError("Parameter is neither a list nor a dict")
            
    async def try_get_param_item(self, name: str, index: Union[str,int]) -> Tuple[bool, ParameterTypes]:
        with self._lock:
            if name not in self._params:
                return False, None
            param = self._params[name]
            if isinstance(param,list):
                try:
                    return True, copy.deepcopy(param[index])
                except:
                    return False, None
            elif isinstance(param,dict):
                try:
                    return True, copy.deepcopy(param[index])
                except:
                    return False, None
            else:
                False, None

    async def get_param_item_or_default(self, name: str, index: Union[str,int], default_value: ParameterTypes) -> ParameterTypes:
        with self._lock:
            if name not in self._params:
                param_info_res, param_info = self._find_param_info(name)
                if param_info_res:                   
                    if param_info.default_value is not None:
                        return copy.deepcopy(param_info.default_value)
                return copy.deepcopy(default_value)
            param = self._params[name]
            if isinstance(param,list):
                try:
                    return copy.deepcopy(param[index])
                except:
                    return copy.deepcopy(default_value)
            elif isinstance(param,dict):
                try:
                    return copy.deepcopy(param[index])
                except:
                    return copy.deepcopy(default_value)
            else:
                return copy.deepcopy(default_value)

    async def set_param_item(self, name: str, index: Union[str,int], value: ParameterTypes):
        with self._lock:
            is_list=False
            is_dict=False

            if name in self._params_schema:
                param_schema = self._params_schema[name]
                is_dict = isinstance(param_schema._schema,yamale.validators.Map)
                is_list = isinstance(param_schema._schema,yamale.validators.List)
            else:
                raise ValueError("Invalid parameter name {}".format(name))

            if is_dict:
                value_dict = {index, value}
                param_schema.validate(value_dict,None,True)
            elif is_list:
                value_list = [value]
                param_schema.validate(value_list,None,True)
            else:
                raise ValueError("Invalid parameter type for set_param_item")

            if name in self._params:
                param = self._params[name]
            else:
                if is_dict:
                    param_info_res, param_info = self._find_param_info(name)
                    if param_info_res and param_info.default_value is not None:
                        raise ValueError("Parameter has default value but is not set. Aborting set item")
                    param = dict()
                    self._params[name] = param
                elif is_list:
                    param_info_res, param_info = self._find_param_info(name)
                    if param_info_res and param_info.default_value is not None:
                        raise ValueError("Parameter has default value but is not set. Aborting set item")
                    param = []
                    self._params[name] = param
                else:
                    raise ValueError("Invalid parameter type for set_param_item")
            
            param[index] = copy.deepcopy(value)
            self._save_to_stream()                

    async def append_param_item(self, name: str, value: ParameterTypes):
        with self._lock:
            is_list=False
            
            if name in self._params_schema:
                param_schema = self._params_schema[name]
                is_list = isinstance(param_schema._schema,yamale.validators.List)
            else:
                raise ValueError("Invalid parameter name {}".format(name))

            if is_list:
                value_list = [value]
                param_schema.validate(value_list,None,True)
            else:
                raise ValueError("Invalid parameter type for set_param_item")

            if name in self._params:
                param = self._params[name]
            else:
                if is_list:
                    param_info_res, param_info = self._find_param_info(name)
                    if param_info_res and param_info.default_value is not None:
                        raise ValueError("Parameter has default value but is not set. Aborting append item")
                    param = []
                    self._params[name] = param
                else:
                    raise ValueError("Invalid parameter type for set_param_item")
            
            param.append(copy.deepcopy(value))
            self._save_to_stream()   

    async def del_param_item(self, name: str, index: Union[str,int]):
        with self._lock:

            # Test that schema validates before deleting
            test_value = copy.deepcopy(self._params[name])
            del test_value[index]
            self._group_schema.validate(self._params, None, not self._info.allow_new_parameters)

            del self._params[name][index]
            self._save_to_stream()

    async def get_param_item_count(self, name: str) -> int:
        with self._lock:
            return len(self._params[name])
    

class NameValidator(yamale.validators.Regex):
    tag = 'name'
    constraints = [yamale.validators.constraints.LengthMin, yamale.validators.constraints.LengthMax]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regexes = [re.compile(r"^(?:[a-zA-Z](?:\w*[a-zA-Z0-9])?)$")]

class QualifiedNameValidator(yamale.validators.Regex):
    tag = 'qualified_name'
    constraints = [yamale.validators.constraints.LengthMin, yamale.validators.constraints.LengthMax]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regexes = [re.compile(r"^(?:[a-zA-Z](?:\w*[a-zA-Z0-9])?)(?:\.(?:[a-zA-Z](?:\w*[a-zA-Z0-9])?))*$")]

class UuidValidator(yamale.validators.Regex):
    tag = 'uuid'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regexes = [re.compile(r'^(?:(?:\{([a-fA-F0-9]{8})-?([a-fA-F0-9]{4})-?([a-fA-F0-9]{4})-?([a-fA-F0-9]{4})-?([a-fA-F0-9]{12})\})|(?:([a-fA-F0-9]{8})-?([a-fA-F0-9]{4})-?([a-fA-F0-9]{4})-?([a-fA-F0-9]{4})-?([a-fA-F0-9]{12})))$')]

class VersionValidator(yamale.validators.Regex):
    tag = 'version'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regexes = [re.compile(r'^\d+\.\d+(?:\.\d+)?$')]

class UrlValidator(yamale.validators.Validator):
    tag = 'url'

    
    def _uri_validator(self,x):
        # based on https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
        try:
            result = urllib.parse.urlparse(x)
            if all([result.scheme, result.netloc, result.path]):
                return True
            # Relative URL
            return all([not result.scheme, not result.netloc, result.path])

        except:
            return False

    def _is_valid(self, value):
        return self._uri_validator(value)


_validators = yamale.validators.DefaultValidators
_validators[NameValidator.tag] = NameValidator
_validators[QualifiedNameValidator.tag] = QualifiedNameValidator
_validators[UuidValidator.tag] = UuidValidator
_validators[VersionValidator.tag] = VersionValidator
_validators[UrlValidator.tag] = UrlValidator



_group_info_schema: yamale.schema.Schema = None
_bucket_info_schema: yamale.schema.Schema = None

def _load_group_info_schema():
    global _group_info_schema
    group_info_schema_str = resources.read_text(_pkg_name, "parameter_group_info_schema.yml")
    raw_schemas = yamale.readers.parse_yaml(content = group_info_schema_str)
    assert raw_schemas is not None
    group_schema = raw_schemas[0]['parameter_group_info_schema']
    s = yamale.schema.Schema(group_schema, name='parameter_group_info_schema', validators=_validators)
    for raw_schema in raw_schemas[1:]:
        s.add_include(copy.deepcopy(raw_schema))
    _group_info_schema = s
    
def _load_bucket_info_schema():
    global _bucket_info_schema
    bucket_info_schema_str = resources.read_text(_pkg_name, "parameter_bucket_info_schema.yml")
    raw_schemas = yamale.readers.parse_yaml(content = bucket_info_schema_str)
    group_info_schema_str = resources.read_text(_pkg_name, "parameter_group_info_schema.yml")
    raw_schemas2 = yamale.readers.parse_yaml(content = group_info_schema_str)
    s = yamale.schema.Schema(raw_schemas[0], name="parameter_bucket_info_schema", validators=_validators)
    for raw_schema in chain(raw_schemas[1:],raw_schemas2):
        s.add_include(raw_schema)
    _bucket_info_schema = s


def _load_group_info(yaml_info_str: str) -> YamlGroupInfoWithSchema:
    
    group_info_data = yamale.readers.parse_yaml(content = yaml_info_str)
    group_info_data0 = group_info_data
    if isinstance(group_info_data,list):
        group_info_data0 = group_info_data[0]
    yamale.validate(_group_info_schema, [(group_info_data0,None)])

    info = _load_group_info_tuple(group_info_data0)

    parameters_schema = dict()
    parameter_group_raw_schema = dict()

    for p in group_info_data0["parameters"]:
        p_name = p["name"]
        p_raw_schema = p["type_schema"]

        s = yamale.schema.Schema(p_raw_schema, name="paramater_info_schema_{}".format(p_name), validators=_validators)
        for raw_schema in group_info_data[1:]:
            s.add_include(copy.deepcopy(raw_schema))

        parameter_group_raw_schema[p_name] = p_raw_schema
        parameters_schema[p_name] = s

    parameter_group_schema = yamale.schema.Schema(parameter_group_raw_schema, name="parameter_group_schema_{}".format(info.name), validators=_validators)
    for v in parameter_group_schema._schema.values():
        v.is_required=False
    for raw_schema in group_info_data[1:]:
            parameter_group_schema.add_include(copy.deepcopy(raw_schema))

    return YamlGroupInfoWithSchema(info, parameter_group_schema, parameters_schema)

def _load_group_info_tuple(yaml_info_dict: Dict[str,Any]):

    def _p(n, f=None, g=None):
        return _load_optional(yaml_info_dict, n, f, g)

    name = yaml_info_dict["name"]
    uuid =_p("uuid", UUID)
    version_ = _p("version", version.parse)
    description = yaml_info_dict["description"]
    long_description = _p("long_description")
    help_url = _p("help_url")
    tags = _p("tags", _load_tags)
    visibility = _p("visibility", _load_visilibility_enum, ParameterVisibility.DEFAULT)
    access = _p("access", _load_access_enum, ParameterAccess.DEFAULT)
    allow_new_parameters = _p("allow_new_parameters", bool, False)

    parameters = []
    
    parameters_info_list = yaml_info_dict["parameters"]
    if len(parameters_info_list) == 0:
        raise ValueError("Parameter group parameter list must not be empty")

    for parameter_info_dict in parameters_info_list:
        def _p2(n, f=None, g=None):
            return _load_optional(parameter_info_dict, n, f, g)
        parameter_name = parameter_info_dict["name"]

        if any([parameter_name == x.name for x in parameters]):
            raise ValueError("parameter name {} is not unique".format(parameter_name))

        parameter_description = parameter_info_dict["description"]
        parameter_long_description = _p2("long_description")
        parameter_help_url = _p2("help_url")
        parameter_tags = _p2("tags", _load_tags)
        parameter_visibility = _p2("visibility", _load_visilibility_enum, ParameterVisibility.DEFAULT)
        parameter_access = _p2("access", _load_access_enum, ParameterAccess.DEFAULT)
        parameter_secret = _p2("secret", bool, False)
        parameter_type_schema = parameter_info_dict["type_schema"]
        parameter_default_value = _p2("default_value")

        parameter_info = ParameterInfo(parameter_name, parameter_description, 
            parameter_long_description, parameter_help_url,
            parameter_tags, parameter_visibility,
            parameter_access, parameter_secret, 
            parameter_type_schema, parameter_default_value)

        parameters.append(parameter_info)

    group_info = ParameterGroupInfo(name=name, uuid=uuid, version=version_,
        description=description, long_description=long_description,
        help_url=help_url, tags=tags, visibility=visibility,
        access=access, allow_new_parameters=allow_new_parameters,
        parameters=parameters)

    return group_info

def _load_bucket_info(yaml_info_str, load_groups=True) -> Tuple[ParameterBucketInfo,Dict[str,YamlGroupInfoWithSchema]]:
    bucket_info_data = yamale.readers.parse_yaml(content = yaml_info_str)
    bucket_info_data0 = bucket_info_data
    if isinstance(bucket_info_data,list):
        bucket_info_data0 = bucket_info_data[0]
    yamale.validate(_bucket_info_schema, [(bucket_info_data0,None)])

    group_infos = dict()
    group_names = []

    for g in bucket_info_data0["groups"]:
        group_info_resource_name = g["resource_name"]
        if "resource_pkg" in g:
            group_info_pkg_name = g["resource_pkg"]
            group_info_yml_str = resources.read_text(group_info_pkg_name, group_info_resource_name)
            group_info = _load_group_info(group_info_yml_str)
            group_infos[group_info[0].name] = group_info
            group_names.append(group_info[0].name)

    info = _load_bucket_info_tuple(bucket_info_data0, group_names)

    return info, group_infos

def _load_bucket_info_tuple(yaml_info_dict: [Dict[str,any]], group_names: List[str]):
    def _p(n, f=None, g=None):
        return _load_optional(yaml_info_dict, n, f, g)

    name = yaml_info_dict["name"]
    scope = _load_scope_enum(yaml_info_dict["scope"])
    uuid =_p("uuid", UUID)
    version_ = _p("version", version.parse)
    description = yaml_info_dict["description"]
    long_description = _p("long_description")
    help_url = _p("help_url")
    tags = _p("tags", _load_tags)

    bucket_info = ParameterBucketInfo(name, scope, uuid, version, description, \
        long_description, help_url, tags, group_names)

    return bucket_info

    

def _load_optional(d, n, f=None, g=None):
    if not n in d:
        return g
    v = d[n]
    if isinstance(v,bool):
        return v
    if isinstance(v,int):
        return v
    if isinstance(v,str):
        return v
    if v is None or len(v) == 0:
        return g
    if f is None:
        return v
    return f(v)

_visibility_enum_str_dict = {"hidden": ParameterVisibility.HIDDEN, "advanced": ParameterVisibility.ADVANCED, \
    "normal": ParameterVisibility.NORMAL, "default": ParameterVisibility.DEFAULT}

def _load_visilibility_enum(val_str: str):
    enum_val = _visibility_enum_str_dict.get(val_str, None)
    if enum_val is None:
        raise ValueError("Invalid parameter visibility option: {}".format(val_str))
    return enum_val

_access_enum_str_dict = {"readonly": ParameterAccess.READONLY, "protected": ParameterAccess.PROTECTED, \
    "all": ParameterAccess.ALL, "default": ParameterAccess.DEFAULT}    

def _load_access_enum(val_str: str):
    enum_val = _access_enum_str_dict.get(val_str, None)
    if enum_val is None:
        raise ValueError("Invalid parameter access option: {}".format(val_str))
    return enum_val

def _load_tags(tags: Union[str,List[str]]):
    if isinstance(tags,str):
        return [tags]
    elif isinstance(tags,list):
        return tags
    else:
        raise ValueError("Invalid paramater tags")

def _default_parameter_value_from_schema(param_schema: yamale.schema.Schema):
    if isinstance(param_schema._schema,yamale.validators.String):
        return ""
    elif isinstance(param_schema._schema,yamale.validators.Integer):
        return 0
    elif isinstance(param_schema._schema,yamale.validators.List):
        return []
    elif isinstance(param_schema._schema,yamale.validators.Map):
        return dict()
    else:
        return None

_scope_enum_str_dict = {"core": ParameterBucketScope.CORE, "plugin": ParameterBucketScope.PLUGIN, \
    "user_program": ParameterBucketScope.USER_PROGRAM}

def _load_scope_enum(val_str: str):
    enum_val = _scope_enum_str_dict.get(val_str, None)
    if enum_val is None:
        raise ValueError("Invalid parameter bucket scope option: {}".format(val_str))
    return enum_val

_load_group_info_schema()
_load_bucket_info_schema()