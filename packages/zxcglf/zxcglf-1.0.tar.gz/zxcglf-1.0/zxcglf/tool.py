#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from zyr import system


def tool_shutdown_computer(time=0):
    """
    给定一个时间，单位为分钟，将在该时间后关闭计算机，若缺省则为0
    :param time: 剩余关机时间，若缺省则为0
    :return: 仅在遇到不支持的操作系统时返回提示信息
    """
    system_type = system.system_type_get()
    if system_type == "Windows":
        os.system("shutdown -s -t %s" % str(time * 60))
    elif system_type == "Linux":
        os.system("shutdown -h +%s" % time)
    elif system_type == "MacOS":
        os.system("sudo shutdown -h +%s" % time)
    else:
        return "系统不受支持！问题出现在 tool_shutdown_computer 函数体，详情请阅读zyr模块README文件。"
