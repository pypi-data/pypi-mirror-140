#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/3/2 2:11 PM
# @Author  : chenDing
"""
email 发送邮件，使用的是python 原生库 smtplib.SMTP
⚠️ 注意账号隐私问题。此库为公共库。
"""
from mlogs import StdoutLogger

alerts = {
    "alerts_type": "email",
    "params": {
        "username": "chending@gostudy.ai",
        "password": "YZ2kaDaeFeCGLacD",
        "host": "smtp.exmail.qq.com",  # 邮箱服务器地址
        "port": 465,  # 邮箱服务器端口
        "from": "chending@gostudy.ai",  # 邮件发送人
        "to": [
            "chending@gostudy.ai",  # 邮件接收人
        ],
        "login": True,
        "ssl": True,
    },
}

L = StdoutLogger(alerts=alerts)
L.error('nice')

# import notifiers
#
# params = {
#     "username": "chending@gostudy.ai",
#     "password": "YZ2kaDaeFeCGLacD",
#     "to": "chending@gostudy.ai",
#     "host": "smtp.exmail.qq.com",  # 邮箱服务器地址
#     "from": "chending@gostudy.ai",  # 邮件发送人
#     "port": 465,  # 邮箱服务器端口
#     "login": True,  # 手动登录
#     "ssl": True,  # 手动登录
# }
# notifier = notifiers.get_notifier("email")
# notifier.notify(raise_on_errors=True, message="The application is running!", **params)
