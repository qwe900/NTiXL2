"""load package using autoreload."""

print('import ntixl2 with autoreload extension')
from IPython import get_ipython
ipython = get_ipython()
ipython.magic('load_ext autoreload')
ipython.magic('autoreload 1')
ipython.magic('aimport ntixl2')

from ntixl2.xl2 import XL2SLM
from ntixl2.message import *

#####################
print("initiate XL2 object as xl2")
xl2 = XL2SLM()