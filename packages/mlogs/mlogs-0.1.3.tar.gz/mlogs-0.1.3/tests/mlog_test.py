#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/2/9 3:26 PM
# @Author  : chenDing
from mlogs import MLogger, AdaptHistoryLogger

mlog = MLogger()
dd = {
    'msg': "This is log debug!",
    "tts": 'hahnic'
}
mlog.debug(dd, request_id='nice', topic='hhh')
mlog.info("This is log info!")
mlog.warning("This is log warn!")
mlog.error("This is log error!")

L = AdaptHistoryLogger()
L.debug('nice', 'hhh', dd)
L.info('nice', 'hhh', "This is log info!")
L.warning('nice', 'hhh', "This is log warn!")
L.error('nice', 'hhh', "This is log error!")

_conf = {
    "sink": "out.log",
}
L2 = AdaptHistoryLogger(_conf)
L2.error('nice', 'hhh', "This is log error!")


def func(a, b):
    return a / b


def nested(c):
    try:
        func(5, c)
    except ZeroDivisionError:
        mlog.exception("What?!")


nested(0)
