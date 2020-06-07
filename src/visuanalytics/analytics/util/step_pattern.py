import operator
from functools import reduce
from string import Formatter


class StepPatternFormatter(Formatter):
    def __init__(self, split_key="|"):
        super().__init__()
        self.__split_key = split_key

    def get_value(self, key, args, kwargs):
        return data_get_pattern(key, args[0], self.__split_key)


def _to_int(x):
    return int(x) if x.isnumeric() else x


def data_get_pattern(keys, data, split_key="|"):
    if isinstance(keys, str):
        keys = map(_to_int, keys.split(split_key))
        return reduce(operator.getitem, keys, data)

    return data[keys]


def data_insert_pattern(keys, data, value, split_key="|"):
    if isinstance(keys, str) and '|' in keys:
        key_array = keys.split(split_key)
        keys = map(_to_int, key_array[:-1])
        last = _to_int(key_array[-1])

        reduce(operator.getitem, keys, data)[last] = value
    else:
        data[keys] = value
