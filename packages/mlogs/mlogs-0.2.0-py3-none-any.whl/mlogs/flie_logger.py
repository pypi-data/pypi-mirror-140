#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/9 4:17 PM
# @Author  : chenDing
import os
import sys
from inspect import getframeinfo, stack

from .base_logger import BaseLogger


def _log_filter(x):
    print(x)
    return x


class FileLogger(BaseLogger):
    """日志仅输出到 文件"""
    def __init__(self, log_path=None, rotation="50 MB", retention=10, **kwargs):
        """
        :param log_path: 日志文件路径（绝对路径）
        :param kwargs:
        """
        super().__init__(**kwargs)
        if not log_path:
            # print(stack())
            log_path = os.path.join(os.path.dirname(getframeinfo(stack()[1][0]).filename), "logs")
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        debug_log = os.path.join(log_path, "debug.log")
        info_log = os.path.join(log_path, "info.log")
        warning_log = os.path.join(log_path, "warning.log")
        error_log = os.path.join(log_path, "error.log")
        critical_log = os.path.join(log_path, "critical.log")
        exception_log = os.path.join(log_path, "exception.log")
        self._common_conf = {
            "level": self._LEVEL,
            # 使用队列，能解决多进程情况可能导致的日志被覆盖
            "enqueue": True,
            # 允许捕获具体错误 ⚠️ 这里可能导致敏感数据泄漏。使用时需要注意
            "backtrace": True,  # 允许显示整个堆栈
            "diagnose": True,
            # 自定义格式
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green>, <level>{level}</level>, "
                      "<cyan>{extra[call_info]}</cyan>, <level>{message}</level>",

        }
        self._common_conf_file = {
            "rotation": rotation,  # 默认 50 MB 分割
            "retention": retention,  # 默认 保留10 个日志文件
        }
        self._new_config = {
            "handlers": [
                {
                    "sink": debug_log,
                    "filter": lambda x: x["function"] == 'debug',
                    **self._common_conf,
                    **self._common_conf_file,
                },
                {
                    "sink": info_log,
                    "filter": lambda x: x["function"] == 'info',
                    **self._common_conf,
                    **self._common_conf_file,
                },
                {
                    "sink": warning_log,
                    "filter": lambda x: x["function"] == 'warning',
                    **self._common_conf,
                    **self._common_conf_file,
                },
                {
                    "sink": error_log,
                    "filter": lambda x: x["function"] == 'error',
                    **self._common_conf,
                    **self._common_conf_file,
                },
                {
                    "sink": critical_log,
                    "filter": lambda x: x["function"] == 'critical',
                    **self._common_conf,
                    **self._common_conf_file,
                },
                {
                    "sink": exception_log,
                    "filter": lambda x: x["function"] == 'exception',
                    **self._common_conf,
                    **self._common_conf_file,
                },
            ]
        }
        self._logger.remove()  # 删去import logger之后自动产生的handler，不删除的话会出现重复输出的现象
        self._logger.configure(**self._new_config)
