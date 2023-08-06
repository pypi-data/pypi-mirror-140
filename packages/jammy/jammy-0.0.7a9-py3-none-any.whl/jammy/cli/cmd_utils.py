import re
import argparse
from collections.abc import Iterable
import itertools
from dataclasses import asdict
from dataclasses import fields


def _args_single_param(item):
    key, value = item
    rtn = []
    if not isinstance(value, Iterable):
        value = [value]
    fist_element = value[0] if isinstance(value, list) else value
    if isinstance(fist_element, bool):
        for cur_value in value:
            arg = '--' + key if cur_value else '--no_' + key
            rtn.append(arg)
        return rtn
    for i in value:
        rtn.append(f"--{key} {i}")

    return rtn


def param_sweep(prefix=None, **kwargs):
    args_list = list(map(_args_single_param, kwargs.items()))
    if prefix is not None:
        args_list.insert(0, [prefix])
    permutation = list(itertools.product(*args_list))
    return [' '.join(item) for item in permutation]
