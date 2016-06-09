import serial
import os
import stat
import time
import subprocess

##func
def safe_remove_MASS():
    subprocess.Popen(["safe_rm_XL2-sd"]).wait()

def find_xl2( linux = False, filter= "XL2"):
    comports = list(list_ports.comports())
    attr = ['device', 'description','pid','vid','serial_number', 'product','manufacturer','interface','hwid']
    devices = []
    for p in comports:
        if linux:
            attribute = {a : getattr(p,a) for a in attr}
            #q = any([filter in v for k,v in attribute.items() if type(v)=='str'])
            #print('Device: ', attribute['description'], ', filter: ', q)
            print
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

##class

class XL2(object):
    """
    represent
    """
    def __init__(self, serialDev='/dev/XL2', storageDev = '/dev/XL2-sd', mountDir = '/media/XL2-sd'):
        self.serialDev = serialDev
        self.storageDev = storageDev
        self.mountDir = mountDir
        try:
            self._init_serial_conn()
        except serial.SerialException:
            pass

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
            self.conn.isWaiting()
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
                return 'MASS'
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
        if self.device_status == 'SERIAL':
            try:
                mess = "SYST:MSDMAC"
                r = self.serial_message(mess)
            except:
                pass
        done = False
        i=0
        while done or  i > 4:
            i+=1
            done = (self.device_status == 'MASS')
            time.sleep(0.5)
        return done

    def to_SERIAL(self):
        if self.device_status == 'MASS':
            safe_remove_MASS()
        done = False
        i=0
        while done or i > 4:
            i+=1
            done = (self.device_status == 'SERIAL')
            time.sleep(0.5)
        return done

    def _mount_status(self):
                pass

    def measurement_status(self):
        pass

    def serial_message(mess):
        if self.device_status() == 'SERIAL':
            self.conn.write((mess + "\n").encode('UTF-8'))
            l = self.conn.readline()
        if len(l):
            return l.decode('UTF-8')
        else:
            return l
        
    def list_data(self,path):
        pass
    
    def get_data(self,data_path):
        pass
    
    def rm(self, path):
        pass

####
