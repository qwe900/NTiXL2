from ntixl2.xl2parser import *

Edict = parse_broadband_file("data/2016-06-28_SLM_002_123_Log.txt")

print(dict)

dict = parse_spectrum_file("data/2016-06-28_SLM_002_RTA_3rd_Log.txt")

print(dict)