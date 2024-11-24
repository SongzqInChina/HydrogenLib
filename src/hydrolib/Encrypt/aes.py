import logging
import os
from typing import Iterable

import pyaes

from .func import split, pad, unpad

zencrypt_logger = logging.getLogger("SzQlib.zencrypt")


# module end


def aes_encrypt(plaintext: bytes, key, iv=None):
    if iv is None:
        iv = os.urandom(16)

    plaintext_bytes = plaintext
    padded_plaintext = plaintext_bytes
    aes = pyaes.AESModeOfOperationCBC(key, iv)
    ciphertext = aes.encrypt(padded_plaintext)
    return ciphertext, iv


def aes_decrypt(ciphertext, key, iv):
    aes = pyaes.AESModeOfOperationCBC(key, iv)
    decrypted_data = aes.decrypt(ciphertext)
    return decrypted_data


def aes_encrypt_ls(plain_text_list: Iterable, key, vi=None, NoIV=False):
    for i in plain_text_list:
        if NoIV:
            yield aes_encrypt(i, key, vi)[0]
        else:
            yield aes_encrypt(i, key, vi)


def aes_detrypt_ls(cipher_text_list, key, vi):
    for i in cipher_text_list:
        yield aes_decrypt(i, key, vi)


def generate_key(size=16):
    return os.urandom(size)


def generate_iv(size=16):
    return os.urandom(size)


def generate(size=16):
    return generate_key(size), generate_iv(size)


def split_pad(text: bytes, size=16):
    return [pad(i, size) for i in split(text, size)]


def join(args):
    return b''.join(args)


def encode(text: bytes, key, iv):  # 提供一个最简单的加密api
    """
    加密函数，提供一个最简单的api加快使用效率
    :param text:
    :param key:
    :param iv:
    :return: bytes
    """
    byte = text
    byte = split_pad(byte)
    crypt_text = aes_encrypt_ls(byte, key, iv, NoIV=True)

    return join(crypt_text)


def decode(crypt_text: bytes, key, iv):  # 提供一个最简单的解密api
    """
    解密，提供一个最简单的api加快使用效率
    :param crypt_text:
    :param key:
    :param iv:
    :return: str
    """
    crypt_list = split(crypt_text)
    plain_text = list(aes_detrypt_ls(crypt_list, key, iv))
    for i in range(len(plain_text)):
        plain_text[i] = unpad(plain_text[i])
    return join(plain_text)


def encrypt(plain_text: bytes, key, iv=None):  # 别名
    return encode(plain_text, key, iv)


def decrypt(crypt_text: bytes, key, iv=None):  # 别名
    return decode(crypt_text, key, iv)


zencrypt_logger.debug("Module zencrypt loading ...")
