"""The message.py module implement the command structure for the serial communication with the XL2 sound level meter.
For more information about the remote measurement option of the XL2 device see
the manual_ .

.. _manual: http://www.nti-audio.com/Portals/0/data/en/XL2-Remote-Measurement-Manual.pdf

Note
----

- There are **Query** messages by which the XL2 perform an **answers** and messages without an answers.

- There are messages with parameter and messages without parameters.

- A message has always a root message string. If the message has parameter the root string is followed by a \
  list (normally one) of parameter strings separated by spaces.

- XL2  root messages and parameter are not case sensitive

- The different types of messages are build on top of the **Basic message classes**

Warnings
-----
- Only a subset of the  XL2 messages are implemented
- Some messages are not complete
- The messages are not tested

Todo
----
- Implement all messages: Input messages
- Tests

"""

from collections import namedtuple
import itertools
import parse

########### Messages ##############

class Message(object):
    """Basic XL2 serial message class

    The class has methods for the creation (:meth:`to_str`) of XL2 messages and methods\
    for parsing (:meth:`parse_answers`) the relative XL2 answers.

    Note
    -----
    This class is for messages without params

    Attributes
    ----------
    GROUP : str
        Message group
    AVAILABILITY : str
        Message availability
    ROOT : str
        Message root string
    EOL : str
        Serial communication end of line
    RETURN : str
        XL2 answers string template. `None` if message has no answers

    """
    # parameter Group
    GROUP = ""
    AVAILABILITY = ['always']
    # Serial message string
    ROOT = ""
    # serial message eind of line
    EOL = "\r\n"
    # return line format
    RETURN = None

    def to_str(self):
        """Return the serial message

        Returns
        -------
        str
            serial message string

        """
        return self.ROOT + self.EOL

    def return_lines(self):
        """Return the expected number of return lines of the message."""
        return 1

    def _parse(self, line):
        """Parse answers line according to RETURN  class attribute."""
        if self.RETURN is not None:
            p = parse.compile(self.RETURN + self.EOL)
            try:
                ret = p.parse(line).named
            except AttributeError as e:
                s = "not able to parse return string '{}'".format(line)
                raise AttributeError(s)
            else:
                return ret

    def parse_answers(self, lines):
        """Parse XL2 answers.

        Parameters
        ----------
        lines : list
            list containing XL2 answers lines to message

        Returns
        -------
        dict
            dict containing contents (key, value) of XL2 answers
        """
        assert len(lines) == 1
        line = lines[0]
        return self._parse(line)


############
# Parameters
############

# Categorical parameter values
ParamValue = namedtuple("ParamValue", ['value', 'description', 'requiredOption'])
ParamValue.__new__.__defaults__ = (None, '', 'BASE')


class CategoricalParam(object):
    """Serial message parameter of type categorical.

    Serial messages have often parameters of categorical type. eg. there is a finite set of allowed values.

    Note
    -----
    Repetitions are allowed

    """

    def __init__(self, description, allowedValues=None, repeatAllowed=1,
                 delimiter=" ", options=['BASE']):
        self.description = description
        self.options = options
        self.allowedValues = self._filter(allowedValues)
        self.repeatAllowed = repeatAllowed
        """ int : Max length of parameter list"""
        self.param_list = []
        self.delimiter = delimiter

    def _filter(self, allowedValues):
        return [av for av in allowedValues if av.requiredOption in self.options]

    def _match_value(self, value):
        try:
            index = [av.value for av in self.allowedValues].index(value)
        except ValueError:
            return False
        else:
            return index

    def append_param(self, value):
        """Append parameter to parameter list."""
        if len(self.param_list) <= self.repeatAllowed:
            index = self._match_value(value)
            if type(index) == int:
                self.param_list.append(index)
            else:
                raise ValueError('Value {} is not allowed. See allowedValues attribute'.format(value))
        else:
            raise UserWarning('Max number of repeated parameter is {}'.format(self.repeatAllowed))

    def rm_param(self, last=False):
        """Remove parameters from list.

        Parameters
        ----------
        last : bool
            If  True remove last element from parameter list else remove all elements
        """
        if last:
            self.param_list = self.param_list[:-1]
        else:
            self.param_list = []

    def set_param(self, value: str):
        """ Set parameter or replace last parameter in parameter list."""
        self.rm_param(last=True)
        self.append_param(value)

    def to_str(self):
        """Translate parameter list to string for serial communication"""
        l = [self.allowedValues[i].value for i in self.param_list]
        if len(l):
            return self.delimiter.join(l)
        else:
            raise UserWarning('There are no param')

    def parameter_list(self):
        """Return list of parameter names."""
        l = [self.allowedValues[i].value for i in self.param_list]
        if len(l):
            return l
        else:
            raise UserWarning('There are no param')


class NumericalParam(object):
    """Serial message parameter of type numerical"""

    def __init__(self, description, min=None, max=None):
        self.description = description
        self.allowedValues = {'min': min, 'max': max}
        self.value = None

    def set_param(self, value):
        """Set or overwrite parameter value"""
        if value <= self.allowedValues['max'] and value >= self.allowedValues['min']:
            self.value = float(value)
        else:
            raise ValueError('Value {} is not allowed. See allowedValues attribute'.format(value))

    def rm_param(self, last=False):
        """ Remove parameter value."""
        self.value = None

    def to_str(self):
        """Translate parameter list to string for serial communication"""
        if self.value is not None:
            return str(self.value)
        else:
            raise UserWarning('There are no param')


class MessageWithParam(Message):
    """XL2 serial message class for messages with  single param.

    Implement XL2  serial messages which need single parameter.

    Attributes
    ----------
    PARAM_TYPE : str
        string  describing parameter type. Should be {'categorical'|'numerical'}
    PARAM_NAME : str
        parameter name
    ALLOWED_VALUES : list
        list (of type : paramValues) values of allowed message parameter
    REPEAT_PARAM : int
        number of time which is possible to repeat parameter in a message string
    """

    # type of param; categorical or numerical
    PARAM_TYPE = None
    PARAM_NAME = ''
    # list of allowed values for categorical parameter (of type:paramValues) or  min and max value fr numerical param
    ALLOWED_VALUES = None
    # number of repetition allowed
    REPEAT_PARAM = 1

    def __init__(self):
        if self.PARAM_TYPE == 'categorical':
            self.param = CategoricalParam(self.PARAM_NAME, allowedValues=self.ALLOWED_VALUES,
                                          repeatAllowed=self.REPEAT_PARAM)
        elif self.PARAM_TYPE == 'numerical':
            self.param = NumericalParam(self.PARAM_NAME, self.ALLOWED_VALUES[0], self.ALLOWED_VALUES[1])
        else:
            raise ValueError('Parameter type is not correct.')

    def to_str(self):
        """Return the serial message

        Returns
        -------
        str
            serial message string

        """
        param = self.param.to_str()
        return self.ROOT.format(param) + self.EOL

    def allowed_param_values(self, short=True):
        """Return list of allowed parameter strings."""
        if short and self.PARAM_TYPE == "categorical":
            return [p.value for p in self.param.allowedValues]
        else:
            return self.param.allowedValues

    def set_param(self, value):
        """Set or overwrite parameter value

        Note
        -----
        value string is converted to uppercase

        Parameters
        ----------
        value : str
            parameter value

        """
        self.param.set_param(value.upper())

    def rm_param(self, last=False):
        """Remove parameter value.

        Parameters
        ----------
        last : bool
            if  False remove all parameters from list else remove the last one.
        """
        self.param.rm_param(last)


class MessageWithParams(MessageWithParam):
    """XL2 serial message class for messages with repeated parameter"""

    def append_param(self, value):
        """Append parameter to parameter list.

        Note
        -----
        value string is converted to uppercase

        Parameters
        ----------
        value : str
            parameter value
        """
        self.param.append_param(value)

########################
# Debug Mesages
class ECHO(Message):
    """Returns the 'deb' after the command including separators. It is for debugging purpose only.

    Note
    ----
    this implementation is not the same as the one in the manual_ .

    """
    GROUP = "Debug"
    ROOT = "ECHO deb"
    RETURN = "{string}"

########################
# Device Status Messages

class QUERY_IDN(Message):
    """Query the unique identification of the XL2."""

    GROUP = "DeviceStatus"
    ROOT = "*IDN?"
    RETURN = "{manufacturer},{unit},{serialNumber},{FW_Version}"

class RESET(Message):
    """ Executes a device reset.

    *The RST command:*
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

    Note
    ----
    Should be the first command when starting a remote session to ensure that all XL2 settings make sense for remote
    measuring. It is highly recommended to execute this command first to avoid unwanted side effects.

    """

    GROUP = "DeviceStatus"
    ROOT = "*RST"


##########################
# Initialization Messages

class INITIATE(MessageWithParam):
    """Starts/Stops a measurement"""

    GROUP = "InitiateSubsystem"
    AVAILABILITY = ["SLM", "FFT", "1/12Oct"]
    ROOT = "INIT {}"
    PARAM_NAME = "action"
    PARAM_TYPE = "categorical"
    ALLOWED_VALUES = [ParamValue("START", "start a measurement", "BASE"),
                      ParamValue("STOP", "stop a measurement", "BASE")]

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
    """Queries the run status of a measurement.

    status: [STOPPED|FROZEN|SETTLING|RUNNING|PAUSED]
    """

    GROUP = "InitiateSubsystem"
    ROOT = "INIT:STATE?"
    RETURN = "{state}"


######################
# Measurement Messages
FUNCTIONS = ["SLMeter", "FFT", "RT60", "Polarity", "Delay", "RMS/THD",
             "N.Rating", "Scope", "1/12Oct", "STIPA", "Calibrte", "System"]


class MEASURE_FUNCTION(MessageWithParam):
    """Set the active measurement function."""

    GROUP = "Measurement"
    ROOT = "MEAS:FUNCTION {}"
    PARAM_NAME = 'function'
    PARAM_TYPE = 'categorical'
    ALLOWED_VALUES = [ParamValue(func, '', 'BASE') for func in FUNCTIONS]


class QUERY_MEASURE_FUNCTION(Message):
    """Queries the active measurement function."""

    GROUP = "Measurement"
    ROOT = "MEAS:FUNCTION?"
    RETURN = "{function}"


class MEASURE_INITIATE(Message):
    """Triggers a measurement."""

    GROUP = "Measurement"
    ROOT = "MEAS:INIT"


class QUERY_MEASURE_TIMER(Message):
    """Queries the actual measurement timer value."""

    GROUP = "Measurement"
    ROOT = "MEAS:TIME?"
    RETURN = "{t:g} sec, {status}"
    AVAILABILITY = ["SLM"]


class QUERY_MEASURE_DTTIME(Message):
    """Queries the time period used for the calculation of dt values.

    The value is active as long as the measurement is RUNNING, and is reset after each INIT:MEAS or INIT START command.

    """

    GROUP = "Measurement"
    AVAILABILITY = ["runningSLM"]
    ROOT = "MEAS:DTTI?"
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
STATISTICS = [[s.format(w) for s in p] for p, w in itertools.product(STATISTICS, 'ACZ')] + [['k1', '', 'BASE'],
                                                                                            ['k2', '', 'BASE']]


class QUERY_MEAS_SLM_123(MessageWithParams):
    """..."""
    GROUP = "Measurement"
    AVAILABILITY = ["SLM"]
    ROOT = "MEAS:SLM:123? {}"
    RETURN = "{level:g} dB, {status}"
    PARAM_TYPE = "categorical"
    PARAM_NAME = "noiseStatistics"
    ALLOWED_VALUES = [ParamValue(*p) for p in STATISTICS]

    def return_lines(self):
        return len(self.param.parameter_list())

    def parse_answers(self, lines):
        ret = {}
        for p, line in zip(self.param.parameter_list(), lines):
            ret[p] = self._parse(line)
        return ret

################
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
    """Queries the microphone type recognized by the ASD system.

    Details:
    If no ASD (A Automatic S Sensor D Detection) microphone is currently connected, the command always returns noASD.
    In contrast, the command CALIB:MIC:SENS:SOURce returns the ASD microphone that
    was last connected, as long as the microphone sensitivity has not been changed
    manually or by remote command.

    """
    GROUP = "Calibrate"
    ROOT = "CALI:MIC:TYPE?"
    RETURN = "{micType}"


class QUERY_CALIBRATE_MIC_SENS_SOURCE(Message):
    """Queries the source of the sensitivity value.
    Device answer:
        micSensytivitySource:
        [PLEASE CALIBRATE|USER CALIBRATED|MANUALLY|M2210 USER|M2210 FACTORY|M2210 CAL.CENTER|
        M4260 USER|M4260 FACTORY|M4260 CAL.CENTER]

    Returns the ASD microphone that was last connected as long as the microphone
    sensitivity has not been changed manually or by remote command.
    PLEASE CALIBRATE is returned when the sensitivity has never been set since the last
    factory default setup.

    """
    GROUP = "Calibrate"
    ROOT = "CALI:MIC:SENS:SOUR?"
    RETURN = "{micSensytivitySource}"


class CALIBRATE_MIC_SENS_VALUE(MessageWithParam):
    """Defines the microphone sensitivity in V/Pa.

    Details:
    Command is not accepted when an ASD microphone is connected.

    """

    GROUP = "Calibrate"
    ROOT = "CALI:MIC:SENS:VALU {}"
    PARAM_NAME = "micSensitivity"
    PARAM_TYPE = float
    ALLOWED_VALUES = {'min': 100e-6, 'max': 9.99}


class QUERY_CALIBRATE_MIC_SENS_VALUE(Message):
    """Queries the microphone sensitivity in V/Pa.

    Device answer is:

    V,OK  float  100e-6 to 9.99 V/Pa

    """
    GROUP = "Calibrate"
    ROOT = "CALI:MIC:SENS:VALU?"
    RETURN = "{micSensitivityValue:g} V,{status}"


##################
# System messages
class QUERY_SYSTEM_ERROR(Message):
    """Queries the error queue.

    *possible errors are:*

    - -350: "Error queue full - at least 2 errors lost",
    - -115: "Too many parameters in command",
    - -113: "Invalid command",
    - -112: "Too many characters in one of the command parts",
    - -109: "Missing command or parameter",
    - -108: "Invalid parameter",
    - 0: "no error (queue is empty)",
    - 1: "Command too long; too many characters without new line",
    - 2: "UNEXPECTED_PID",
    - 3: "DSP_TIMEOUT",
    - 4: "Changing microphone sensitivity is not possible when an ASD microphone is connected to the XL2",
    - 5: "Parameter not available, license not installed",
    - 6: "dt value does not exist for this parameter",
    - 7: "Parameter is not available in the current measurement function",
    - 8: "Unspecified DSP error",
    - 9: "Not valid, measurement is running"

    Attributes
    -----
    ERRORS : dict
        dict of errors.

    """

    GROUP = "System"
    ROOT = "SYST:ERRO?"
    RETURN = "{errList}"
    ERRORS = {
        -350: "Error queue full - at least 2 errors lost",
        -115: "Too many parameters in command",
        -113: "Invalid command",
        -112: "Too many characters in one of the command parts",
        -109: "Missing command or parameter",
        -108: "Invalid parameter",
        0: "no error (queue is empty)",
        1: "Command too long; too many characters without new line",
        2: "UNEXPECTED_PID",
        3: "DSP_TIMEOUT",
        4: "Changing microphone sensitivity is not possible when an ASD microphone is connected to the XL2",
        5: "Parameter not available, license not installed",
        6: "dt value does not exist for this parameter",
        7: "Parameter is not available in the current measurement function",
        8: "Unspecified DSP error",
        9: "Not valid, measurement is running"
    }

    def parse_answers(self, lines):
        assert len(lines) == 1
        line = lines[0]
        ret = self._parse(line)["errList"]
        err_list = [int(i.strip()) for i in ret.split(",")]
        return [(err, self.ERRORS.get(err)) for err in err_list]


class SYSTEM_KEY(MessageWithParams):
    """Simulates a key stroke on the XL2"""

    GROUP = "System"
    ROOT = "SYST:KEY {}"
    RETURN = "{status}"
    PARAM_TYPE = "categorical"
    ALLOWED_VALUES = [ParamValue(key, '', 'BASE') for key in
                      ["ESC", "NEXT", "FNEXT", "PREV", "FPREV", "ENTER", "PAGE", "START",
                       "PAUSE", "SPEAKER", "LIMIT", "LIGHT"]]
    REPEAT_PARAM = 30


class SYSTEM_KLOCK(MessageWithParam):
    """Locks the keyboard of the XL2"""

    GROUP = "System"
    ROOT = "SYST:KLOC {}"
    PARAM_TYPE = "categorical"
    ALLOWED_VALUES = [ParamValue("ON", "Keyboard is locked", "BASE"),
                      ParamValue("OFF", "Keyboard is unlocked", "BASE")]
    PARAM_NAME = "keyStroke"

    @classmethod
    def ON(cls):
        instance = cls()
        instance.set_param("ON")
        return instance

    @classmethod
    def OFF(cls):
        instance = cls()
        instance.set_param("OFF")
        return instance


class QUERY_SYSTEM_KLOCK(Message):
    """Queries the key lock status"""
    GROUP = "System"
    ROOT = "SYST:KLOC?"
    RETURN = "{keyLock}"


class QUERY_SYSTEM_OPTIONS(Message):
    """Queries the installed options."""

    GROUP = "System"
    ROOT = "SYST:OPTI?"
    RETURN = "{optList}"

    def parse_answers(self, lines):
        assert len(lines) == 1
        line = lines[0]
        ret = self._parse(line)["optList"]
        return [i.strip() for i in ret.split(",")]


class SYSTEM_MSDMAC(Message):
    """Switches the XL2 to the USB mass storage mode for Mac and Linux.

    Use this Command on Mac and Linux instead of “SYSTem:MSD”, otherwise MSD will
    timeout after 2 minutes and the XL2 returns to COM mode.
    After sending this command, the XL2 drops the COM connection (no more remote
    commands are possible) and switches to mass storage mode. The host then has full
    access to the data stored on the SD card of the XL2.
    To return to COM mode eject the XL2 drive from the host computer.

    Note
    ----
    If you umount the XL2 drive by the host, the XL2 will not return to COM
    mode. it is necessary to eject the disk.

    """

    GROUP = "System"
    ROOT = "SYST:MSDMAC"

