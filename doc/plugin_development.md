# PyRI Plugin Development

PyRI is a modular software system, designed to be easily extensible. It consists of three major parts:

* **Runtime** - The runtime stores user programs, executes user programs, provides a server for the WebUI, and interacts with the rest of the automation system.
* **WebUI** - The user interface that interacts with the Runtime to program and control the system.
* **Devices** - The other automation devices in the system. These typically communicate with the Runtime using ROS or Robot Raconteur

Plugins are developed to extend the functionality of the Runtime and the WebUI. These plugins are capable of providing interfaces to other automation components, providing new programming capabilities, and adding new panels to the user interface.

### Plugin Architecture

Plugins in PyRI provide a "factory" for plugin type they implement. Each plugin type has a base class that describes the methods that the plugin must implement. The plugins are detected at load time using the `entry_points` portion of a Python package manifest. See https://packaging.python.org/specifications/entry-points/ for more information on `entry_points`. The function specified as the entry point for a plugin type must return an instantiated plugin factory for the specified type.

### Example Plugin

See https://github.com/pyri-project/pyri-example-plugin for an example PyRI plugin.

### Runtime and WebUI shared plugins

The Runtime and WebUI can use the same plugin, but due to the limited ability to load non-pure Python dependencies on the Pyodide interpreter, it is recommended that plugin packages be targeted at only the Runtime or WebUI.

## Runtime Plugins

The Runtime consists of the following Robot Raconteur nodes:

* **Variable Storage** - Stores all data relating to the current program, including global variables, procedures, active device information, etc.
* **Device Manager** - Detects available devices on the network, manages devices selected by the program, and provides connection information. The `DeviceManagerClient` package provides automatic connections to devices.
* **Devices States** - Connects to all devices, and aggregates state information. Clients can request the aggregated state with an update rate of 10 Hz
* **Sandbox** - Executes user programs written in Blockly or PyRI
* **WebUI Server** - Provides a server to initialize and run the WebUI

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

## Sandbox Plugins

The sandbox plugins allow for the addition of functions that are made available to the sandbox environment, and custom Blockly blocks that are presented to the user.

### Sandbox Functions Plugin

Sandbox functions are injected into the sandbox runtime environment, so that user procedures can execute them. They run outside of the sandbox, and have pull access to the sandbox node. The sandbox is considered to be ephemeral, meaning that it may be destroyed and restarted between procedures. This allows for the plugins and other parts of the sandbox to be refreshed without needing to restart the rest of the system nodes. Because of this behavior, the plugins must not assume that any global data will remain between the execution of procedures. Any persistent data must be stored in the Variable Storage node.

Sandbox functions are provided state information, access to the Robot Raconteur node, access to the device manager client, and a "print" function that is shown to the user through the `PyriSandboxContext` object. This object is thread-static. It has the following definition:

```
class PyriSandboxContext(threading.local):
    node = None
    device_manager = None
    print_func = None
```

Sandbox functions are standard Python functions. They are provided to the sandbox using the `PyriSandboxFunctionFactory` factory. It has the following definition:

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

See https://github.com/pyri-project/pyri-example-plugin/blob/master/src/pyri_example_plugin/sandbox_functions.py for an example of a sandbox function plugin.

### Blockly Plugins

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

See https://github.com/pyri-project/pyri-example-plugin/blob/master/src/pyri_example_plugin/blockly.py for an example of a blockly plugin.

## WebUI Server plugins

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

See https://github.com/pyri-project/pyri-example-plugin/blob/master/src/pyri_example_plugin/webui_server.py for an example of a server plugin.

## WebUI Panel Plugin

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

The panel HTML may use Vue to assist with the display. The devices states data is received by the core, and stored in a Vuex instance. This instance can be retrieved, and the state data displayed. 

The entry point `pyri.plugins.webui_browser_panel` is used for this plugin type.

See https://github.com/pyri-project/pyri-webui-browser/blob/master/src/pyri/webui_browser/panels/jog_panel.py and https://github.com/pyri-project/pyri-webui-browser/blob/master/src/pyri/webui_browser/panels/jog_panel.html for an example of adding panels to the WebUI.


