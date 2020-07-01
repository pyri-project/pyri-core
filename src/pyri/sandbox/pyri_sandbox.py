

import re
from RestrictedPython import compile_restricted, safe_globals

_valid_name_re = re.compile('[a-zA-Z][a-zA-Z0-9_]*')

class PrintCollector:
    def __init__(self):
        self.printed = ""
    
    def __call__(self, _gettattr_=None):
        return self

    def write(self, text):
        self.printed += text

    def _call_print(self, text):
        self.printed += text


class PyriSandbox():
    def run_sandbox(self, script_src, function_name, params):
        if _valid_name_re.match(function_name) is None:
            raise RR.InvalidArgumentException("Function name is invalid")
        if params is not None:
            for k in params:
                if _valid_name_re.match(params) is None:
                    raise RR.InvalidArgumentException("Param name is invalid")
        
        loc = {}
        
        byte_code = compile_restricted(script_src, '<robotraconteur_sandbox>', 'exec')
        sandbox_globals = safe_globals.copy()
        print_collector = PrintCollector()
        sandbox_globals["_print_"] =print_collector
        exec(byte_code, sandbox_globals, loc)
        if params is None:
            res = loc[function_name]()
        else:
            res = loc[function_name](*params)

        print(print_collector.printed)