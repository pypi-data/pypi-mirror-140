#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/9 3:24 PM
# @Author  : chenDing
"""
loguru doc https://loguru.readthedocs.io/en/stable/overview.html#installation
notifiers https://notifiers.readthedocs.io/en/latest/usage.html#provider-schema
"""
import sys
import os
import json
from inspect import getframeinfo, stack

from loguru import logger
from notifiers.logging import NotificationHandler

from .utils import NumpyEncoder


class BaseLogger:
    def __init__(self, config=None, level=None, set_handler=None, alerts=None, **kwargs):
        """
        :param config:  loguru 配置，覆盖原本设置
        :param level:  强制覆盖 日志 级别
        :param set_handler:  拓展接口，传入一个函数支持自定义设置日志
        :param alerts:  报警配置接口，传入 dict
        """
        if os.environ.get('DEPLOYMENT') == 'PRODUCTION':
            self._LEVEL = 'INFO'
        else:
            self._LEVEL = 'DEBUG'
        if level:  # todo 添加 level 检查
            self._LEVEL = level
        if config and config.get("level"):
            self._LEVEL = config["level"]
        print(f"Environ: {os.environ.get('DEPLOYMENT', 'DEVELOP')}, log level is:{self._LEVEL}")
        config = config or {}
        alerts = alerts or {}
        _format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green>, <level>{level}</level>, " \
                  "<cyan>{extra[call_info]}</cyan>, <level>{message}</level>"
        new_config = {
            "sink": sys.stdout,
            "level": self._LEVEL,
            # 使用队列，能解决多进程情况可能导致的日志被覆盖
            "enqueue": True,
            # 允许捕获具体错误 ⚠️ 这里可能导致敏感数据泄漏。使用时需要注意
            "backtrace": True,  # 允许显示整个堆栈
            "diagnose": True,
            # 自定义格式
            "format": _format,
            # "colorize": True,   # 把颜色 输出到 日志，有些不兼容？
            **config
        }
        logger.remove()  # 删去import logger之后自动产生的handler，不删除的话会出现重复输出的现象
        logger.add(**new_config)
        if alerts:
            n_handler = NotificationHandler(alerts["alerts_type"], defaults=alerts.get("params"))
            logger.add(n_handler, level=alerts.get("alerts_level", "ERROR"), format=_format)
        if set_handler:  # 拓展接口，传入一个函数支持自定义设置日志
            set_handler(logger, **kwargs)
        self._logger = logger

    def debug(self, msg, request_id='', topic=''):
        self._logger.opt(colors=True).bind(call_info=self._call_info()).debug(self._format_args(msg, request_id, topic))

    def info(self, msg, request_id='', topic=''):
        self._logger.opt(colors=True).bind(call_info=self._call_info()).info(self._format_args(msg, request_id, topic))

    def warning(self, msg, request_id='', topic=''):
        self._logger.opt(colors=True).bind(call_info=self._call_info()).warning(
            self._format_args(msg, request_id, topic))

    def error(self, msg, request_id='', topic=''):
        self._logger.opt(colors=True).bind(call_info=self._call_info()).error(self._format_args(msg, request_id, topic))

    def critical(self, msg, request_id='', topic=''):
        self._logger.opt(colors=True).bind(call_info=self._call_info()).critical(
            self._format_args(msg, request_id, topic))

    def exception(self, msg, request_id='', topic=''):
        self._logger.opt(exception=True, colors=True).bind(call_info=self._call_info()).exception(
            self._format_args(msg, request_id, topic))

    def __getattr__(self, item):
        return getattr(logger, item)

    @staticmethod
    def _call_info():
        # print(stack())
        caller = getframeinfo(stack()[2][0])
        return f'{os.path.basename(caller.filename)}:{caller.function}:line {caller.lineno}'

    @staticmethod
    def _format_args(msg, request_id='', topic=''):
        if not isinstance(msg, dict):
            msg = {'log': msg}
        data = {**msg}
        if request_id:
            data["request_id"] = request_id
        if topic:
            data["request_id"] = topic
        json_str = json.dumps(data, ensure_ascii=False, cls=NumpyEncoder)
        return json_str[1:-1]  # 去掉前后括号
