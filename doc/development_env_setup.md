# Development Workspace Configuration

## Preparation

### Windows

Begin by downloading and installing the latest Python version from: https://www.python.org/downloads/ PyRI requires Python 3.8 or greater.

Download and install Git from https://git-scm.com/download/win


Download and install  NodeJS LTS and NPM from https://nodejs.org/en/download/ This is necessary for the Blockly compiler.

Download and install Visual Studio 2019 Community https://visualstudio.microsoft.com/downloads/ Make sure to select the C++ and Python workload https://docs.microsoft.com/en-us/cpp/build/vscpp-step-0-installation?view=msvc-160

### Linux

Ubuntu 20.04 or greater required. Run the following:

    sudo apt install python3-pip python3-venv libboost-all-dev curl git

Install the Node.js version 14.x

    curl -fsSL https://deb.nodesource.com/setup_14.x | sudo -E bash -
    sudo apt-get install -y nodejs

## Prepare Workspace

```
c:\python39\python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip

python -m pip install vcstool
vcs import --input https://raw.githubusercontent.com/pyri-project/pyri-core/master/pyri.repos

python -m pip install -e pyri-cli -e pyri-common

python -m pip install requests
python pyri-webui-resources\tools\install_npm_deps.py
python pyri-webui-resources\tools\install_pyodide.py

pyri-cli dev --dev-install-runtime --dev-install-webui

```

The `pyri-webui-resources` scripts only need to be run once, unless the contents of the resource package is updated.

Because an editable install is used, any changes to the runtime packages will be immediately applied. If changes
to `pypackage.toml` or `setup.py` are made, it is necessary to run `pyri-cli --dev-install-runtime` again. For the
WebUI packages, it is necessary to rerun `pyri-cli --dev-install-webui` to pack the wheels for the browser when
the packages are modified.

## Run PyRI

To run PyRI, use:

```
pyri-core --db-file=my_project.db
```

Each service can be started individually for debugging purposes.

## Debugging with VS Code

PyRI can be debugged with VS Code. Be sure to select the Python interpreter in `venv\Scripts\python` using the `Select Python Interpreter` task https://code.visualstudio.com/docs/python/environments Use the `launch.json` file in the `scripts` directory to configure the launch profiles for the PyRI service nodes.

## Updating

To update PyRI, change to the project root directory and run:

```
vcs pull
pyri-cli dev --dev-install-runtime --dev-install-webui
```
