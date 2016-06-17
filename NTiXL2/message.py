from collections import namedtuple
import parse
import itertools
#from enum import Enum
#Option = Enum('RequiredOptions',['BASE', 'EAP', 'STIPA', 'REMOTE', 'SLI', 'CA', 'TA'])

ParamValue = namedtuple("ParamValue", ['value','description', 'requiredOption'])
ParamValue.__new__.__defaults__ = (None,'','BASE')

class categoricalParam(object):
    """define a parameter of type categorical"""
    def __init__(self, description, allowedValues=None, repeatAllowed = 1,
                 delimiter =" ",options=['BASE']):
        self.description = description
        self.options = options
        self.allowedValues = self._filter(allowedValues)
        self.repeatAllowed = repeatAllowed
        self.param_list = []
        self.delimiter = delimiter

    def _filter(self,allowedValues):
        return [av for av in allowedValues if av.requiredOption in self.options]

    def _match_value(self,value):
        try:
            index = [av.value for av in self.allowedValues].index(value)
        except ValueError:
            return False
        else:
            return index

    def append_param(self, value):
        if len(self.param_list) <= self.repeatAllowed:
            index = self._match_value(value)
            if type(index)==int:
                self.param_list.append(index)
            else:
                raise ValueError('Value {} is not allowed. See allowedValues attribute'.format(value))
        else:
            UserWarning('Max number of repeated parameter is {}'. format(self.repeatAllowed))

    def rm_param(self, last = False):
        if last:
            self.param_list=self.param_list[:-1]
        else:
            self.param_list = []

    def set_param(self, value):
        self.rm_param(last=True)
        self.append_param(value)

    def to_str(self):
        l = [self.allowedValues[i].value for i in self.param_list]
        if len(l):
            return self.delimiter.join(l)
        else:
            raise UserWarning('There are no param')
            return ''

    def to_list(self):
        l = [self.allowedValues[i].value for i in self.param_list]
        if len(l):
            return l
        else:
            raise UserWarning('There are no param')
            return []

class NumericalParam(object):
    """define a parameter of type numerical"""
    def __init__(self, description, min = None, max = None ):
        self.description = description
        self.allowedValues = {'min':min,'max':max}
        self.value = None

    def set_param(self, value):
        if value <= self.allowedValues['max'] and value >= self.allowedValues['min']:
            self.value = float(value)
        else:
            raise ValueError('Value {} is not allowed. See allowedValues attribute'.format(value))

    def rm_param(self, last=False):
        self.value=None

    def to_str(self):
        if self.value is not None:
            return str(self.value)
        else:
            raise UserWarning('There are no param')

###################################
########### Messages ##############
###################################

class Message(object):
    """Basic message class"""
    GROUP = ""
    AVAILABILITY = ['always']
    ROOT = ""
    EOL = "\r\n"
    HAS_RETURN = False
    RETURN = ""

    def to_str(self):
        return self.ROOT + self.EOL

    def return_lines(self):
        return 1

    def _parse(self, result):
        if result == self.EOL:
            return None
        else:
            p = parse.compile(self.RETURN + self.EOL)
            try:
                ret = p.parse(result).named
            except AttributeError as e:
                s = "not able to parse return string '{}'".format(result)
                raise AttributeError(s)
            else:
                return ret

    def parse_result_str(self, result):
        self._parse(result)

class MessageWithParam(Message):
    """Basic message class with parameter"""
    PARAM_TYPE = None
    PARAM_NAME = ''
    ALLOWED_VALUES = None
    REPEAT_PARAM = 1
    def __init__(self):
        if self.PARAM_TYPE == 'categorical':
            self.param = categoricalParam(self.PARAM_NAME, allowedValues = self.ALLOWED_VALUES,
                                          repeatAllowed = self.REPEAT_PARAM)
        elif self.PARAM_TYPE == float:
            self.param = NumericalParam(self.PARAM_NAME,self.ALLOWED_VALUES['min'],
                                        self.ALLOWED_VALUES['max'])

    def allowed_param_values(self, short=True):
        if short and self.PARAM_TYPE=="categorical":
            return [p.value for p in self.param.allowedValues]
        else:
            return self.param.allowedValues

    def set_param(self, value):
        self.param.set_param(value)

    def rm_param(self, last=False):
        self.param.rm_param(last)

    def to_str(self):
        param = self.param.to_str()
        return self.ROOT.format(param) + self.EOL

class MessageWithParams(MessageWithParam):
    """Basic message class with  repeated parameter"""
    def append_param(self, value):
        self.param.append_param(value)

########################
# Device Status Messages

class QUERY_IDN(Message):
    """Reads the unique identification of the XL2."""
    GROUP = "DeviceStatus"
    ROOT = "*IDN?"
    HAS_RETURN = True
    RETURN= "{manufacturer},{unit},{serialNumber},{FW_Version}"


class RESET(Message):
    """ Executes a device reset, and should be the first command when starting a remote
session to ensure that all XL2 settings make sense for remote measuring.

    It is highly recommended to execute this command first to avoid unwanted side effects.
The RST command:
-  clears the error queue
-  stops any running measurement
-  stops any running script
-  exits any active profile
-  selects the SLMeter function
-  sets the following parameters
-  Append mode: OFF
-  Auto save: OFF
-  Logging: OFF
-  Events:  OFF
-  Timer mode: CONTINUOUS
-  Range: MID
-  RMS/THDN Filter: Z-WEIGHTED
-  Input: XLR
-  Phantom Power:  ON
-  RTA S- urce: LZF
-  RTA Resolution: TERZ
-  locks the keyboard
-  sets the precision of queried floating-point numbers to 'LCD'
    """
    GROUP = "DeviceStatus"
    ROOT = "*RST"
    HAS_RETURN = False

##########################
# Initialization Messages
class INITIATE(MessageWithParam):
    """Starts/Stops a measurement"""
    GROUP = "InitiateSubsystem"
    AVAILABILITY = ["SLM", "FFT", "1/12Oct"]
    ROOT = "INIT {}"
    HAS_RETURN = False
    PARAM_NAME = "action"
    PARAM_TYPE = "categorical"
    ALLOWED_VALUES = [ParamValue("START","start a measurement","BASE"),
                      ParamValue("STOP","stop a measurement","BASE")]
      
    @classmethod
    def START(cls):
        instance = cls()
        instance.set_param("START")
        return instance
    
    @classmethod
    def STOP(cls):
        instance = cls()
        instance.set_param("STOP")
        return instance

class QUERY_INITIATE_STATE(Message):
    """Queries the run status of a measurement
Answer:
 [STOPPED|FROZEN|SETTLING|RUNNING|PAUSED]
    """
    GROUP = "InitiateSubsystem"
    ROOT = "INIT:STATE?"
    HAS_RETURN = True
    RETURN = "{state}"

######################
# Measurement Messages
FUNCTIONS = ["SLMeter","FFT","RT60","Polarity","Delay","RMS/THD",
             "N.Rating","Scope","1/12Oct","STIPA","Calibrte","System"]

class MEASURE_FUNCTION(MessageWithParam):
    """Defines the active measurement function"""
    GROUP = "Measurement"
    ROOT = "MEAS:FUNCTION {}"
    HAS_RETURN = False
    PARAM_NAME = 'function'
    PARAM_TYPE = 'categorical'
    ALLOWED_VALUES = [ParamValue(func, '' , 'BASE') for func in FUNCTIONS]

class QUERY_MEASURE_FUNCTION(Message):
    """Queries the active measurement function"""
    GROUP = "Measurement"
    ROOT = "MEAS:FUNCTION?"
    HAS_RETURN = True
    RETURN = "{function}"

class MEASURE_INITIATE(Message):
    """
    Triggers a measurement
    """
    GROUP = "Measurement"
    ROOT = "MEAS:INIT"
    HAS_RETURN = False

class QUERY_MEASURE_TIMER(Message):
    """Queries the actual measurement timer value"""
    GROUP = "Measurement"
    ROOT = "MEAS:TIME?"
    HAS_RETURN = True
    RETURN = "{t:g} sec, {status}"
    AVAILABILITY = ["SLM"]

class QUERY_MEASURE_DTTIME(Message):
    """Queries the time period used for the calculation of dt values. The value is active as long
as the measurement is RUNNING, and is reset after each INIT:MEAS or INIT START
command."""
    GROUP = "Measurement"
    AVAILABILITY = ["runningSLM"]
    ROOT = "MEAS:DTTI?"
    HAS_RETURN = True
    RETURN = "{dt:g} sec, {status}"


# QUERY_MEAS_SLM_123 param
STATISTICS = [['L{}S', 'Sound pressure level {} weigthed SLOW(1. sec) time average', 'BASE'],
['L{}SMAX', '', 'BASE'],
['L{}SMIN', '', 'BASE'],
['L{}F', 'Sound pressure level {} weigthed FAST(0.125 sec) time average', 'BASE'],
['L{}FMAX', '', 'BASE'],
['L{}FMIN', '', 'BASE'],
['L{}EQ', '', 'BASE'],
['L{}PK', '', 'BASE'],
['L{}PKMAX', '', 'BASE'],
['L{}AEQt', '', 'BASE']]
STATISTICS = [[s.format(w) for s in p] for p,w in itertools.product(STATISTICS,'ACZ')] + [['k1', '', 'BASE'],['k2', '', 'BASE']]

class QUERY_MEAS_SLM_123(MessageWithParams):
    GROUP = "Measurement"
    AVAILABILITY = ["SLM"]
    ROOT = "MEAS:SLM:123? {}"
    HAS_RETURN = True
    RETURN= "{level:g} dB, {status}"
    PARAM_TYPE = "categorical"
    PARAM_NAME = "noiseStatistics"
    ALLOWED_VALUES = [ParamValue(*p) for p in STATISTICS]

    def return_lines(self):
        return len(self.param.to_list())

    def parse_result_str(self, result):
        ret = {}
        for p,v in zip(self.param.to_list(), result):
            ret[p] = self._parse(v)
        return ret

# input messages
class INPUT_SELECT(Message):
    pass

class QUERY_INPUT_SELECT(Message):
    pass

class INPUT_RANGE(Message):
    pass

class QUERY_INPUT_RANGE(Message):
    pass

class INPUT_PHANTOM(Message):
    pass

class QUERY_INPUT_PHANTOM(Message):
    pass

####################
# calibrate messages

class QUERY_CALIBRATE_MIC_TYPE(Message):
    """Queries the microphone type recognized by the ASD (A Automatic S Sensor D Detection)
system.

Details:
If no ASD microphone is currently connected, the command always returns noASD.
In contrast, the command CALIB:MIC:SENS:SOURce returns the ASD microphone that
was last connected, as long as the microphone sensitivity has not been changed
manually or by remote command.
"""
    GROUP = "Calibrate"
    ROOT = "CALI:MIC:TYPE?"
    HAS_RETURN = True
    RETURN = "{micType}"

class  QUERY_CALIBRATE_MIC_SENS_SOURCE(Message):
    """Queries the source of the sensitivity value.
Answer:
[PLEASE CALIBRATE|USER CALIBRATED|MANUALLY|M2210 USER|M2210 FACTORY|M2210 CAL.CENTER|
M4260 USER|M4260 FACTORY|M4260 CAL.CENTER]

Details:
Returns the ASD microphone that was last connected as long as the microphone
sensitivity has not been changed manually or by remote command.
PLEASE CALIBRATE is returned when the sensitivity has never been set since the last
factory default setup.
"""
    GROUP = "Calibrate"
    ROOT = "CALI:MIC:SENS:SOUR?"
    HAS_RETURN = True
    RETURN = "{micSensytivitySource}"

class CALIBRATE_MIC_SENS_VALUE(MessageWithParam):
    """Defines the microphone sensitivity in V/Pa.
    Details:
    Command is not accepted when an ASD microphone is connected.
    """
    GROUP = "Calibrate"
    ROOT = "CALI:MIC:SENS:VALU {}"
    HAS_RETURN = False
    PARAM_NAME = "micSensitivity"
    PARAM_TYPE = float
    ALLOWED_VALUES = {'min':100e-6,'max':9.99}

class QUERY_CALIBRATE_MIC_SENS_VALUE(Message):
    """Queries the microphone sensitivity in V/Pa .
Answer:
V,OK  float  100e-6 to 9.99 V/Pa
"""
    GROUP = "Calibrate"
    ROOT = "CALI:MIC:SENS:VALU?"
    HAS_RETURN = True
    RETURN = "{micSensitivityValue:g} V,{status}"

##################
# System messages
class QUERY_SYSTEM_ERROR(Message):
    """Queries the error queue"""
    GROUP = "System"
    ROOT = "SYST:ERRO?"
    HAS_RETURN = True
    RETURN= "{errList}"
    RETURN_translator ={-350:"Error queue full - at least 2 errors lost",
                       -115:  "Too many parameters in command",
                       -113:  "Invalid command",
                       -112:  "Too many characters in one of the command parts",
                       -109:  "Missing command or parameter",
                       -108:  "Invalid parameter",
                        0:  "no error (queue is empty)",
                        1:  "Command too long; too many characters without new line",
                        2:  "UNEXPECTED_PID",
                        3:  "DSP_TIMEOUT",
                        4:  "Changing microphone sensitivity is not possible when an ASD microphone is connected to the XL2",
                        5:  "Parameter not available, license not installed",
                        6:  "dt value does not exist for this parameter",
                        7:  "Parameter is not available in the current measurement function",
                        8:  "Unspecified DSP error",
                        9:  "Not valid, measurement is running"}

    def parse_result_str(self, result):
        ret = self._parse(result)["errList"]
        err_list = [int(i.strip()) for i in ret.split(",")]
        return  [(err, self.RETURN_translator.get(err)) for err in err_list ]

class SYSTEM_KEY(MessageWithParams):
    """Simulates a key stroke on the XL2"""
    GROUP = "System"
    ROOT = "SYST:KEY {}"
    HAS_RETURN = True
    RETURN= "{status}"
    PARAM_TYPE = "categorical"
    ALLOWED_VALUES = [ParamValue(key,'','BASE') for key in ["ESC","NEXT","FNEXT","PREV","FPREV","ENTER","PAGE","START",
                                                      "PAUSE","SPEAKER","LIMIT","LIGHT"]]
    REPEAT_PARAM = 30

class SYSTEM_KLOCK(MessageWithParam):
    """Locks the keyboard of the XL2"""
    GROUP = "System"
    ROOT = "SYST:KLOC {}"
    HAS_RETURN = False
    PARAM_TYPE = "categorical"
    ALLOWED_VALUES = [ParamValue("ON","Keyboard is locked","BASE"), ParamValue("OFF","Keyboard is unlocked","BASE")]
    PARAM_NAME = "keyStroke"

class QUERY_SYSTEM_KLOCK(Message):
    """Queries the key lock status
Answer: [ON|OFF]"""
    GROUP = "System"
    ROOT = "SYST:KLOC?"
    HAS_RETURN = True
    RETURN = "{keyLock}"

class QUERY_SYSTEM_OPTIONS(Message):
    """Queries the installed options.
Answer: list of installed options
    """
    GROUP = "System"
    ROOT = "SYST:OPTI?"
    HAS_RETURN = True
    RETURN = "{optList}"

    def parse_result_str(self, result):
        ret = self._parse(result)["optList"]
        return  [i.strip() for i in ret.split(",")]

class SYSTEM_MSDMAC(Message):
    """
Switches the XL2 to the USB mass storage mode for Mac and Linux

Answer: None, connection is closed

Use this Command on Mac and Linux instead of “SYSTem:MSD”, otherwise MSD will
timeout after 2 minutes and the XL2 returns to COM mode.
After sending this command, the XL2 drops the COM connection (no more remote
commands are possible) and switches to mass storage mode. The host then has full
access to the data stored on the SD card of the XL2.
To return to COM mode eject the XL2 drive from the host computer.
Attention: If you unmount the XL2 drive by the host, the XL2 will not return to COM
mode
"""
    GROUP = "System"
    ROOT = "SYST:MSDMAC"