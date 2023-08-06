"""
ABSFUYU-EXTRA: DATA ANALYSIS
-------------
"""



# Library
##############################################################
__EXTRA_MODE = False
try:
    import pandas as __pd
    import numpy as __np
    import matplotlib.pyplot as __plt
except ImportError:
    from absfuyu.config import show_cfg as __aie
    if __aie("auto-install-extra", raw=True):
        __cmd: str = "python -m pip install -U absfuyu[extra]".split()
        from subprocess import run as __run
        __run(__cmd)
    else:
        raise SystemExit("This feature is in absfuyu[extra] package")
else:
    __EXTRA_MODE = True



def isloaded():
    try:
        if __EXTRA_MODE:
            return True
        else:
            return False
    except:
        return True