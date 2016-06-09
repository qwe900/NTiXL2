from serial import Serial
from serial.tools import list_ports

import sys

reset = "*RST"
smes = "MEAS:INIT"
start = "INIT START"
stop = "INIT STOP"
mes = "MEAS:SLM:123? LAS"





def command(conn,c):
    conn.write((c + "\n").encode('UTF-8'))
    l = conn.readline()
    if len(l):
        return l.decode('UTF-8')
    else:
        return l

def to_mass_storage(CONN):
    mass = "SYST:MSDMAC"
    command(CONN,mass)
    CONN.Close()
    return device
    
def to_serial():
    import subprocess
    subprocess.Popen(["safe_rm_XL2-sd"])


xl2=find_xl2(linux=True)[0]
conn = Serial('XL2', 9600,timeout=1)
#to_mass_storage(conn)
