from collections import namedtuple
from enum import Enum
MyStruct = namedtuple("MyStruct", ['a','b'])

DeviceStatus
INITIATE
MEASURE
IMPUT
CALIBRATE
SYSTEM

## Serial messages interface

class Param(object):
    NAME = ""
    def __init__(self, parent):
        self._parent = parent
        self._value = None
    @property
    def value(self):
        return self._value
    @property
    def name(self):
        return self.NAME

    def is_set(self):
        return  not self._value == None

class Action(Param):
    NAME = 'action'

    @property
    def START(self):
        self._value = "START"
        return self._parent
    @property
    def STOP(self):
        self._value = "STOP"
        return self._parent

class Weight(Param):
    NAME = 'Weight'

    @property
    def A(self):
        self._value = "A"
        return self._parent
    @property
    def C(self):
        self._value = "C"
        return self._parent
        @property
    def Z(self):
        self._value = "Z"
        return self._parent

class Result(Param):
    NAME = 'Result'

    @property
    def LxS(self):
        self._value = "L{}S"
        return self._parent
    @property
    def LxSMAX(self):
        self._value = "L{}SMAX"
        return self._parent



class Message(object):
    ROOT = ""
    PARAM = None

    def to_list(self):
        l = [("root",self.ROOT)]
        for par in self._param:
            l.append((par.name,par.value))
        return l

    def to_serial(self):
        return (str(self) + '\n').encode('UTF_8')

    def parse_serial_return(self, bytes):
        return bytes.decode('UTF-8')
    def valid(self):
        pass
    def reset(self):
        pass
    def __str__(self,*args,**kwargs):
        values = [v for n,v in self.to_list()]
        return " ".join(values)

class INIT(Message):
    ROOT= "INIT"
    PARAM = namedtuple('InitParam',("action"))
    def __init__(self):
        self._param = self.PARAM(Action(self))
    @property
    def action(self):
        return self._param.action



class MEASureSLM123(Message):
    ROOT= "MEASure:SLM:123?"
    PARAM = namedtuple('MEASure:SLM:123?Param',('p1','p2'))
    def __init__(self):
        self._param = self.PARAM(Action(self))
    @property
    def action(self):
        return self._param.action


###########################

class XL2(Object):
"""
represent
"""
    def __init__(self, name, ykush_port):
        self.ykush_port = ykush_port
        self.name = Name
        #self.mountDir = None
        self.conn = Serial.connection()

    @property
    def connection_status(self):
        status = 0# ['SERIAL, 'MASS', 'NODEVICE']
        return status
        
    @property
    def serial_port(self);
        if self.connection_status == 'SERIAL':
            return port
            
    @property
    def mass_device(self);
        if self.connection_status=='MASS':
            return port
        
    def to_MASS(self):
        if self.connection_status == 'SERIAL':
            try:
                mess = "SYST:MSDMAC"
                r = self._send_msg(mess)
            except:
                pass
        elif False:
            pass
        return self.connection_status == 'MASS'
    
    def to_SERIAL(self):
        if self.connection_status == 'MASS':
            try:
                pass
            except:
                print()
        return  self.connection_status == 'SERIAL'
    
    @property
    def serial_conn_status(self):
        pass
         
    def build_serial_conn(self, force):
        if self.connection_status == "MASS" and force:
            self.to_SERIAL():
        if self.connection_status == "SERIAL":
            if self.serial_conn_status:
                print('already connected')
            else:
                try:
                    self.conn.connect(self.serial_port)
                except:
                    print('error')
        return self.serial_conn_status 
    
    def _kill_serial_connecction(self):
        pass
        
    @property
    def mount_status(self):
        pass
    
    def mount(self, mountDir = "/media/NTIAUDIOXL2", force = False):
        if self.connection_status == 'SERIAL' and force:
            success = self.to_MASS()
        if self.connection_status=='MASS':
            if mountDir != self.mountDir :
                self.unmount()
                try:
                    self.mountDir = self._mount(mountDir)
                except:
                    self.mountDir = None
                    
        return self.mount_status()
    
    def _mount(mountDir):
        import os
        import subprocess
        out =subprocess.check_output(["sudo","blkid","-t", 'LABEL="{}"'.format(self.name),"-o" , "value"])
        _, UUID, format = out.decode('UTF-8').split('\n')[1:-1]
        if not os.path.isdir(mountDir):
            subprocess.Popen(["sudo","mkdir", mountDir])
        subprocess.Popen(["sudo","mount","-t", format ,"-U" , UUID, mountDir])
        return mountDir
        
    def _unmount(self):
        if self.mountDir:
            #unmount(self.path)
            self.mountDir = None
            success =True
        else:
            print('nothing to unmount')
            success = False
        return success
    
    #other functions
    def measurement_status(self):
            self.serial_message(mess)
    
    def serial_message(mess):
        return mess
        
    def list_data(self,path):
        pass
    
    def get_data(self,data_path):
        pass
    
    def rm(self, path):
        recursive
        pass
    
##Tools linux specific!

def find_serial_port():
    pass
    
def find_mass_device()
    pass
    
def find_ykush_port():
    pass

def ykush_shutdown_port():
    pass
    
def logger_data_parser(data)
    return {}