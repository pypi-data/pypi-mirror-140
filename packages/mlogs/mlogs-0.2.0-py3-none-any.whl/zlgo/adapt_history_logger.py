#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/9 3:27 PM
# @Author  : chenDing
from .base_logger import BaseLogger


class AdaptHistoryLogger(BaseLogger):
    """兼容历史日志"""

    def __init__(self, config=None, level=None):
        """
        :param config:  loguru 配置
        :param level:  指定日志 级别
        """
        super().__init__(config, level)

    def debug(self, request_id, topic, msg):
        self._logger.bind(call_info=self._call_info()).debug(self._format_args(msg, request_id, topic))

    def info(self, request_id, topic, msg):
        self._logger.bind(call_info=self._call_info()).info(self._format_args(msg, request_id, topic))

    def warning(self, request_id, topic, msg):
        self._logger.bind(call_info=self._call_info()).warning(self._format_args(msg, request_id, topic))

    def error(self, request_id, topic, msg):
        self._logger.bind(call_info=self._call_info()).error(self._format_args(msg, request_id, topic))

    def critical(self, request_id, topic, msg):
        self._logger.bind(call_info=self._call_info()).critical(self._format_args(msg, request_id, topic))

    def exception(self, request_id, topic, msg):
        self._logger.bind(call_info=self._call_info()).exception(self._format_args(msg, request_id, topic))
