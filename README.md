# NTi XL2 module

The Python module `ntixl2` implement an API for the Remote Measurement usage of  the **NTi XL2** 
sound level meter.

**Disclaimer**: This module is in development, and might break what you're working on.

## System requirements
**linux**
TODO

- XL2Basic with device UUID
- XYL2AutoDetect

- **mass storage** name='XL2_SD-Card', id=0003: Der lärmessgerät verhält sich wie ein Speicher. 
- **seriale verbindung**, name='XL2_Remote', id=0004  : Der lärmessgerät bietet eine seriale Schnittstelle. den device ist unten ttyACM zu finden

-The xl2 device name has to be:

    - Fixed device name (`XL2`) if connected as serial device
    - Fixed device name (`XL2-sd`) if connected as mass storage device
    - automount to fixed path (`/media/XL2-sd`) if device connected as mass storage

-Use udev rules to achieve this behaviour

The mounting directory has to

### device recognition
`udev`

```bash

```

The implementation is for linux systems with following requirements:



### automount device
Wenn der Lärmmessgerät an RPI mit USB verbunden ist kann sich in zwei unterschiedliche Moden befinden:

- **mass storage** name='XL2_SD-Card', id=0003: Der lärmessgerät verhält sich wie ein Speicher. 
- **seriale verbindung**, name='XL2_Remote', id=0004  : Der lärmessgerät bietet eine seriale Schnittstelle. den device ist unten ttyACM zu finden

In Beide fälle ist den gerät erkennbar durch ID_VENDOR=NTiAudio, ID_VENDOR_ENC=NTiAudio, ID_VENDOR_ID=1a2b

## Installation

Currently there are no packages available.

The recommended method to install is to clone this repository

`git clone git@github.com:python-acoustics/python-acoustics.git`

and install this package in development mode

`python setup.py develop`

This way one can easily update to the latest version using

`git pull`

and running again

`python setup.py develop`

## Examples

Examples can be found in the `examples` folder.

## Documentation

Documentation can be found [online](http://python-acoustics.github.io/python-acoustics/).

## License

`python-acoustics` is distributed under the BSD 3-clause license. See LICENSE for more information.

python  setup.py develop
```
# system requirements
