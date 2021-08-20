# Time Blocks and Sandbox Functions

"Time" section in the Blockly toolbox. Provides blocks and functions for time operations including sleeping and synchronizing in process actions. These functions and blocks are provided by the `pyri-common` package.

## time_wait

![](figures/blocks/time_wait.png)

    time_wait(seconds)

Wait for a specified time in seconds.

Parameters:

* seconds (float) Time to wait in seconds

## time_wait_for_completion

![](figures/blocks/time_wait_for_completion.png)

    time_wait_for_completion(local_device_name, timeout)

Wait for an asynchronous operation to complete for specified
device. Raises an error if timeout expires before completion.

Parameters:

* local_device_name (str): Name of the device to wait for completion
* timeout (float): Wait timeout in seconds

## time_wait_for_completion_all

![](figures/blocks/time_wait_for_completion_all.png)

    time_wait_for_completion_all(timeout)

Wait for all asynchronous operations on all devices to complete.
Raises an error if timeout expires before completion.

Parameters:

* timeout (float): Wait timeout in seconds