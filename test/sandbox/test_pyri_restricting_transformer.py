import pytest
from pyri.sandbox.restricting_transformer import PyriRestrictingNodeTransformer

from RestrictedPython import compile_restricted

import importlib.resources as resources

import restricted_transformer_data
import ast
from astdiff import astdiff
import astor

# Check that the node transformer policy is working as expected
# Assume that the transformer provided by RestrictedPython is working properly

def run_transformer(script_src):    
    byte_code = compile_restricted(script_src, filename='<pyri module>', mode='exec', policy=PyriRestrictingNodeTransformer)
    

def make_function(py_src):
    f = "def myfunc():\n"

    return f + '\n'.join(["    " + x for x in py_src.split("\n")])

def check_transformer_output(src_fname):
    src = resources.read_text(restricted_transformer_data, src_fname)
    expected_src = resources.read_text(restricted_transformer_data, src_fname + ".res")

    c_ast = ast.parse(src, "<file>", "exec")

    collected_errors = []

    policy = PyriRestrictingNodeTransformer

    policy_instance = policy(collected_errors)
    policy_instance.visit(c_ast)
    if (len(collected_errors) > 0):
        print (collected_errors)
        raise Exception("Got errors")

    run_transformer(src)

    expected_c_ast = ast.parse(expected_src, "<file>", "exec")

    # Run c_ast through the decompiler to have matching formats
    c_ast2 = ast.parse(astor.to_source(c_ast),"<file 2>", "exec")
    
    astdiff.compare_ast(c_ast2,expected_c_ast)
    
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

def test_Starred():

    src1 = ("myfunc(*args)")
    with pytest.raises(SyntaxError):
        run_transformer(make_function(src1))

    src2 = ("myfunc(**kwargs)")
    with pytest.raises(SyntaxError):
        run_transformer(make_function(src2))

    src3 = ("def myfunc(*args):\n    pass")
    with pytest.raises(SyntaxError):
        run_transformer(src3)

    src4 = ("def myfunc(**kwargs):\n    pass")
    with pytest.raises(SyntaxError):
        run_transformer(src4)

    src5 = ("def myfunc():\n"
            "    def myinnerfunc():\n"
            "        pass")
    with pytest.raises(SyntaxError):
        run_transformer(src5)

def test_UnaryOp():
    check_transformer_output("unary_op.py.test")

def test_BinOp():
    check_transformer_output("bin_op.py.test")

def test_Compare():
    check_transformer_output("compare_op.py.test")

def test_MatMult():
    src = ("b = 1\n"
           "c = 2\n"
           "a = b @ c")
    run_transformer(make_function(src))

def test_Call():    
    src1 = ("myfunc(*args)")
    with pytest.raises(SyntaxError):
        run_transformer(make_function(src1))

    src2 = ("myfunc(**kwargs)")
    with pytest.raises(SyntaxError):
        run_transformer(make_function(src2))

    src3 = ("_begin_blockly_statement_('9472o92')\n_end_blockly_statement_('9472o92')")
    run_transformer(make_function(src3))

    src4 = ("_not_special_function()")
    with pytest.raises(SyntaxError):
        run_transformer(make_function(src4))

    src5 = ("eval('malicious_function()'")
    with pytest.raises(SyntaxError):
        run_transformer(make_function(src5))
    
    src6 = ("exec(malicious_bytecode)")
    with pytest.raises(SyntaxError):
        run_transformer(make_function(src6))

    check_transformer_output("call.py.test")

def test_Attributes():
    check_transformer_output("attribute.py.test")

def test_Subscript():
    check_transformer_output("subscript.py.test")

def test_ListComp():
    src1 = ("a = [x + 1 for x in [10,20]]")
    with pytest.raises(SyntaxError):
        run_transformer(make_function(src1))

def test_SetComp():    
    src1 = ("a = {x + 1 for x in [10,20]}")
    with pytest.raises(SyntaxError):
        run_transformer(make_function(src1))

def test_GeneratorExp():
    src1 = ("a = (x + 1 for x in [10,20])")
    with pytest.raises(SyntaxError):
        run_transformer(make_function(src1))

def test_DictComp():
    src1 = ("a = {k:x + 1 for (k,x) in {'a': 10, 'b': 20} }")
    with pytest.raises(SyntaxError):
        run_transformer(make_function(src1))

def test_Assign():
    src1 = ("a = 10\na, b = 10, 20\na, (b,c) = (10, (20,30))")
    run_transformer(make_function(src1))

    src2 = ("_a = 10")
    with pytest.raises(SyntaxError):
        run_transformer(make_function(src2))

    src3 = ("_a, _b = 10, 20")
    with pytest.raises(SyntaxError):
        run_transformer(make_function(src3))

    src4 = ("_a, (_b, _c) = (10, (20, 30))")
    with pytest.raises(SyntaxError):
        run_transformer(make_function(src4))

    src5 = ("a = b = 10")
    with pytest.raises(SyntaxError):
        run_transformer(make_function(src5))

    check_transformer_output("assign.py.test")

def test_AugAssign():

    def f(src):
        with pytest.raises(SyntaxError):
            run_transformer(make_function(src))    

    f("a += 1")
    f("a -= 1")
    f("a *= 1")
    f("a /= 1")
    f("a %= 1")
    f("a **= 1")
    f("a >>= 1")
    f("a <<= 1")
    f("a &= 1")
    f("a ^= 1")
    f("a |= 1")
    
def test_Delete():
    def f(src):
        with pytest.raises(SyntaxError):
            run_transformer(make_function(src))  

    f("del a")
    f("del a,b")
    f("del a.a, a.b")

    run_transformer(make_function("del a.a"))
    run_transformer(make_function("del a[10]"))
    run_transformer(make_function("del a.a[10]"))

    check_transformer_output("delete.py.test")

def test_For():
    check_transformer_output("for.py.test")

def test_Try():
    check_transformer_output("try.py.test")

def test_With():
    check_transformer_output("with.py.test")

def test_FunctionDef():

    def f(src):
        with pytest.raises(SyntaxError):
            run_transformer(src)

    f("def myfunc():\n def myfunc1():\n  pass")
    f("def myfunc(a,*b):\n pass")
    f("def myfunc(a,*b,c):\n pass")
    f("def myfunc(a,*b,**c):\n pass")
    f("def myfunc(a,**b):\n pass")
    f("def myfunc(a,*b):\n pass")
    f("def myfunc(a,*,b=1):\n pass")

def test_Lambda():

    src1 = ("def myfunc():\n a = lambda x: x+1")
    with pytest.raises(SyntaxError):
        run_transformer(src1)

def test_Yield():

    src1 = ("def myfunc():\n a = yield 1")
    with pytest.raises(SyntaxError):
        run_transformer(src1)

def test_YieldFrom():

    src1 = ("def myfunc():\n a = yield from b")
    with pytest.raises(SyntaxError):
        run_transformer(src1)

def test_Global():

    src1 = ("def myfunc():\n global b")
    with pytest.raises(SyntaxError):
        run_transformer(src1)

def test_Classdef():
    src1 = ("def myfunc():\n class B:\n  pass")
    with pytest.raises(SyntaxError):
        run_transformer(src1)

def test_NamedExpr():
    src1 = "def myfunc():\n if a := b():\n  pass"
    with pytest.raises(SyntaxError):
        run_transformer(src1)

def test_Module():
    def f(src):
        with pytest.raises(SyntaxError):
            run_transformer(src)

    # Check that top level statements are not allowed
    f("a = 1")
    f("a()")
    f("if a == b:\n pass")