import hashlib
import struct

from . import Hash as shash
from . import BaseStruct as ostruct
from . import Time
from . import TypeFunc


def pack(data, hashes=None, timestamp=None):
    # --------------------------------------------
    # init_head |  8    |   8    | hash报文  | *
    # 初始化头    |数据长度 | 时间戳 | hash报文 | 数据
    # --------------------------------------------
    # init_head = struct.pack("<Q", len(data_bytes+8))  # 加上自己的长度
    if hashes is None:
        hashes = ["md5", "sha256", "sha512"]
    if timestamp is None:
        timestamp = Time.time.time()
    data_size = ostruct.pack(len(data))  # 使用小端序8个字节无符号整数表示数据长度
    time_head = ostruct.pack(int(timestamp))  # 时间戳
    hash_head = b""
    for hash_name in hashes:
        # hash_size hash_name_size data_hash hash_name
        if hash_name in hashlib.__dict__:
            data_hash = shash.getHashValueByName(data, hash_name)
            hash_name_bytes = hash_name.encode("utf-8")  # hash名称
            hash_name_size = ostruct.pack(len(hash_name_bytes))  # hash名称长度
            hash_size = ostruct.pack(len(data_hash))  # hash长度
            hash_head += hash_size + hash_name_size + data_hash + hash_name_bytes  # hash报文

    data_bytes = data_size + hash_head + data
    init_head = ostruct.pack(len(data_bytes) + 16)
    return init_head + time_head + data_size + hash_head + data


def __unpack(__data):
    data = TypeFunc.IndexOffset.Offset(__data)
    init_head = ostruct.unpack(int, data > 8)  # 初始化头——数据段总长

    now_data = data.offseter(init_head - 8)  # 跳过初始化头，获取hash，时间戳和数据

    time_head = ostruct.unpack(int, now_data > 8)  # 时间戳
    data_size = ostruct.unpack(int, now_data > 8)  # 实际数据长度

    # print(data_size, time_head)

    data_bytes = now_data[-data_size:]  # 数据
    data_hashes = TypeFunc.IndexOffset.Offset(now_data[: -data_size])  # 获取hash段
    data_hashes += 16  # 跳过初始化头、时间戳（16字节）
    hashes = {}
    # 分离hash
    while True:
        hash_size = ostruct.unpack(int, data_hashes > 8)  # hash 长度
        hash_name_size = ostruct.unpack(int, data_hashes > 8)  # hash 名称长度

        # print(hash_size, hash_name_size)

        data_hash = data_hashes > hash_size
        hash_name = data_hashes > hash_name_size
        hashes[hash_name.decode()] = data_hash
        if data_hashes.isend():
            break
    return {
        "data": data_bytes,
        "time": time_head,
        "hashes": hashes,
        "size": init_head,
    }


def __unpacks(__data):
    data = __data
    init_head = struct.unpack("<Q", data >= 8)[0]
    now_data = data.offseter(init_head)
    if not data.isend():
        return [now_data, *__unpacks(data)]
    return [now_data]


def unpacks(__data):
    data = TypeFunc.IndexOffset.Offset(__data)
    map_data = map(lambda x: __unpack(x.to(bytes)), __unpacks(data))
    for i in map_data:
        yield i  # type: dict


def lunpacks(__data):
    return list(unpacks(__data))


def lunpacks_hash(__data):
    try:
        ls = lunpacks(__data)
    except:
        return None
    for i in ls:
        for hash_name, hash_value in i["hashes"].items():
            assert \
                shash.getHashValueByName(i["data"], hash_name) == hash_value, \
                f"哈希验证错误:\n\tname={hash_name}, \n\tvalue ={hash_value}, \n\texcept={shash.getHashValueByName(i["data"], hash_name)}."
    return ls
