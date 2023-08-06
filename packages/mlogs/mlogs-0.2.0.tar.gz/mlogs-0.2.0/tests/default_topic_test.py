#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/3/3 11:30 AM
# @Author  : chenDing
from mlogs import StdoutLogger

L1 = StdoutLogger(default_topic="1")
L2 = StdoutLogger(default_topic="2")
L3 = StdoutLogger(default_topic="3")

L1.info('nice')
L2.info('nice')
L3.info('nice')
