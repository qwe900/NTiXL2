""" usage: python3 measuremet.py repetition timesteps. """

import sys
from ntixl2.xl2 import XL2SLM
from ntixl2.message import *

import time
import datetime

if len(sys.argv) == 3:
    try:
        repetition = int(sys.argv[1])
        timestep = int(sys.argv[2])
    except:
        print(__doc__)
        sys.exit()
else:
    print(__doc__)
    sys.exit()

tot_time = datetime.timedelta(seconds=repetition*timestep)
print('Measuremet lenght is {} h:m:s, timestep is {} sec.'.format(str(tot_time), timestep))

#####################
# initiate XL" object
xl2 = XL2SLM()
# Reset device and select profile RBL
xl2.select_profile(profile=5)
# unlock key
xl2.klock()
# query
slmq = QUERY_MEAS_SLM_123()
slmq.set_param('LAEQ')

# #initiate state
xl2.serial_message(INITIATE.START())
# do measurement of sec length
i = 0
while i <= repetition:
    state = xl2.serial_message(QUERY_INITIATE_STATE())[ 'state' ]
    if state == 'RUNNING':
        xl2.serial_message(MEASURE_INITIATE())
        r = xl2.serial_message(slmq)
        print("elapsed time: {}; value: {}".format(str(datetime.timedelta(seconds=i*timestep)), r))
        time.sleep(timestep)
        i += 1
    else:
        time.sleep(0.1)
#
xl2.serial_message(INITIATE.STOP())
print('STOP measurement')
