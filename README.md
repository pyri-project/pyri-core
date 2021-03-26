# PyRI Open Source Teach Pendant Core Module

**WARNING: THIS REPOSITORY CONTAINS UNFINISHED SOFTWARE**

## Development Workspace Configuration

### Windows

#### Preparation

Begin by downloading and installing the latest Python version from: https://www.python.org/downloads/ PyRI requires Python 3.8 or greater.

Download and install Git from https://git-scm.com/download/win

Next, install vstools by running the following command:

    python -m pip install vcstools

It may be necessary to run this command using an administrative command prompt https://www.isunshare.com/windows-10/2-ways-to-run-command-prompt-as-administrator-in-win-10.html

Download and install  NodeJS LTS and NPM from https://nodejs.org/en/download/ This is necessary for the Blockly compiler.

Download and install Visual Studio 2019 Community https://visualstudio.microsoft.com/downloads/ Make sure to select the C++ and Python workload https://docs.microsoft.com/en-us/cpp/build/vscpp-step-0-installation?view=msvc-160

Install the Windows Terminal https://docs.microsoft.com/en-us/windows/terminal/get-started

#### Clone and initialize

Create a new directory to hold the files. Change to that directory in a command prompt, and run:

    vcs import --input https://raw.githubusercontent.com/pyri-project/pyri-core/master/pyri.repos
    cd scripts
    create_python_venv
    init_workspace_packages

#### Run PyRI and initialize default devices

Create a terminal, and change to the `scripts` directory. Run to start all services in tabs in the terminal:

    run_all

Add default devices. This only has to be done once:

    add_default_devices

Now, open firefox and go to http://localhost:8000 The PyRI WebUI will start.

#### Run PyRI

To run PyRI, change to the `scripts` directory and run `run_all`. Navigate to http://localhost:8000 with firefox

#### Debugging with VS Code

PyRI can be debugged with VS Code. Be sure to select the Python interpreter in `venv\Scripts\python` using the `Select Python Interpreter` task https://code.visualstudio.com/docs/python/environments Use the `launch.json` file in the `scripts` directory to configure the launch profiles for the PyRI service nodes.

## PyRI Components

PyRI currently consists of the following components:

* `pyri-common`: https://github.com/pyri-project/pyri-common
* `pyri-variable-storage`: https://github.com/pyri-project/pyri-variable-storage
* `pyri-device-manager`: https://github.com/pyri-project/pyri-device-manager
* `pyri-sandbox`: https://github.com/pyri-project/pyri-sandbox
* `pyri-webui-server`: https://github.com/pyri-project/pyri-webui-server
* `pyri-core`: https://github.com/pyri-project/pyri-core
* `pyri-robotics`: https://github.com/pyri-project/pyri-robotics

Additional developer tools:

* `pyri-example-plugin`: https://github.com/pyri-project/pyri-example-plugin
* `pyri-scripts`: https://github.com/johnwason/pyri-scripts (development scripts and examples to trial components)

To clone all repositories for PyRI using vcstool run:

    vcs import --input https://raw.githubusercontent.com/pyri-project/pyri-core/master/pyri.repos

## Plugin Architecture

PyRI uses setuptools `entry_points` to add plugins. See https://packaging.python.org/guides/creating-and-discovering-plugins/#using-package-metadata for an overview of how `entry_points` can be used to create and discover plugins.

PyRI plugin `entry_points` functions return "plugin factory" objects. These objects return the individual components that are made available by the plugins. The factories can be found in `pyri-common`, in the `pyri.plugins` package. The following `entry_points` are currently defined:

| Entry Point | Factory Type | Description |
| ---         | ---          | ---         |
| `pyri.plugins.robdef` | `pyri.plugins.robdef.PyriRobDefPluginFactory` | Additional Robot Raconteur robdef service types |
| `pyri.plugins.sandbox_functions` | `pyri.plugins.sandbox_functions.PyriSandboxFunctionsPluginFactory` | Functions to make available in the PyRI sandbox |
| `pyri.plugins.blockly` | `pyri.plugins.blockly.PyriBlocklyPluginFactory` | Custom blocks and generators to add to the blockly workspace |
| `pyri.plugins.webui_server` | `pyri.plugins.webui_server.PyriWebUIServerPluginFactory` | WebUI server routes and data to serve to the teach pendant browser user interface |

## Python VirtualEnv

It is recommended that a Python virtual environment be used for development. See https://docs.python.org/3/tutorial/venv.html for more information on creating a virtual environment. A parent directory should be created, and in that directory, all modules should be checked out and a `venv` directory created for the virtual environment using:

```
python3 -m venv venv
```

Next, go into each package directory, and execute:

```
python3 -m pip install -e .
```
This command will create an "editable install" in the virtual environment. The package will behave like a normal Python package, but will point to the current source code rather than copying the source into the venv package directory. See https://the-hitchhikers-guide-to-packaging.readthedocs.io/en/latest/pip.html#installing-from-a-vcs for more information.

