# NTi XL2 module

The Python module `ntixl2` implement an API for the Remote Measurement usage of  the **NTi XL2** 
sound level meter.

**Disclaimer**: This module is in development, and might break what you're working on.

The module contains:

 - a submodule `message` containing serial messages implementations
 - a submodule `xl2` containing the XL2SLM object 
 - a submodule `xl2parser` containing tools for parsing XL2 output data.

## System requirements

The submodule `xl2` works only under linux systems. The requirements on  the system and on the XL2SLM  device are listed
in the documentation of the **xl2 submodule**.

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