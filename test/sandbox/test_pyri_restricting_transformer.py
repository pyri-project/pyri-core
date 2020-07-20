import pytest
from pyri.sandbox.restricting_transformer import PyriRestrictingNodeTransformer

from RestrictedPython import safe_builtins, compile_restricted

def run_transformer(script_src):    
    reserved_names = ["reserved1", "reserved2"]
    byte_code = compile_restricted(script_src, filename='<pyri module>', mode='exec', policy=PyriRestrictingNodeTransformer)
    #exec(byte_code, {'__builtins__': safe_builtins}, None)

def test_Name():
    src1 = ("def myfunc():\n"
            "   a=10\n"
            "   b=100\n")

    run_transformer(src1)

    src2 = ("def _myfunc():\n"
            "    pass")

    with pytest.raises(SyntaxError):
        run_transformer(src2)

    src3 = ("def myfunc_():\n"
            "    pass")

    with pytest.raises(SyntaxError):
        run_transformer(src3)

def test_MatMult():
    src = ("b = 1\n"
           "c = 2\n"
           "a = b @ c")
    run_transformer(src)

def test_Call():    
    src1 = ("myfunc(*args)")
    with pytest.raises(SyntaxError):
        run_transformer(src1)

    src2 = ("myfunc(**kwargs)")
    with pytest.raises(SyntaxError):
        run_transformer(src2)

    src3 = ("__begin_blockly_statement('9472o92')\n__end_blockly_statement('9472o92')")
    run_transformer(src3)

    src4 = ("__not_special_function()")
    with pytest.raises(SyntaxError):
        run_transformer(src4)

    src5 = ("eval('malicious_function()'")
    with pytest.raises(SyntaxError):
        run_transformer(src5)
    
    src6 = ("exec(malicious_bytecode)")
    with pytest.raises(SyntaxError):
        run_transformer(src6)

"""def test_Assign():
    src1 = ("a = 10\na, b = 10, 20")
    run_transformer(src1)

    src2 = "a = reserved_name1\nreserved_name2()"
    run_transformer(src2)

    src3 = "reserved_name1 = 10"
    with pytest.raises(SyntaxError):
        run_transformer(src3)"""