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

