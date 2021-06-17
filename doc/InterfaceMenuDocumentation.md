

# Pyri Interface Menu Documentation


## ARM 19-01 F-24



## 1.0: Devices Menu


The devices menu provides all the elements required to connect to devices in this system. On loading, the devices menu will show all active devices connected to the system. The view
of the devices can be toggled using the "Show card view" button at the upper right, adjacent to the search menu. Table View can be seen in Figure 1 below and Card View can be seen in Figure 2.


<figure><img src="figures/pyri_software_architecture/devicemenutableview.png"><figcaption>Figure 1: Device Menu in Table View Mode</figcaption></figure>


<figure><img src="figures/pyri_software_architecture/devicemenucardview.png"><figcaption>Figure 2: Device Menu in Card View Mode</figcaption></figure>

Each device in the menu has a local name that you specify when you add the device into the system, this is the name that can be used to refer to the device in other sections of the UI, such as in the Blockly code. It also has its own Device Name that the UI obtains from the service itself along with its Device Type. The entry also displays the current connection Status of the device. The status can be either Ready, Connected or Error, with Connected specifying an active connection to a device or robot that has not yet been enabled. For additional information on the device you can press the Blue I icon under Actions.
Additional features of this menu include the ability to search for desired devices using the search menu in the upper right and also select multiple devices and delete them using the "Remove Selected Devices" button in the upper left. Individual services can also be deleted using the Trash can icon under that device's Actions.
To add a new device into the system you press the green "Add Device" button. This will open the interface shown in Figure 3. This menu features a list of all Robot Raconteur visible device services using service discovery. The view of visible services can be refreshed with the "Refresh" button at the top left. This menu gives you all the appropriate information to verify the service you are connecting to is the correct one. To add the service, simply press the blue + icon listed under Actions. This will open up a prompt, shown in Figure 4, asking you to specify a unique Local Device Name to give the device that other parts of the interface can use to refer to the device.


<figure><img src="figures/pyri_software_architecture/adddevice.png"><figcaption>Figure 3: Add Device Menu</figcaption></figure>

<figure><img src="figures/pyri_software_architecture/enterdevicename.png"><figcaption>Figure 4: Enter Local Device Name Prompt</figcaption></figure>
