"""
Simple example of nti module usage

list data located on sd card of XL2SLM
"""
from ntixl2 import XL2SLM

# initiate XL" object
xl2 = XL2SLM()
print("device_status: ", xl2.device_status)
print("switch to device status to MASS", xl2.to_mass())
folder = "Projects"
print("list dir in {}/{} folder\n ".format(str(xl2.mountDir), folder), xl2.list_dir(folder))
path = input("Please enter folder to list files: ")
print("files: \n", "\n".join(xl2.list_files(folder +'/'+ path)))

