"""
Core Module
-----------

Contain type hint and other stuff
"""

# Module Package
##############################################################
ModulePackage = [
    "all",
    "cli",
    "beautiful", "extra", 
    "test", "dev", "fixers",
]


# Library
##############################################################
from typing import (
    Dict as __Dict,
    # Iterable as __Iterable,
    List as __List,
    Optional as __Optional,
    # Sequence as __Sequence,
    Tuple as __Tuple,
    TypeVar as __TypeVar,
    Union as __Union,
)

from sys import version_info as __py_ver # Get python version
if __py_ver[0] == 3:
    # Python 3.7.x
    if __py_ver[1] == 7:
        try:
            from typing_extensions import Literal as __Literal
        except ImportError as err:
            # Auto install
            from subprocess import run as __run
            __cmd = [
                # "python -m pip install --upgrade pip".split(),
                "python -m pip install typing_extensions".split(),
            ]
            for x in __cmd:
                __run(x)
            # raise SystemExit(err)
    # Not python 3.7.x | Python >= 3.8
    else:
        from typing import Literal as __Literal
else:
    raise SystemExit("Not Python 3")

# Check for colorama library
try:
    import colorama as __colorama
except ImportError:
    __colorama = None




# Color - colorama
##############################################################
if __colorama is not None:
    # __colorama.init(autoreset=True)
    Color: __Dict[str, str] = {
        "green": __colorama.Fore.LIGHTGREEN_EX,
        "blue": __colorama.Fore.LIGHTCYAN_EX,
        "red": __colorama.Fore.LIGHTRED_EX,
        "RED": __colorama.Fore.RED,
        "yellow": __colorama.Fore.LIGHTYELLOW_EX,
        "reset": __colorama.Fore.RESET
    }
else:
    Color = {"green":"", "blue":"", "red":"",
    "RED":"", "yellow":"", "reset":""}


# Type hints
##############################################################
Number = __TypeVar("Number", int, float)
NumberC = __TypeVar("NumberC", int, float, complex)

# Random string generator
CharacterOption = __Literal[
    "default", "alphabet", "full", "uppercase",
    "lowercase", "digit", "special", "all"
]

# Obfuscator
EncodeOption = __Literal["b64","full"]
CodecOption = __Literal["rot_13"]
TxtFormat = __Literal["txt","py","bat"]

Path = str

# Matrix stuff
MatrixOption = __Literal["all","row","col"]

# Sudoku
Sudoku = __List[__List[int]]
SudokuStr = str
Position = __Optional[__Tuple[int, int]]
SudokuStrStyle = __Literal["zero", "dot"]

# Other
MonthLong = __Literal["january", "february", "march", "april", "may", "june", "july", "august" , "september", "october", "november", "december"]
MonthShort = __Literal["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug" , "sep", "oct", "nov", "dec"]
Month = __Union[MonthShort, MonthLong]
