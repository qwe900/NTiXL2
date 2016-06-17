from .message import SYSTEM_MSDMAC, SYSTEM_KEY, QUERY_SYSTEM_ERROR, QUERY_IDN
import serial
from serial.tools import list_ports
import os
import psutil, pyudev
import pathlib,shutil
import time
import subprocess


##func
def safe_remove_XL2_MASS():
    subprocess.Popen(["safe_rm_XL2-sd"]).wait()

class XL2(object):
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
        stat = self.device_status
        print(stat)

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
                    return 'ERROR'
                else:
                    return 'SERIAL'
            elif dev == self.storageDev:
                mntStatus = self.mount_status()#{'mounted':True,'path':self.mountDir}#
                if mntStatus['mounted'] == True and mntStatus['path'] == str(self.mountDir):
                    return 'MASS'
                else:
                    print(mntStatus)
                    return 'MASS_NOT_MOUNT'
            else:
                return 'NO_DEVICE'
        else:
            return 'SERIAL'

    def _init_serial_conn(self):
        try:
            self.conn = serial.Serial(self.serialDev, baudrate=9600, timeout=1)
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
        """
        switch the device to MASS status. Return True if succesful
        :return:
        """
        if self.device_status == 'SERIAL':
            try:
                mess = SYSTEM_MSDMAC()
                r = self.serial_message(mess)
            except:
                pass
        done = False
        i=0
        while not (done or i > 6):
            i+=1
            done = (self.device_status == 'MASS')
            time.sleep(1)
        return done

    def to_SERIAL(self):
        """
        switch the device to SERIAL status. Return True if succesful
        :return:
        """
        if self.device_status == 'MASS':
            safe_remove_XL2_MASS()
        done = False
        i=0
        while not (done or i > 4):
            i+=1
            done = (self.device_status == 'SERIAL')
            time.sleep(0.5)
        return done

    def mount_status(self):
        disk = None
        context = pyudev.Context()
        for i,d in enumerate(psutil.disk_partitions()):
            try:
                device = pyudev.Device.from_device_file(context,d.device)
            except pyudev.DeviceNotFoundByFileError:
                pass
            else:
                links = list(device.device_links)
                if self.storageDev in links:
                    disk = d
                    #print("Device 'XL2-sd'->{} , present.".format(d.device))
        if disk is not None:
            return {'mounted': True, 'path':disk.mountpoint, 'device_file':disk.device}
        else:
            return {'mounted': False, 'path':''}

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

    def measurement_status(self):
        pass

    def serial_message(self, mess, check_error = False):
        if self.device_status == 'SERIAL':
            self.conn.write((mess.to_str()).encode('UTF-8'))
            ret = [(i,self.conn.readline().decode('UTF-8')) for i in mess.return_lines() ]
            return mess.parse_result_str(ret)

    def check_errors(self):
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