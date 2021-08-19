# PyRI Extension Development

PyRI is a modular software system, designed to be easily extensible. See [software_architecture.md](software_architecture.md) for a detailed overview of the teach pendant architecture. Familiarity of the software architecture is required for the rest of this document.

Extensions are distributed as Python packages. These packages can contain plugins, using `entry_points` in `setup.py`, and/or additional services that run in their own process, and can be launched using `pyri-core`. Extension packages can also be added to the WebUI, to add additional panels. These packages are
stored in a special directory for the WebUI Server.

In most cases, an extension will only need to add "sandbox functions" and corresponding Blockly blocks. These plugins will allow user procedures to call these new functions.

All extension packages require a properly formatted `setup.py` file. See https://packaging.python.org/tutorials/packaging-projects/ . The `entry_points` field in the `setup.py` file is used to discover plugins. See https://packaging.python.org/guides/creating-and-discovering-plugins/ . When developing packages, they must be installed for the `entry_points` to work properly. The best method to install packages under development is to use a `pip` "editable" install. See https://brandonrozek.com/blog/pipeditable/ .

It is highly recommended that Conda be used for development. Install `pyri-robotics-superpack` package, and use `pip install -e path/to/my/package` to install a symlink for your package to the conda environment. See https://github.com/pyri-project/pyri-core/blob/master/README.md#conda-install for conda install instructions.

## Example Extension Packages

Three packages will be used as examples:

| Package | Repository | Description |
| ---     | ---        | ---         |
| pyri-example-plugin | https://github.com/pyri-project/pyri-example-plugin | Example package with "sandbox function" and "Blockly" plugin |
| pyri-robotics | https://github.com/pyri-project/pyri-robotics | Package that adds support for robots to the teach pendant |
| pyri-tesseract-planning | https://github.com/pyri-project/pyri-tesseract-planning | Package that adds support for the Tesseract motion planner |

## Runtime and WebUI shared plugins

The Runtime and WebUI can use the same plugin, but due to the limited ability to load non-pure Python dependencies on the Pyodide interpreter, it is recommended that plugin packages be targeted at only the Runtime or WebUI.

## Runtime Plugins

The Runtime consists of the following Robot Raconteur nodes:

* **Variable Storage** - Stores all data relating to the current program, including global variables, procedures, active device information, etc.
* **Device Manager** - Detects available devices on the network, manages devices selected by the program, and provides connection information. The `DeviceManagerClient` package provides automatic connections to devices.
* **Devices States** - Connects to all devices, and aggregates state information. Clients can request the aggregated state with an update rate of 10 Hz
* **Sandbox** - Executes user programs written in Blockly or PyRI
* **WebUI Server** - Provides a server to initialize and run the WebUI
* **Program Master** - Top level program state machine

Plugins can be developed to extend the functionality of some of the runtime nodes.

### Devices States

PyRI by default does not understand how to read the state or information of devices. Plugins must be provided that convert the type specific state information into a format that the devices states node can understand. This is accomplished using a "device type adapter" plugin. The plugin provides `PyriDeviceTypeAdapter` instances that convert the feedback type of the device into the common `PyriDeviceTypeAdapterExtendedState` state feedback type. The definitions for these types are:

```
class PyriDeviceTypeAdapterExtendedState(NamedTuple):
    robotraconteur_type: str
    display_flags: List[str]
    state_data: Any
    ready: bool
    error: bool
    state_seqno: int


class PyriDeviceTypeAdapter:
    def __init__(self, device_subscription, node):
        pass

    def get_robotraconteur_type(self) -> str:
        pass

    async def get_extended_device_infos(self, timeout = 0) -> Dict[str,"RobotRaconteur.VarValue"]:
        pass

    async def get_extended_device_states(self, timeout = 0) -> Dict[str,PyriDeviceTypeAdapterExtendedState]:
        pass
```

The `get_extended_device_infos` method should return any device information structures that are type specific without modifying them. The `get_extended_device_states` should populate the `PyriDeviceTypeAdapterExtendedState` structure based on the latest data. This is typically accomplished by subscribing to the device's state wire, and then populating the `PyriDeviceTypeAdapterExtendedState` based on the latest `InValue`. The factory for the devices states plugin has the following definition:

```
class PyriDeviceTypeAdapterPluginFactory:

    def get_plugin_name(self) -> str:
        return ""

    def get_robotraconteur_types(self) -> List[str]:
        return []

    def create_device_type_adapter(self, robotraconteur_type: str, client_subscription: Any, node) -> PyriDeviceTypeAdapter:
        return None
```

The entry point `pyri.plugins.device_type_adapter` is used for this plugin type.

An example of the device type adapter plugin used by the `pyri-robotics` package is here: https://github.com/pyri-project/pyri-robotics/blob/master/src/pyri/robotics/device_type_adapter.py . The plugin `entry_points` specification can be found here: https://github.com/pyri-project/pyri-robotics/blob/9adbf3f7ba807b827ecab0e78bc6923cfbee6b39/setup.py#L30 .

### Sandbox Plugins

The sandbox plugins allow for the addition of functions that are made available to the sandbox environment, and custom Blockly blocks that are presented to the user. The sandbox must be restarted if the plugins are modified.

#### Sandbox Functions Plugin

Sandbox functions are injected into the sandbox runtime environment, so that user procedures can execute them. They run outside of the sandbox, and have pull access to the sandbox node. The sandbox is considered to be ephemeral, meaning that it may be destroyed and restarted between procedures. This allows for the plugins and other parts of the sandbox to be refreshed without needing to restart the rest of the system nodes. Because of this behavior, the plugins must not assume that any global data will remain between the execution of procedures. Any persistent data must be stored in the Variable Storage node.

Sandbox functions are provided state information, access to the Robot Raconteur node, access to the device manager client, and a "print" function that is shown to the user through the `PyriSandboxContext` object. This object is thread-static. It has the following definition:

```
class PyriSandboxContext(threading.local):
    node : RobotRaconteurNode
    device_manager : DeviceManagerClient
    print_func : Callable[str]
    action_runner : PyriSandboxActionRunner
    context_vars : Dict[str,Any]
    proc_result : str
```

Sandbox functions are standard Python functions. These functions are designed to be called from the PyRI restricted python sandbox, but run in a standard Python context. Sandbox functions can perform computations and return a result, set the procedure result, print to the output window, modify `context_vars`, or communicate with outside devices/services. Most of these scenarios require using `PyriSandboxContext`. The `device_manager` field is used to access the `DeviceManagerClient`, which automatically connects to all devices. Use this to communicate with other devices in the system. The `print_func` will print to the output window. `context_vars` is a dict of values that is scoped to the current procedure. These values will be retained until the procedure exits, and are used to track things like the currently selected robot. The `action_runner` is used to run asynchronous operations. This is used for Robot Raconteur generator functions that are used for long running actions, like a robot motion. See https://github.com/pyri-project/pyri-robotics/blob/9adbf3f7ba807b827ecab0e78bc6923cfbee6b39/src/pyri/robotics/sandbox_functions.py#L44 for the `robot_movej` function that can execute asynchronously. The synchronization functions `time_wait_for_completion()` and `time_wait_for_completion_all()` can be to wait for asynchronous operations to complete.

Sandbox functions are provided to the sandbox using the `PyriSandboxFunctionFactory` factory. It has the following definition:

```
class PyriSandboxFunctionsPluginFactory:
    def __init__(self):
        super().__init__()

    def get_plugin_name(self) -> str:
        return ""

    def get_sandbox_function_names(self) -> List[str]:
        return []

    def get_sandbox_functions(self) -> Dict[str,Callable]:
        return {}
```

The entry point `pyri.plugins.sandbox_functions` is used for this plugin type.

See https://github.com/pyri-project/pyri-example-plugin/blob/master/src/pyri_example_plugin/sandbox_functions.py for a simple example of a sandbox function plugin. See https://github.com/pyri-project/pyri-robotics/blob/master/src/pyri/robotics/sandbox_functions.py for a more complicated example of sandbox functions, used for robotics. See https://github.com/pyri-project/pyri-example-plugin/blob/master/setup.py#L22 for an example of the `entry_points` specification in `setup.py`.

#### Blockly Plugins

Blockly blocks and Blockly categories are added using the plugin type `PyriBlocklyPluginFactory`. These plugins typically do not have any Python code, and instead return JSON and JavaScript for use by the Blockly workspace.

Blockly categories are defined using the `PyriBlocklyCategory` structure:

```
class PyriBlocklyCategory(NamedTuple):
    name: str
    json: str
```

`name` is the name of the category, and `json` is the JSON description of the category as defined at https://developers.google.com/blockly/guides/configure/web/toolbox#json .

Blockly blocks are defined using the `PyriBlocklyBlock` structure:

```
class PyriBlocklyBlock(NamedTuple):
    name: str
    category: str
    doc: str
    json: str
    python_generator: str
```

`name` is the name of the block. `category` is the name of the category to add the block to in the toolbox. `doc` is the documentation to provide to the user about the block. `json` is the block definition as described here: https://developers.google.com/blockly/guides/create-custom-blocks/define-blocks . `python_generator` is the JavaScript function the Blockly compiler will use to generate Python code for the sandbox to execute.

The `PyriBlocklyPluginFactory` has the following definition:

```
class PyriBlocklyPluginFactory:

    def get_plugin_name(self):
        return ""

    def get_category_names(self) -> List[str]:
        return []

    def get_categories(self) -> List[PyriBlocklyCategory]:
        return []

    def get_block_names(self) -> List[str]:
        return []

    def get_block(self,name) -> PyriBlocklyBlock:
        return None

    def get_all_blocks(self) -> Dict[str,PyriBlocklyBlock]:
        return []
```

The entry point `pyri.plugins.blockly` is used for this plugin type.

See https://github.com/pyri-project/pyri-example-plugin/blob/master/src/pyri_example_plugin/blockly.py for a simple example of a Blockly plugin. See https://github.com/pyri-project/pyri-robotics/blob/master/src/pyri/robotics/blockly.py for a more complicated example of sandbox functions, used for robotics. See https://github.com/pyri-project/pyri-example-plugin/blob/master/setup.py#L23 for an example of the `entry_points` specification in `setup.py`.

### RobDef Plugins

The variable storage service, devices states service, and sandbox need to have new Robot Raconteur types included at startup. Unlike clients, Robot Raconteur services cannot dynamically handle unknown data types, so they need to have all types registered with the node. This is accomplished using the plugin type `PyriRobDefPluginFactory`. All Group 1 standard Robot Raconteur types are registered automatically, and do not require plugins to register them.

`PyriRobDefPluginFactory` has the following definition:

```
class PyriRobDefPluginFactory:
    def __init__(self):
        super().__init__()

    def get_plugin_name(self):
        return ""

    def get_robdef_names(self) -> List[str]:
        return []

    def get_robdefs(self) -> List[str]:
        return []
```

The function `get_robdefs()` is expected to return a list of strings containing the service definitions. Typically, the service definitions are included as resources inside the Python package. See the `importlib_resources` package.

The entry point `pyri.plugins.blockly` is used for this plugin type.

See https://github.com/pyri-project/pyri-program-master/blob/master/src/pyri/program_master/robdef.py for an example of a robdef plugin. See https://github.com/pyri-project/pyri-program-master/blob/0c9be2eb9804bd9a572428cbe1e10feb0502ba98/setup.py#L28 for an example of the `entry_points` specification in `setup.py`.


### Devices States Plugins

The devices states service is used to aggregate and distribute state information. Adapter plugins are used to add new state and info types to the service. The `PyriDeviceTypeAdapterPluginFactory` is used for this plugin type. It is expected to instantiate `PyriDeviceTypeAdapter` adapters. See https://github.com/pyri-project/pyri-common/blob/master/src/pyri/plugins/device_type_adapter.py for the definitions of these types.

The entry point `pyri.plugins.device_type_adapter` is used for this plugin type.

See https://github.com/pyri-project/pyri-robotics/blob/master/src/pyri/robotics/device_type_adapter.py for an example of a devices states plugin. See https://github.com/pyri-project/pyri-robotics/blob/9adbf3f7ba807b827ecab0e78bc6923cfbee6b39/setup.py#L30 for an example of the `entry_points` specification in `setup.py`.

Developing devices states adapters is a rarely required and potentially challenging task. Please request assistance at https://github.com/pyri-project/pyri-core/discussions if necessary.

### WebUI Server Plugins

The WebUI is a simple HTTP server that is used to initialize the WebUI in a browser. It is implemented using the "sanic" Python HTTP server. By default it provides the following functionality:

* Static file serving
* Configuration information, including the available Python wheels and Blockly blocks
* Blockly block definitions

Plugins can add "sanic" routes to the server. These routes are added to the location `/plugins/{plugin_name}/`. The `PyriWebUIServerPluginFactory` is used to specify the plugin route to add for the plugin:

```
class PyriWebUIServerPluginFactory:

    def get_plugin_name(self) -> str:
        return ""

    def get_plugin_route_handler(self) -> Callable[["sanic.request.Request",str],"sanic.response.BaseHTTPResponse"]:
        return None
```

See `https://sanicframework.org/en/guide/basics/routing.html` for more information on sanic routing. The `PyriWebUIResourceRouteHandler` is a helper class provided for returning files embedded in a Python package.

The entry point `pyri.plugins.webui_server` is used for this plugin type.

See https://github.com/pyri-project/pyri-example-plugin/blob/master/src/pyri_example_plugin/webui_server.py for an example of a server plugin. See https://github.com/pyri-project/pyri-example-plugin/blob/677c87e854f7f45cd9de09bdf030308838a695df/setup.py#L24 for an example of the `entry_points` specification in `setup.py`.

### Service Launch Plugins

Extension packages can contain services that need to be launched when the teach pendant software is started. `pyri-core` starts services, and manages their lifecycle. Services should use the `PyriServiceNodeSetup` class to start and configure the service for use by the teach pendant system. It has a `wait_exit()` function, that listens for the shutdown signal from `pyri-core` so the service is stopped appropriately. See https://github.com/pyri-project/pyri-robotics/blob/master/src/pyri/robotics/robotics_motion_service/__main__.py for an example of a service designed to be executed by `pyri-core`. Note that the service definition is stored in the package as a resource file, and loaded by the node setup class.

`pyri-core` uses the `PyriServiceNodeLaunchFactory` plugin factory type to understand which services to launch. This plugin type returns `ServiceNodeLaunch` named tuples which contain instructions to launch the service. `ServiceNodeLaunch` has the following definition:

```
class ServiceNodeLaunch(NamedTuple):
    name: str
    plugin_name: str
    module_main: str
    add_arg_parser_options: Callable[[argparse.ArgumentParser],None] = _default_add_args
    prepare_service_args: Callable[[argparse.Namespace],List[str]] = _default_prepare_args
    depends: List[str] = ["device_manager"]
    depends_backoff: float = 1
    restart: bool = False
    restart_backoff: float = 5
    default_devices: List[Tuple[str,str]] = []
    extra_params: dict = None
```

The `module_main` is the module that should be executed. It is started using `python -m <module_name>`

The `add_arg_parser_options` and `prepare_service_args` functions are used to add additional command line options to `pyri-core`, which can then be passed to the service. See https://github.com/pyri-project/pyri-variable-storage/blob/7919cee3bf3569abaada1db9950a7530c7c79b9e/src/pyri/variable_storage/service_node_launch.py#L3 for an example of how these are used to add custom command line options.

`default_devices` is used to specify that a device with a specified identifier name should be added. For instance, for variable storage `default_devices` is

```
default_devices=[("pyri_variable_storage","variable_storage")]
```

Which will add the device named `pyri_variable_storage` with local device name `variable_storage`

The plugin factory has the following definition:
```
class PyriServiceNodeLaunchFactory:
    def __init__(self):
        pass

    def get_plugin_name(self):
        return ""

    def get_service_node_launch_names(self) -> List[str]:
        return []

    def get_service_node_launches(self) -> List[ServiceNodeLaunch]:
        return []
```

The entry point `pyri.plugins.service_node_launch` is used for this plugin type.

See https://github.com/pyri-project/pyri-robotics/blob/master/src/pyri/robotics/service_node_launch.py for an example of a server plugin. https://github.com/pyri-project/pyri-robotics/blob/9adbf3f7ba807b827ecab0e78bc6923cfbee6b39/setup.py#L34 for an example of the `entry_points` specification in `setup.py`.

## WebUI Plugins

WebUI plugins are distributed using packages, similar to runtime extension packages. However, these packages should not be installed into the normal Python installation location. Instead, the Wheel file should be copied to the WebUI Server Wheel directory. For Conda environments, this location is:

```
$CONDA_PREFIX/pyri-project/pyri-webui-server/wheels
```

The WebUI server must be restarted if wheels are changed.

### WebUI Panel Plugin

The WebUI runs inside a browser using Pyodide. This allows for the WebUI to run normal Python code, and also to interact with the JavaScript running in the browser. See https://github.com/iodide-project/pyodide/blob/master/docs/usage/type-conversions.md for more information on communicating with JavaScript from Python. The JavaScript communication is primarily used for interacting with the HTTP DOM, and for receiving events from the user. The WebUI uses "Golden Layout" (https://golden-layout.com/), Vue.js (https://vuejs.org/), and Bootstrap/BootstrapVue (https://vuejs.org/) on the JavaScript side to build the user interface.

During the initialization of the WebUI, the WebUI server provides `config` JSON information. This includes a list of wheels that can be downloaded from the `/wheels/` directory on the server. The initialization process will download and extract all of the available wheels into the Pyodide virtual filesystem. These wheels then become available as if they had been installed normally. This includes the metadata of the packages, so the entry points technique for detecting plugins continues to work.

WebUI plugins are initialized after the core has been initialized. WebUI plugins use the `PyriWebUIBrowserPanelPluginFactory` factory type. It has the following definition:

```
class PyriWebUIBrowserPanelPluginFactory:
    def __init__(self):
        super().__init__()

    def get_plugin_name(self) -> str:
        return ""

    def get_panels_infos(self) -> Dict[str,PyriWebUIBrowserPanelInfo]:
        return []

    async def add_panel(self, panel_type: str, core: "PyriWebUIBrowser", parent_element: Any) -> PyriWebUIBrowserPanelBase:
        raise NotImplementedError()
```

On load, the WebUI core will call `add_panel` for each panel type returned by `get_panel_infos`. It is expected that the `add_panel` method will add a panel to the golden layout. The HTML template for the panel can be stored in a separate HTML file and loaded using `importlib_resources`, or it can be generated dynamically.

The panel HTML may use Vue to assist with the display. The devices states data is received by the core, and stored in a WebUI core class. This instance can be retrieved, and the state data displayed.

Vue.js, Bootstrap, and BootstrapVue are commonly used for panels. See the examples, and the documentation for these projects for more information.

The entry point `pyri.plugins.webui_browser_panel` is used for this plugin type.

See https://github.com/pyri-project/pyri-webui-browser/blob/master/src/pyri/webui_browser/panels/jog_panel.py, https://github.com/pyri-project/pyri-webui-browser/blob/master/src/pyri/webui_browser/panels/jog_panel.html, and https://github.com/pyri-project/pyri-robotics-browser/blob/master/src/pyri/robotics_browser/panels/robotics_panels.py for an example of adding panels to the WebUI.

### WebUI Variable Editors

Variable editors are used to create and edit new data types. These are accessed through the "Globals" subpanel in the "Program" panel. The plugin uses the `PyriWebUIBrowserVariableDialogPluginFactory`. Adding variable editors is a rarely necessary task. Please request assistance at https://github.com/pyri-project/pyri-core/discussions if necessary.

The entry point `pyri.plugins.webui_browser_variable_dialog` is used for this plugin type.

See https://github.com/pyri-project/pyri-vision-browser/blob/master/src/pyri/vision_browser/dialogs/new_image_template_dialog.py, https://github.com/pyri-project/pyri-vision-browser/blob/master/src/pyri/vision_browser/dialogs/new_image_template_dialog.html, and https://github.com/pyri-project/pyri-vision-browser/blob/master/src/pyri/vision_browser/dialogs/vision_variable_dialogs.py for an example of a server plugin. See https://github.com/pyri-project/pyri-vision-browser/blob/af23af3b2dc0e2868d985c506646fcfbcaaa7082/setup.py#L24 for an example of the `entry_points` specification in `setup.py`.

## Conda Package Distribution

Conda is used to distribute PyRI packages, since it allows including all the various types of dependencies and miscellaneous files required. A full document describing how to build these packages is being written for the Robot Raconteur ecosystem. For now, see the Conda packaging documentation https://docs.conda.io/projects/conda-build/en/latest/user-guide/tutorials/build-pkgs.html . It is recommended that `conda-smithy` be used for building the packages. See https://conda-forge.org/docs/user/ci-skeleton.html . Packages should be developed to conform to `conda-forge` package dependencies. Create a new anaconda.org account to distribute your plugins using your channel.

See https://github.com/pyri-project-conda/pyri-tesseract-planner-feedstock for an example `conda-smithy` feedstock for the `pyri-tesseract-planner` package. This feedstock builds a Conda package for the `pyri-tesseract-planner` package, which can be found at https://github.com/pyri-project/pyri-tesseract-planning . The package contains a sandbox function plugin, a blockly plugin, and an additional service. (Note that this service **does not** launch automatically). The feedstock
also includes the `pyri-tesseract-planner-browser` package, which can be found at https://github.com/pyri-project/pyri-tesseract-planning-browser . This package is built to a wheel, and copied into the special WebUI server directory. See https://github.com/pyri-project-conda/pyri-tesseract-planner-feedstock/blob/master/recipe/build.sh and https://github.com/pyri-project-conda/pyri-tesseract-planner-feedstock/blob/master/recipe/bld.bat for examples of installing the runtime and browser packages to the correct locations.