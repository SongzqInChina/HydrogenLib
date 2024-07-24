import logging

# module end 我们会将模块的很多常量慢慢集成到这里

zlibcon_logger = logging.getLogger(__name__)

DBX_FUNC_TYPE_MRO = 0x1001
DBX_FUNC_TYPE_GET = 0x1002
ETY_TYPE_KEY = 0x1003
ETY_TYPE_IV = 0x1004

UNKNOWN = "Unknown"


_link_constants = []


def link_constant(name, value):
    """
    create new constant in `libcon`


    :param name:
    :param value:
    :return:
    """
    globals()[name] = value
    _link_constants.append(name)


def unlink_constant(name):
    if name not in _link_constants:
        raise ValueError(f"{name} is not a constant")
    del globals()[name]


zlibcon_logger.debug("Module zlibcon loading ...")
