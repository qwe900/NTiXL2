"""The xl2.py module implement the XL2 device.

Note
----
- **The implementation is for linux systems only**

- **Systems requirements**

    1. **device file name**

        The XL2 device can either be in serial mode or in mass storage mode. When the XL2 is plugged in to an usb port\
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

    3. **umount**

        to ummount the XL2 device and switch to serial mode ist necessary the linux bash command `Eject`.

    4. **`udev` rule example**

        Information on `udev` rules can be found here<http://www.reactivated.net/writing_udev_rules.html>_ .

        .. code-block:: bash

            #! /bin/sh

            #######################################
            #    XL2SLM device rules              #
            #######################################

            # Symlink 'XL2-sd' and auto mount if device mass storage mode
            #############################################################
            #mounting point
            ENV{mntDir}="/media/XL2-sd"
            # start at sdb to ignore the system hard drive
            ACTION == "add", KERNEL=="sd[b-z]?", ATTRS{idVendor}=="1a2b",ATTRS{idProduct}=="0003", GROUP="users", SYMLINK+="XL2-sd" ,RUN+="/bin/mkdir -p '%E{mntDir}'" ,RUN+="/bin/mount /dev/XL2-sd -t auto '%E{mntDir}'"

            # Symlink 'XL2' if device in serial mode
            ########################################
            ACTION == "add", KERNEL=="ttyA*", ATTRS{idVendor}=="1a2b",ATTRS{idProduct}=="0004", GROUP="users", SYMLINK+="XL2"

        With this rule  we have the following parameter (default) to pass during class initiation:

            - Fixed device name (`XL2`) if connected as serial device
            - Fixed device name (`XL2-sd`) if connected as mass storage device
            - automount to fixed path (`/media/XL2-sd`) if device connected as mass storage

- **XL2 settings**

    1. automatic switch to serial mode when plugged in

Todo
----
- implement object for window usage too
- implement device detection in __init__ method using device **uuid** and without symlink

"""

import os
import time
import subprocess
import warnings
import pathlib,shutil
import serial
from serial.tools import list_ports
from .message import ECHO, SYSTEM_MSDMAC,RESET, SYSTEM_KEY, QUERY_SYSTEM_ERROR, QUERY_IDN, \
    SYSTEM_KLOCK, QUERY_INITIATE_STATE

class XL2Error(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

##func
def safe_remove_mass_storage_device(device, mountDir):
    """Umount and eject device

    Parameters
    ----------
    device : str
        device file path
    mountDir : str
        device mount path

    Note
    ----
    this function  need the `Eject` linux program

    """
    subprocess.call(["sudo", "umount", "-l", mountDir])
    subprocess.call(["sudo", "eject", device])
    subprocess.call(["sudo", "rmdir", mountDir])


class XL2SLM(object):
    """The XL2 device object.

    Attributes
    -----------
        serialDev : str
            device path in serial modus
        storageDev : str
            device path in mass storage modus
        mountDir : str
            directory path where device is automatically mounted


    """

    def __init__(self,mountDir,  serialDev='/dev/XL2', storageDev = '/dev/XL2-sd'):
        """Initiate

        Parameters
        ----------
        serialDev : str
            XL2 device file when in serial modus
        storageDev : str
            XL2 device file when in mass storage modus
        mountDir : str
            XL2 mount directory

        """
        self.serialDev = serialDev
        self.storageDev = storageDev
        self.mountDir = pathlib.Path(mountDir)
        self.device_status

    def _which_device(self):
        #return which device is connected
        try:
            os.stat(self.serialDev)
        except FileNotFoundError:
            pass
        else:
            return self.serialDev
        # is mass storage device there?
        try:
            os.stat(self.storageDev)
        except  FileNotFoundError:
            pass
        else:
            return self.storageDev

    def _conn_active(self):
        # test if connection si active
        mess = ECHO()
        try:
            self.conn.write((mess.to_str()).encode('ascii'))
        except (serial.SerialException,AttributeError) as e:
            return False
        else:
            try:
                self.conn._timeout = 0.5
                line = self.conn.readline().decode('UTF-8')
            except serial.SerialException:
                self.conn._timeout = 1
                return False
        self.conn._timeout = 1
        return line == "deb" + mess.EOL

    @property
    def device_status(self):
        """ :obj:`str`: describing the device status. The status can be one of {'SERIAL'| 'MASS'}

        Raise :class:`ntixl2.xl2.XL2ERROR` if the status can't be defined.

        """
        # if self._conn_active():
        #     return 'SERIAL'
        # else:
        dev = self._which_device()
        if dev == self.serialDev:
            try :
                self.conn = serial.Serial(self.serialDev, baudrate=9600, timeout=1)
            except serial.SerialException:
                raise XL2Error('Serial Error, Not able to serial connect')
            else:
                return 'SERIAL'
        elif dev == self.storageDev:
            mnt = self._mount_status()
            if mnt['mounted']:
                return 'MASS'
            else:
                return 'MASS'
                # TODO: Handle this correctly, is wrong in _mount_status()
                # raise XL2Error('Device not correct mounted')
        else:
            raise XL2Error('No XL2 device found')

    def _mount_status(self):
        disk = None
        # context = pyudev.Context()
        # for i,d in enumerate(psutil.disk_partitions()):
        #     try:
        #         device = pyudev.Device.from_device_file(context,d.device)
        #     except pyudev.DeviceNotFoundByFileError:
        #         pass
        #     else:
        #         links = list(device.device_links)
        #         if self.storageDev in links:
        #             disk = d
        #             #print("Device 'XL2-sd'->{} , present.".format(d.device))
        if disk is not None:
            return {'mounted': True, 'path':disk.mountpoint, 'device_file':disk.device}
        else:
            return {'mounted': False, 'path':''}

    def to_mass(self):
        """ Switch the device into MASS status.

        send a serial message to switch the XL2 device to "MASS" status.


        Note
        ----
            The function is blocking till the switch is successful. This can take many seconds.

        See Also
        --------
        :func:`ntixl2.xl2.safe_remove_mass_storage_device`

        """
        status = self.device_status
        if status == 'SERIAL':
            mess = SYSTEM_MSDMAC()
            try:
                self.serial_message(mess)
            except serial.SerialException:
                print("Serial connection is broken.")
            self.conn.close()
            success,i = False,0
            time.sleep(20)
            while not success:
                time.sleep(5)
                try:
                    status = self.device_status
                except XL2Error:
                    success = False
                else:
                    success = (status == 'MASS')
                if i >20:
                    warnings.warn("timeout", UserWarning)
                    break
                i += 1
        elif status == 'MASS':
            print("XL2 already in 'MASS' status ")

    def to_serial(self):
        """ Switch the device into SERIAL status.

        switch is done by umount and eject the  XL2 device.

        Note
        ----
            The function is blocking till the switch is successful. This can take many seconds.

        """
        status = self.device_status
        if status == 'MASS':
            safe_remove_mass_storage_device(str(self.storageDev), str(self.mountDir))
            success,i = False,0
            time.sleep(30)
            while not success:
                i+=1
                time.sleep(5)
                try:
                    status = self.device_status
                except XL2Error:
                    success = False
                else:
                    success = (status == 'SERIAL')
                if i > 20:
                    warnings.warn("timeout", UserWarning)
                    break
        elif status == 'SERIAL':
            print("XL2 already in 'SERIAL' status ")


    def memory_usage(self):
        """memeory usage on the XL2 sd-card

        device_status has to be MASS

        Returns
        -------
        int
            memeory usage on the XL2 sd-
        """
        if self.device_status == 'MASS':
            return shutil.disk_usage(self.mountDir.as_posix())
        else:
            raise XL2Error('device_status has to be MASS.')
        
    def list_files(self, relPath='', filter = '*'):
        """list files

        device_status has to be MASS

        Parameters
        ----------
        relPath : str
            path relative to mount directory
        filter : str

        Returns
        -------
        list
            list of files names

        """
        if self.device_status=='MASS':
            path = self.mountDir.joinpath(relPath)
            return [str(p) for p in path.glob(filter) if p.is_file()]
        else:
            raise XL2Error('device_status has to be MASS.')

    def list_dir(self, relPath='', filter = '*'):
        """ list directories

        device_status has to be MASS

        Parameters
        ----------
        relPath : str
            path relative to mount directory
        filter : str

        Returns
        -------
        list
            list of directory names

        """
        if self.device_status=='MASS':
            path = self.mountDir.joinpath(relPath)
            path.glob(filter)
            return [str(p) for p in path.glob('*') if p.is_dir()]
        else:
            raise XL2Error('device_status has to be MASS.')

    def serial_message(self, message, wait = 5):
        """

        Parameters
        ----------
        message : :obj:`ntixl2.message.Message` object
        wait : float
            Connection timeout to wait for serial line read in case of message without expected answers.

        Returns
        -------
        dict
            parsed message answers according to message object if message has answers. else **None**
            See :meth:`ntixl2.message.Message.parse_answers`

        Note
        ----
        for messages with answers the connection read timeout is set to 5 seconds.

        """

        if self.device_status == 'SERIAL':
            # write message
            self.conn.write((message.to_str()).encode('ascii'))
            # read returmn lines
            if message.RETURN is not None:
                self.conn._timeout = wait
                ret = []
                for i in range(message.return_lines()):
                    line = self.conn.readline().decode('ascii')
                    assert not line == ""
                    ret.append(line)
                self.conn._timeout = 1
                ret = message.parse_answers(ret)
            else:
                # if message has no return raise error if there is a return
                self.conn._timeout = 0.1
                line = self.conn.readline().decode('ascii')
                self.conn._timeout = 1
                if not line == "":
                    raise ValueError('message expect no return,answer is {}.'.format(line))
                ret = None
            self.conn.close()
            return ret
        else:
            raise XL2Error('device_status has to be SERIAL')

    def select_profile(self, profile=5):
        """ Reset device and load the wanted profile

        The profile number refer to the profile order in the profile Menu

        Parameters
        ----------
        profile : int
            profile number. The profile number refer to the profile order in the profile menu.

        Note
        ----
        The function wait for the 'OK' status of the :obj:`ntixl2.message.SYSTEM_KEY` message. Another 5 seconds waiting to load the\
        profile

        """
        # reset
        m = RESET()
        self.serial_message(m)
        # key msg
        m = SYSTEM_KEY()
        # select profile
        for par in ['ESC', 'ENTER'] + ['NEXT'] * 8 + ['ENTER'] * 2 + ['NEXT'] * profile + ['ENTER']:
            m.append_param(par)
        r = self.serial_message(m)
        assert r['status'] == 'ok'
        time.sleep(5)


    def klock(self, locked = False):
        """Lock unlock XL2 keyboard

        Parameters
        ----------
        locked : bool
            if True lock keyboard else unlock

        """
        if locked:
            self.serial_message(SYSTEM_KLOCK.ON())
        else:
            self.serial_message(SYSTEM_KLOCK.OFF())

    def check_errors(self):
        """ Read the XL2 Error queue and return a list of errors

        Returns
        -------
        list
            list of errors

        See Also
        --------
        :class:`ntixl2.message.QUERY_SYSTEM_ERROR`

        """
        return self.serial_message(QUERY_SYSTEM_ERROR())

    def reset(self):
        """ Reset the XL2 device

        See Also
        --------
        :class:`ntixl2.message.RESET`

        """
        self.serial_message(RESET())

    def identification(self):
        """ Return the XL2 device identification data

        Returns
        -------
        dict
            identification dict

        See Also
        --------
        :class:`ntixl2.message.QUERY_IDN`

        """
        return self.serial_message(QUERY_IDN())

### other functions

def find_xl2(linux = True, filter= "XL2"):
    """
    listet alle vorhandene serielle Ports welches Geraet Beschreibung enthalten die string  'filter'
    
    :param linux:
    :param filter: string
    :return: liste aus dict mit serielle ports attributen
    """
    comports = list(list_ports.comports())
    attr = ['device', 'description','pid','vid','serial_number', 'product','manufacturer','interface','hwid']
    devices = []
    for p in comports:
        if linux:
            attribute = {a : getattr(p,a) for a in attr}
            if filter in  attribute['description']:
                attribute['pid'] = format( attribute['pid'], '#06x')
                attribute['vid'] = format( attribute['vid'], '#06x')
                devices.append(attribute)
        else:
            attribute = p
            q = any([(filter in v) for v in p if type(v)=='str'])
            print('Device: ', attribute[1], ', filter: ', q)
            if q:
                devices.append(attribute)
    return devices





