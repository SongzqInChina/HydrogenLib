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

max_lenght = 2 ** 24


def gethashByName(string, hash_name="sha256", lenght=None):
    if lenght is None:
        lenght = hash_mro[hash_name]
    if lenght < 0 or lenght > max_lenght:
        zhash_logger.error("lenght must be between 0 and 2**24")
        raise ValueError("lenght must be between 0 and 2**24")
    if hash_name in hash_mro:
        hash_func = hashlib.__dict__[hash_name]
        if hash_name not in ("shake_128", "shake_256"):
            return hash_func(string).digest()
        else:
            return hash_func(string).digest(lenght)
    else:
        return hashlib.sha256(string).digest()


zhash_logger.debug("Module zhash loading ...")
