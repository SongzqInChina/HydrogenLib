import hashlib
import logging

from . import TypeFunc
from .zfilex import JsonFileOpen, JsonGet, JsonSet
from .Encryio import EncryptJsonOpen
from .Json import *
from .Const import *
from .PathPlus import *


zdatabasex_logger = logging.getLogger(__name__)





def mktemplate(**dic):
    return TypeFunc.template.Template(**dic)


zdatabasex_logger.debug("Module zdatabaseX loading ...")
