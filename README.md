<ins>**__BridgeGui__**</ins>

**Description**

This is a simple Gui to create bridge interfaces in order to bridge your network interface to your virtual machine.


**Todo**

Workaround for wireless interfaces as they do not allow to be enslaved to a bridge.


**Dependencies**

This programm needs wxpython to run:

Debian:
`sudo apt install python-wxgtk3.0`

Manjaro:
`pamac install python-wxpython`

or build from source:
https://wiki.wxpython.org/How%20to%20install%20wxPython

**Usage**

Open a terminal and type:
`python <Path/to/file/>bridgeGui`
or launch it with your window manager.


**Note**

This progam needs administrator rights and will ask you to type in a password.

It will create a group "netAdmin" in order to manage ip interfaces.
Use with caution.

