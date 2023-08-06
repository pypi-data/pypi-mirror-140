# -*- coding: utf-8 -*-
"""
ABSFUYU WIP FEATURES
--------------------
WARNING: UNSTABLE
"""

__all__ = [
    "password_check", "fib",
]


# import math
import re as __re
import os as __os
from functools import lru_cache
# from typing import AnyStr as __AnyStr
# from typing import Dict as __Dict
# from typing import Iterable as __Iterable
# from typing import List as __List
# from typing import Optional as __Optional
# from typing import Sequence as __Sequence
# from typing import TypeVar as __TypeVar
# from typing import Union as __Union
# from typing import overload



__here = __os.path.abspath(__os.path.dirname(__file__))






# PASSWORD CHECKER
def password_check(password: str) -> bool:
    """
    Verify the strength of 'password'.
    Returns a dict indicating the wrong criteria.
    A password is considered strong if:
    - 8 characters length or more
    - 1 digit or more
    - 1 symbol or more
    - 1 uppercase letter or more
    - 1 lowercase letter or more
    """

    # calculating the length
    length_error = len(password) < 8

    # searching for digits
    digit_error = __re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = __re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = __re.search(r"[a-z]", password) is None

    # searching for symbols
    symbols = __re.compile(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]')
    symbol_error = symbols.search(password) is None

    detail = {
        'password_ok': not any([ # overall result
            length_error, digit_error,
            uppercase_error, lowercase_error,
            symbol_error
        ]),
        'length_error': length_error,
        'digit_error': digit_error,
        'uppercase_error': uppercase_error,
        'lowercase_error': lowercase_error,
        'symbol_error': symbol_error,
    }

    return detail['password_ok']



# FIBONACCI WITH CACHE
@lru_cache(maxsize=5)
def fib(n: int) -> int:
    """Fibonacci (recursive)"""
    # max recursion is 484
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)




# PRIME NUMBERS (SMALLER THAN 100000 - 9592 NUMBERS)
# from . import load_data as ld
# PRIME_NUMBER = ld.toList(ld.LoadData("prime"))



# https://stackoverflow.com/questions/563022/whats-python-good-practice-for-importing-and-offering-optional-features
def __optional_import(module: str, name: str = None, package: str = None):
    import importlib
    try:
        module = importlib.import_module(module)
        return module if name is None else getattr(module, name)
    except ImportError as e:
        if package is None:
            package = module
        msg = f"install the '{package}' package to make use of this feature"
        import_error = e

        def _failed_import(*args):
            raise ValueError(msg) from import_error

        return _failed_import
