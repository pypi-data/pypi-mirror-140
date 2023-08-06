#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/9 6:17 PM
# @Author  : chenDing
from .base_logger import BaseLogger


class StdoutLogger(BaseLogger):
    """日志仅输出到 terminal"""
