
import pytest
import importlib.resources as resources
import guards_data
from pyri.sandbox.pyri_sandbox import PrintCollector
from pyri.sandbox.restricting_transformer import PyriRestrictingNodeTransformer
from pyri.sandbox import guards
from RestrictedPython import compile_restricted

_policy = PyriRestrictingNodeTransformer

def _get_test_module(module_name, sandbox_globals = None, print_collector = None):

    if sandbox_globals is None:
        sandbox_builtins = guards.get_pyri_builtins_with_name_guard()
        sandbox_globals = {'__builtins__': sandbox_builtins}

    if print_collector is None:
        print_collector = PrintCollector()

    sandbox_globals["_print_"] = print_collector

    module_src = resources.read_text(guards_data, module_name)
    byte_code = compile_restricted(module_src, '<robotraconteur_sandbox>', 'exec', policy = _policy)

    loc = dict()
    exec(byte_code, sandbox_globals, loc)

    return loc

def test_constants():
    mod = _get_test_module("constants.py.test")
    mod["test_constants"]()

def test_types():
    mod = _get_test_module("types.py.test")
    mod["test_bool"]()
    mod["test_int"]()
    mod["test_float"]()
    mod["test_complex"]()

    mod["test_str"]()
    mod["test_bytearray"]()

    mod["test_list"]()
    mod["test_set"]()
    mod["test_dict"]()
    mod["test_tuple"]()

"""def test_abs():
    mod = _get_test_module()
    mod['test_abs']()

def test_open():
    mod = _get_test_module()
    with pytest.raises(NameError):
        mod['test_open']()"""