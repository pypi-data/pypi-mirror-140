
from collections.abc import Iterable
from . import is_a


def flatten(iterable):
    if isinstance(iterable, Iterable) and not isinstance(iterable,
                                                                     str):
        return [a for i in iterable for a in flatten(i)]
    else:
        return [iterable]


def make_list(obj, flatten_list=True):
    if not is_a.List(obj):
        obj = [obj]
    if flatten_list:
        obj = flatten(obj)
    return obj
