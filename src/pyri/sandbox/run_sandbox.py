import argparse

from .pyri_sandbox import PyriSandbox

def main():

    parser = argparse.ArgumentParser(description='Run script function in restricted Python sandbox')
    parser.add_argument('--file', type=argparse.FileType('r'), required=True, help="script file")
    parser.add_argument('--function', type=str, required=True, help="function name")

    parse_res = parser.parse_args()

    function_name = parse_res.function
    with parse_res.file:
        script_src = parse_res.file.read()

    restricted_py = PyriSandbox()
    restricted_py.run_sandbox(script_src, function_name, None)

if __name__ == "__main__":
    main()
