from IPython import get_ipython
import ntixl2
from ntixl2.xl2 import XL2SLM
from ntixl2.message import *
import time

ipython = get_ipython()
ipython.magic('load_ext autoreload')
ipython.magic('autoreload 1')
ipython.magic('aimport NTiXL2')



#####################
# initiate XL" object
xl2 = XL2SLM()
print("device_status", xl2.device_status)
print("IDN :", xl2.identification())
print("measure Function :", xl2.serial_message(QUERY_MEASURE_FUNCTION()))
print("INIT_STATE :", xl2.serial_message(QUERY_INITIATE_STATE()))
print("Error :", xl2.check_errors())
# Reset device and select profile RBL
xl2.select_profile(profile=6)
# unlock key
xl2.klock()
# profile sd path
path = 'Projects/RBL'
# query
slmq = QUERY_MEAS_SLM_123()
slmq.set_param('LZEQ')

# #initiate state
xl2.serial_message(INITIATE.START())
# do measurement of sec length
i = 0
while i <= 120:
    state = xl2.serial_message(QUERY_INITIATE_STATE())[ 'state' ]
    print(state)
    if state == 'RUNNING':
        xl2.serial_message(MEASURE_INITIATE())
        try:
            r = xl2.serial_message(slmq)
        except:
            r = 'ERR'
        print("seconds: {}; value: {}".format(i, r))
        time.sleep(1)
        i += 1
    else:
        time.sleep(0.1)
#
xl2.serial_message(INITIATE.STOP())
print(xl2.serial_message(QUERY_INITIATE_STATE()))
