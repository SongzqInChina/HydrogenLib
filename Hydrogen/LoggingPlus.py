"""
基于logging开发的扩展模块
添加了一些函数帮助更好的，更简洁的使用logging的功能
"""

import logging
import sys


def output_to_console(logger: logging.Logger):
    stream = logging.StreamHandler(sys.stdout)
    logger.addHandler(stream)


def output_to_file(logger: logging.Logger, path: str):
    file = logging.FileHandler(path)
    logger.addHandler(file)
