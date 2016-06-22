"""The xl2.py module implement the XL2 object.

Notes
-----

The implementation is for linux systems with following requirements:

-The xl2 device name has to be:

    - Fixed device name (`XL2`) if connected as serial device
    - Fixed device name (`XL2-sd`) if connected as mass storage device
    - automount to fixed path (`/media/XL2-sd`) if device connected as mass storage

-Use udev rules to achieve this behaviour

The mounting directory has to

"""

import os
import time
import subprocess
import pathlib,shutil
import psutil#, pyudev
import serial
from serial.tools import list_ports
from .message import SYSTEM_MSDMAC,RESET, SYSTEM_KEY, QUERY_SYSTEM_ERROR, QUERY_IDN, SYSTEM_KLOCK, QUERY_INITIATE_STATE


##func
def safe_remove_XL2_MASS():
    """Ummount and eject device"""

    subprocess.Popen(["safe_rm_XL2-sd"]).wait()

class XL2SLM(object):
    """
    The XL2 device
    TODO:
    - implement system usiing pyudev  uuid, and not symbolic
    - implement system with pyudev using Monitor and observer
    """

    def __init__(self, serialDev='/dev/XL2', storageDev = '/dev/XL2-sd', mountDir = '/media/XL2-sd'):
        self.serialDev = serialDev
        self.storageDev = storageDev
        self.mountDir = pathlib.Path(mountDir)
        self.device_status

    @property
    def device_status(self):
        """
        check device status and return one of the following device status:
         - SERIAL
         - MASS
         - MASS_NOT_MOUNT
         - NO_DEVICE
         - ERROR
        :return: str status

        """
        try:
            self.conn.inWaiting()
        except:
            dev = self._which_device()
            if dev == self.serialDev:
                try :
                    self._init_serial_conn()
                except serial.SerialException:
                    return 'SERIAl_ERROR'
                else:
                    return 'SERIAL'
            elif dev == self.storageDev:
                return 'MASS'
                # mntStatus = self.mount_status()#{'mounted':True,'path':self.mountDir}#
                # if mntStatus['mounted'] == True and mntStatus['path'] == str(self.mountDir):
                #     return 'MASS'
                # else:
                #     print(mntStatus)
                #     return 'MASS_NOT_MOUNT'
            else:
                return 'NO_DEVICE'
        else:
            return 'SERIAL'

    def _init_serial_conn(self):
        try:
            self.conn = serial.Serial(self.serialDev, baudrate=9600, timeout=10)
        except serial.SerialException as e:
            print('Not able to serial connect device {}'.format(self.serialDev))
            raise e
        else:
            print('XL2 in serial mode')

    def _which_device(self):
        # is serial device there?
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

    def to_MASS(self):
        """ Switch the device to MASS status sending a serial message. Return True if succesful."""
        if self.device_status == 'SERIAL':
            mess = SYSTEM_MSDMAC()
            try:
                self.serial_message(mess)
            except serial.SerialException:
                print("Seial connection is broken.")
        done = False
        i=0
        time.sleep(4)
        while not (done or i > 20):
            i+=1
            done = (self.device_status == 'MASS')
            time.sleep(1)
        return done

    def to_SERIAL(self):
        """ Switch the device to SERIAL status  by umount and eject the device. Return True if succesful."""
        if self.device_status == 'MASS':
            safe_remove_XL2_MASS()
        done = False
        i=0
        time.sleep(2)
        while not (done or i > 10):
            i+=1
            done = (self.device_status == 'SERIAL')
            time.sleep(1)
        return done

    # def mount_status(self):


    def memory_usage(self):
        if self.device_status=='MASS':
            return shutil.disk_usage(self.mountDir.as_posix())
        else:
            print('device_status has to be MASS.')
        
    def list_files(self, relPath='', filter = '*'):
        if self.device_status=='MASS':
            path = self.mountDir.joinpath(relPath)
            if path.exists():
                return [str(p) for p in path.glob(filter) if p.is_file()]
            else:
                print('The specified path does not exists')
                return None
        else:
            print('device_status has to be MASS.')

    def list_dir(self, relPath='', filter = '*'):
        if self.device_status=='MASS':
            path = self.mountDir.joinpath(relPath)
            if path.exists():
                path.glob(filter)
                return [str(p) for p in path.glob('*') if p.is_dir()]
            else:
                print('The specified path does not exists')
                return None
        else:
            print('device_status has to be MASS ')

    def copy_file(self,filePath, wherePath = '/home/pi-rbl', filename = None):
        if self.device_status=='MASS':
            filePath = self.mountDir.joinpath(filePath)
            if not(filePath.exists() and filePath.is_file()):
                print('The specified file does not exists')
                return None
            wherePath=pathlib.Path(wherePath)
            if not wherePath.is_dir():
                wherePath.mkdir(parents=True)
            to = wherePath.joinpath(filePath.name) if filename is None else wherePath.joinpath(filePath.name)
            return shutil.copyfile(str(filePath), str(to), follow_symlinks=True)
        else:
            print('device_status has to be MASS.')
    
    def rm_file(self, filePath):
        if self.device_status=='MASS':
            filePath = self.mountDir.joinpath(filePath)
            if not(filePath.exists() and filePath.is_file()):
                print('The specified file does not exists')
                return None
            pass
        else:
            print('device_status has to be MASS.')

    def serial_message(self, message, check_error = False, wait = 1):
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
                return message.parse_result_str(ret)
            else:
                # if message has no return raise error if there is a return
                self.conn._timeout = wait
                assert self.conn.readline().decode('UTF-8') == ""
                return None

    def select_profile(self, profile=6):
        """ Reset device and load profile number 'profile'"""
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
        time.sleep(4)

    def klock(self, locked = False):
        if locked:
            self.serial_message(SYSTEM_KLOCK.ON())
        else:
            self.serial_message(SYSTEM_KLOCK.OFF())

    def check_errors(self):
        return self.serial_message(QUERY_SYSTEM_ERROR())

    def reset(self):
        self.serial_message(RESET())

    def identification(self):
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

def force_unplug_USB(ykushPort = 1, ykushPath = '/home/pi-rbl/XL2/YKUSH_V1.4.1/ykush'):
    """force power off and power on of a port on the Ykush USB-hub"""
    # power off USB port
    subprocess.call(ykushPath + "-d {}".format(ykushPort))
    # power on USB port
    subprocess.call(ykushPath + "-u {}".format(ykushPort))
    # list device files
    print(subprocess.call("ls -l /dev"))

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

