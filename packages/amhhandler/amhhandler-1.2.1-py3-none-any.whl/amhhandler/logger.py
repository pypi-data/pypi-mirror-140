#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@time   : 2021/1/8 16:23
@file   : logger.py
@author : nbyue
@desc   : 
@exec   : /bin/python3 logger.py
@wiki
"""
import logging
from logging.handlers import RotatingFileHandler


def log2file(log_file):
    """
    :param log_file:
    :return:
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    # 定义handler的输出格式
    fmt = logging.Formatter(
        "%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s")
    handler = RotatingFileHandler(
        filename=log_file, mode='a', maxBytes=10 * 1024 * 1024, backupCount=2)
    handler.setLevel(logging.INFO)
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    return logger
