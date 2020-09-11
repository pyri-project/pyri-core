from pyri.sandbox.restricting_transformer import PyriRestrictingNodeTransformer
import os
import ast
import sys
import astor
import pathlib

fname = sys.argv[1]

with open(fname, "r") as f:
    py_src = f.read()

c_ast = ast.parse(py_src, "<file>", "exec")

collected_errors = []

policy = PyriRestrictingNodeTransformer

policy_instance = policy(collected_errors)
policy_instance.visit(c_ast)
if (len(collected_errors) > 0):
    print (collected_errors)
    raise Exception("Got errors")

with open(fname + ".res","w") as f:
    f.write(astor.to_source(c_ast))

