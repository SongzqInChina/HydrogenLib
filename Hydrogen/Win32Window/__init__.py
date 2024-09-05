from .. import _PlatFormGetter

if _PlatFormGetter.is_win():
    from .win32 import *
