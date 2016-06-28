"""load package using autoreload."""

from IPython import get_ipython
ipython = get_ipython()
ipython.magic('load_ext autoreload')
ipython.magic('autoreload 1')
ipython.magic('aimport ntixl2')

from ntixl2.xl2 import XL2SLM
from ntixl2.message import *

#####################
# initiate XL" object
xl2 = XL2SLM()