from .Abc import Serializer
from .S_BinStruct import *
from .S_Json import *
from .S_JsonPickle import *
from ...struct_plus import simple_pack, simple_unpack, simple_unpacks
from ...type_func import get_subclasses


def pack(obj, serializer: Serializer = None):
    if serializer is None:
        serialier = Json()

    return connect_length(
        connect_length(
            serializer.dumps(obj)
        ) +
        connect_length(
            serializer.__class__.__name__.encode()
        )
    )


def unpack(data: bytes):
    data = simple_unpack(data)
    data, serializer_name = simple_unpacks(data)
    subclasses = {t.__name__:t for t in get_subclasses(Serializer)}
    if serializer_name.decode() not in subclasses:
        raise ValueError(f'{serializer_name.decode()} is not a subclass of Serializer')

    serializer = subclasses[serializer_name.decode()]()
    return serializer.loads(data)
