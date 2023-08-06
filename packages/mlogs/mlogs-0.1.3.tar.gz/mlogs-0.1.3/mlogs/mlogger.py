#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/9 3:25 PM
# @Author  : chenDing
import sys

from .flie_logger import FileLogger


class MLogger(FileLogger):
    """同时输出到 terminal 和 文件"""
    def __init__(self, log_path=None, rotation="50 MB", retention=10, **kwargs):
        """
        :param log_path: 日志文件路径（绝对路径）
        :param kwargs:
        """
        super().__init__(log_path, rotation, retention, **kwargs)
        self._new_config["handlers"].append(
            {
                "sink": sys.stdout,
                **self._common_conf
            }
        )
        self._logger.remove()  # 删去import logger之后自动产生的handler，不删除的话会出现重复输出的现象
        self._logger.configure(**self._new_config)
