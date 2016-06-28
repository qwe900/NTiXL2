# NTi XL2 module

The Python module `ntixl2` implement an API for the Remote Measurement usage of  the **NTi XL2** 
sound level meter.

**Disclaimer**: This module is in development, and might break what you're working on.

## System requirements
The implementation is for linux systems only

**systems requirements**


1. **device file name**

    the XL2 device can either be in serial mode or in mass storage mode. When the XL2 is plugged in to an usb port\
    it can be detected using the device vendor-id `1a2b` and the device product-id  which is:
        - `0003` if device in mass storage modus
        - `0004` if device in serial mode

    the :class:`ntixl2.xl2.XL2SLM` to work properly need  to known the device file created by the system under \
    the `/dev/` folder for both XL2 mode. The **problem ist that the device filename can change** when the XL2 is\
    plugged and unplugged. Using `udev` rules it is possible to create a fixed symlynk name which point\
    to the correct device file.

    **The symlink  device names for mass storage mode and serial mode are necessary parameter to be passed during class \
    initiation.**

2. **auto mounting**

    the XL2 in mass storage mode should be auto mounted to a fixed path

    **The path where the device is auto mounted is a necessary parameter to be passed during class initiation.**

    `udev` rules can be used to achieve this behaviours.

**`udev` rule example**

``` bash
    #! /bin/sh
    
    #######################################
    #    USB Flash Drives automounting    #
    #######################################
    ENV{mount_options_vfat}="gid=100,dmask=000,fmask=111,utf8,flush,rw,noatime,users"
    ENV{mntDir}="/media/XL2-sd"
    
    # start at sdb to ignore the system hard drive
    ACTION == "add", KERNEL=="sd[b-z]?", ATTRS{idVendor}=="1a2b",ATTRS{idProduct}=="0003", GROUP="users", SYMLINK+="XL2-sd" ,RUN+="/bin/mkdir -p '%E{mntDir}'" ,RUN+="/bin/mount /dev/XL2-sd -t auto '%E{mntDir}'"
    ACTION == "add", KERNEL=="ttyA*", ATTRS{idVendor}=="1a2b",ATTRS{idProduct}=="0004", GROUP="users", SYMLINK+="XL2"
    
    with this rule  we have the following parameter (default) to pass during class initiation:
    - Fixed device name (`XL2`) if connected as serial device
    - Fixed device name (`XL2-sd`) if connected as mass storage device
    - automount to fixed path (`/media/XL2-sd`) if device connected as mass storage
```
## Installation

Currently there are no packages available.

The recommended method to install is to clone this repository

`git clone https://github.com/e-sr/NTiXL2.git`

and install this package in development mode

`python setup.py develop`

This way one can easily update to the latest version using

`git pull`

and running again

`python setup.py develop`

## Examples

Examples can be found in the `examples` folder.

## Documentation

Documentation can be found [online](https://htmlpreview.github.io/?https://raw.githubusercontent.com/e-sr/NTiXL2/master/doc/_build/html/index.html).

## License

The `ntixl2` package is distributed under the GPLv3 license. See LICENSE for more information.

