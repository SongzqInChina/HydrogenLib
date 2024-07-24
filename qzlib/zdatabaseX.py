import hashlib
import logging

from . import typefunc
from .zfilex import JsonFileOpen, JsonGet, JsonSet
from .zencryio import EncryptJsonOpen
from .zjson import *
from .zlibcon import *
from .zpath import *


zdatabasex_logger = logging.getLogger(__name__)





def mktemplate(**dic):
    return typefunc.template.Template(**dic)


zdatabasex_logger.debug("Module zdatabaseX loading ...")
