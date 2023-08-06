#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dict Module
-----------
Some dict methods

Contain:
- dict_int_analyze
- dict_int_analyze_fast
"""



# Module level
##############################################################
__all__ = [
    "dict_int_analyze", "dict_int_analyze_fast"
]




# Library
##############################################################
from typing import Dict as __Dict

from .core import Number as __Num





# Function
##############################################################
def dict_int_analyze(dct: __Dict[str, __Num]):
    """
    Analyze all the key values (int, float) in dict then return highest/lowest index
    """

    input_ = list(dct.items())
    max, min = input_[0][1], input_[0][1]
    max_index = []
    min_index = []
    max_list = []
    min_list = []

    for i in range(len(input_)):
        if input_[i][1] > max:
            max = input_[i][1]
        elif input_[i][1] < min:
            min = input_[i][1]
    
    for i in range(len(input_)):
        if input_[i][1] == max:
            max_index.append(i)
        elif input_[i][1] == min:
            min_index.append(i)
    
    for x in max_index:
        max_list.append(input_[x])

    for x in min_index:
        min_list.append(input_[x])

    
    output = {
        "max_index": max_index,
        "min_index": min_index,
        "max": max_list,
        "min": min_list
    }

    return output

def dict_int_analyze_fast(dct: __Dict[str, __Num]):
    """
    Analyze all the key values (int, float) in dict then return highest/lowest index
    (faster version)
    """

    max_val = max(list(dct.values()))
    min_val = min(list(dct.values()))
    max_list = []
    min_list = []

    for k, v in dct.items():
        if v == max_val:
            max_list.append((k, v))
        if v == min_val:
            min_list.append((k, v))

    output = {
        "max_value": max_val,
        "min_value": min_val,
        "max": max_list,
        "min": min_list
    }

    return output