#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ABSFUYU: EVERYTHING
-------------------
Everything has to offer in this package
"""

# Normal
from absfuyu.calculation import *
from absfuyu.data import *
from absfuyu.fibonacci import *
from absfuyu.help import *
from absfuyu.pry import *
from absfuyu.fun import *
from absfuyu.generator import *
from absfuyu.obfuscator import *
from absfuyu.sort import *
from absfuyu.strings import *
from absfuyu.util import *
from absfuyu.version import *
from absfuyu.lists import *
from absfuyu.stats import *
from absfuyu.dicts import *

# Extra
try:
    from absfuyu.extensions.extra import *
    from absfuyu.extensions.beautiful import *
    from absfuyu.extensions.dev import *
except:
    pass

# Is loaded
__IS_EVERYTHING = True