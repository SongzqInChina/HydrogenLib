import hashlib
import logging

zhash_logger = logging.getLogger("SzQlib.zhash")

# module end

hash_mro = {
    "md5": 16,
    "sha256": 32,
    "sha512": 64,
    "sha3_224": 28,
    "sha3_256": 32,
    "sha3_384": 48,
    "sha3_512": 64,
    "shake_128": 32,
    "shake_256": 64,
    "blake2b": 64,
    "blake2s": 32,
    "sha1": 20,
    "sha224": 28,
    "sha384": 48,
}

max_length = 2 ** 24


def getHashValueByName(string: bytes, hash_name: str = "sha256", length=None):
    """
    如果hash_name不为shake_128或shake_256，则不需要填写length参数
    """
    if length is None:
        length = hash_mro[hash_name]
    if length < 0 or length > max_length:
        zhash_logger.error("length must be between 0 and 2**24")
        raise ValueError("length must be between 0 and 2**24")
    if hash_name in hash_mro:
        hash_func = hashlib.__dict__[hash_name]
        if hash_name not in ("shake_128", "shake_256"):
            return hash_func(string).digest()
        else:
            return hash_func(string).digest(length)
    else:
        return hashlib.sha256(string).digest()


zhash_logger.debug("Module zhash loading ...")
