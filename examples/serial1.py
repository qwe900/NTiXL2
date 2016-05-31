from serial import Serial
from serial.tools import list_ports
import sys

reset = "*RST"
smes = "MEAS:INIT"
start = "INIT START"
stop = "INIT STOP"
mes = "MEAS:SLM:123? LAS"


def find_port():
    comlist = list(list_ports.comports())
    if len(comlist):
        XL2 = [(s1,s2,s3) for s1,s2,s3 in comlist if '1A2B:0004' in s3 ]
    if len(XL2):
        return XL2[0]




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

def mount(name = "NTIAUDIOXL2"):
    import os
    import subprocess
    mountDir = "/media/"+name
    out =subprocess.check_output(["sudo","blkid","-t", 'LABEL="{}"'.format(name),"-o" , "value"])
    _, UUID, format = out.decode('UTF-8').split('\n')[1:-1]
    if not os.path.isdir(mountDir):
        subprocess.Popen(["sudo","mkdir", mountDir])
    subprocess.Popen(["sudo","mount","-t", format ,"-U" , UUID, mountDir])
    return mountDir

def umount(name = "NTIAUDIOXL2"):
    import subprocess
    mountDir = "/media/"+name
    #if os.path.ismount(mountDir):
    subprocess.Popen(["sudo","umount", mountDir])
    #subprocess.Popen(["sudo","rm","-r", mountDir])


def mount_status():
    import subprocess
    out =subprocess.check_output(["sudo","blkid","-o", "list", "-w", "/dev/null"])
    print(out.decode('UTF-8'))

def reset_USB():
    import subprocess
    subprocess.Popen(["sudo","umount", mountDir])

XL2 = find_port()

if XL2 is not None:
    PORT = XL2[0]
    conn = Serial(PORT, 9600,timeout=1)