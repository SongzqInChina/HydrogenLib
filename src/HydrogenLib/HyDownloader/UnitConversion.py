from decimal import Decimal as float
from ..Class.DoubleDict import DoubleDict

unit_mapping = DoubleDict(
    {
        'bit': 0,
        'byte': 1,
        'kb': 2,
        'mb': 3,
        'gb': 4,
        'tb': 5,
        'pb': 6,
        'b': 1,
    }
)


def converse(value, from_unit, to_unit):
    if from_unit == to_unit:
        return value
    funit = unit_mapping[from_unit]
    tunit = unit_mapping[to_unit]

    if tunit > funit:
        return float(value) / (1024 ** (tunit - funit))
    return float(value) * (1024 ** (funit - tunit))


def converse_s(value, to_unit):
    for unit in unit_mapping:
        if value.lower().endswith(unit):
            return converse(float(value[:-len(unit)]), unit, to_unit)
    return None


def to_string(value, unit):
    """
    自动将数据转换成合适的单位
    """
    if unit_mapping[unit] == 6:
        return f"{value:.2f}PB"
    elif value >= 1024:
        next_unit = unit_mapping[unit_mapping[unit] + 1]
        return to_string(float(value) / 1024, next_unit)

    else:
        return f"{value:.2f}{unit}"
