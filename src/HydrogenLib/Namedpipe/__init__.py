from .. import _PlatFormGetter

if _PlatFormGetter.is_win():
    from .windows import *

if _PlatFormGetter.is_linux():
    from .linux_or_mac import *
