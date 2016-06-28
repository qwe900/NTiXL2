"""The xl2.py module implement the XL2 device.

Note
----
- The implementation is for linux systems only

- **Systems requirements**

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

    3. **umount**
        to ummount the XL2 device and switch to serial mode ist necessary the linux bash command `Eject`.

    4. **`udev` rule example**

        .. code-block:: bash

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

- **XL2 settings**

    1. automatic switch to serial mode
Todo
----
- implement object for window usage too
- implement device detection in __init__ method using device **uuid** and without symlink



"""

import os
import time
import subprocess
import pathlib,shutil
import psutil#, pyudev
import serial
from serial.tools import list_ports
from .message import SYSTEM_MSDMAC,RESET, SYSTEM_KEY, QUERY_SYSTEM_ERROR, QUERY_IDN, SYSTEM_KLOCK, QUERY_INITIATE_STATE

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
    subprocess.call("sudo umount -l {}".format(mountDir))
    subprocess.call("sudo rmdir".format(mountDir))
    subprocess.call("sudo eject {}".format(device))


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

    def __init__(self, serialDev='/dev/XL2', storageDev = '/dev/XL2-sd', mountDir = '/media/XL2-sd'):
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

    @property
    def device_status(self):

        """ :obj:`str`: describing the device status. The status can be one of {'SERIAL'| 'MASS'}

        Raise `ntixl2.xl2.XL2ERROR` if the status can't be defined.

        """
        try:
            self.conn.inWaiting()
        except:
            dev = self._which_device()
            if dev == self.serialDev:
                try :
                    self._init_serial_conn()
                except serial.SerialException:
                    raise XL2Error('Serial Error')
                else:
                    return 'SERIAL'
            elif dev == self.storageDev:
                mntStatus = True#
                if mntStatus:
                    return 'MASS'
                else:
                    raise XL2Error('Device not correct mounted')
            else:
                raise XL2Error('No XL2 device found')
        else:
            return 'SERIAL'

    # def _mount_status(self):
    #     disk = None
    #     context = pyudev.Context()
    #     for i,d in enumerate(psutil.disk_partitions()):
    #         try:
    #             device = pyudev.Device.from_device_file(context,d.device)
    #         except pyudev.DeviceNotFoundByFileError:
    #             pass
    #         else:
    #             links = list(device.device_links)
    #             if self.storageDev in links:
    #                 disk = d
    #                 #print("Device 'XL2-sd'->{} , present.".format(d.device))
    #     if disk is not None:
    #         return {'mounted': True, 'path':disk.mountpoint, 'device_file':disk.device}
    #     else:
    #         return {'mounted': False, 'path':''}

    def _init_serial_conn(self):
        # initiate the serial connection
        try:
            self.conn = serial.Serial(self.serialDev, baudrate=9600, timeout=10)
        except serial.SerialException as e:
            print('Not able to serial connect device {}'.format(self.serialDev))
            raise e

    def _which_device(self):
        #return which device is connected
        try:
            os.stat(self.serialDev)
        except  FileNotFoundError:
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

    def to_mass(self):
        """ Switch the device into MASS status.

        send a serial message to switch the XL2 device to "MASS" status.

        Returns
        -------
        bool
            if switch is successful *True* else *False*

        Note
        ----
            The function is blocking till the switch is successful. This can take many seconds.

        See Also
        --------
        :func:`ntixl2.xl2.safe_remove_mass_storage_device`

        """
        if self.device_status == 'SERIAL':
            mess = SYSTEM_MSDMAC()
            try:
                self.serial_message(mess)
            except serial.SerialException:
                print("Serial connection is broken.")
            success = False
            i=0
            time.sleep(4)
            while not (success or i > 20):
                i+=1
                success = (self.device_status == 'MASS')
                time.sleep(1)
            return success
        elif self.device_status == 'MASS':
            print("XL2 already in 'MASS' status ")
            return True

    def to_serial(self):
        """ Switch the device into SERIAL status.

        switch is done by umount and eject the  XL2 device.

        Returns
        -------
        bool
            if switch is successful *True* else *False*

        Note
        ----
            The function is blocking till the switch is successful. This can take many seconds.

        """
        if self.device_status == 'MASS':
            safe_remove_mass_storage_device(self.storageDev)
            success = False
            i=0
            time.sleep(2)
            while not (success or i > 20):
                i+=1
                success = (self.device_status == 'SERIAL')
                time.sleep(1)
            return success
        elif self.device_status == 'SERIAL':
            print(print("XL2 already in 'SERIAL' status "))
            return True


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
            print('device_status has to be MASS.')
        
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
            print('device_status has to be MASS.')

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
            print('device_status has to be MASS ')

    # def copy_file(self,filePath, wherePath = '/home/pi-rbl', filename = None):
    #     if self.device_status=='MASS':
    #         filePath = self.mountDir.joinpath(filePath)
    #         if not(filePath.exists() and filePath.is_file()):
    #             print('The specified file does not exists')
    #             return None
    #         wherePath=pathlib.Path(wherePath)
    #         if not wherePath.is_dir():
    #             wherePath.mkdir(parents=True)
    #         to = wherePath.joinpath(filePath.name) if filename is None else wherePath.joinpath(filePath.name)
    #         return shutil.copyfile(str(filePath), str(to), follow_symlinks=True)
    #     else:
    #         print('device_status has to be MASS.')

    def serial_message(self, message, wait = 1):
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
            self.conn.write((message.to_str()).encode('UTF-8'))
            # read returmn lines
            if message.RETURN is not None:
                self.conn._timeout = 5
                ret = []
                for i in range(message.return_lines()):
                    line = self.conn.readline().decode('UTF-8')
                    assert not line == ""
                    ret.append(line)
                return message.parse_answers(ret)
            else:
                # if message has no return raise error if there is a return
                self.conn._timeout = wait
                assert self.conn.readline().decode('UTF-8') == ""
                return None

    def select_profile(self, profile=6):
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

    def measurement_status(self):
        pass

### other functions

def find_xl2(linux = True, filter= "XL2"):
    """
    listet alle vorhandene serielle Ports welches Gerät Beschreibung enthalten die string  'filter'
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





