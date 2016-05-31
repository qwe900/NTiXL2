from serial import Serial
from serial.tools import list_ports

import sys

reset = "*RST"
smes = "MEAS:INIT"
start = "INIT START"
stop = "INIT STOP"
mes = "MEAS:SLM:123? LAS"


def find_xl2( linux = False, filter= "XL2"):
    comports = list(list_ports.comports())
    attr = ['device', 'description','pid','vid','serial_number', 'product']
    devices = []
    for p in comports:
        if linux:
            attribute = {a : getattr(p,a) for a in attr}
            q = any([filter in v for k,v in attribute.items()])
            print('Device: ', attribute['description'], ', filter: ', q)
            if q:
                devices.append(attribute)
        else:
            attribute = p
            q = any([(filter in v) for v in p if type(v)=='str'])
            print('Device: ', attribute[1], ', filter: ', q)
            if q:
                devices.append(attribute)
    return devices


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

def ykush(command = '-d', port = 3):
    """
    run ykush program
    :param command: '-u or -d'
    :param port: 1, 2, 3 or a
    :return: None
    """
    import subprocess
    subprocess.Popen(["sudo", "~/XL2/YKUSH_V+.4.1/ykush", command, str(port)])

for conn in find_xl2():
    conn = Serial(conn['device'], 9600,timeout=1)