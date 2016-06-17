from IPython import get_ipython
ipython = get_ipython()
ipython.magic('load_ext autoreload')
ipython.magic('autoreload 1')
ipython.magic('aimport NTiXL2')

import NTiXL2
from NTiXL2 import XL2
from NTiXL2.message import *
import time

xl2 = XL2()
path = 'Projects/SCHAFER'
print("device_status", xl2.device_status)
print("IDN :",xl2.serial_message(QUERY_IDN()))
print("measure Function :",xl2.serial_message(QUERY_MEASURE_FUNCTION()))
print("INIT_STATE :",xl2.serial_message(QUERY_INITIATE_STATE()))

print("Error :",xl2.serial_message(QUERY_SYSTEM_ERROR()))

def select_profile_RBL(xl2,profile = 6):
    #reset
    m = RESET()
    xl2.serial_message(m)
    #key msg
    m = SYSTEM_KEY()
    #select profile
    for par in  ['ESC','ENTER'] + ['NEXT']*8 + ['ENTER']*2 + ['NEXT']*profile +['ENTER']:
        m.append_param(par)
    r = xl2.serial_message(m)
    return r

def f(xl2):
    select_profile_RBL(xl2, profile=6)
    slmq = QUERY_MEAS_SLM_123()
    slmq.set_param('LZEQ')
    for i in range(30):
        time.sleep(1)
        state = xl2.serial_message(QUERY_INITIATE_STATE())
        print("INIT_STATE :", state)
        time.sleep(1)
        if not state=='RUNNING':
            xl2.serial_message(INITIATE.START())
        try:
            pass
            #xl2.serial_message(MEASURE_INITIATE())
        except:
            pass
        #print(xl2.serial_message(slmq))
        print("seconds:" ,i*60 )
        time.sleep(58)
    ##
    xl2.serial_message(INITIATE.STOP())
    print(xl2.serial_message(QUERY_INITIATE_STATE()))

