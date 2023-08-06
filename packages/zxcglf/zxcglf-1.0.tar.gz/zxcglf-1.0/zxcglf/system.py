#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import platform


def system_type_get():
    """
    返回操作系统的类型
    在Windows平台下返回"Windows"
    在Linux平台下返回"Linux"
    在MacOS平台下返回"MacOS"
    在其他平台下返回"Other"
    :return: 操作系统的类型
    """
    plt = platform.system()
    if plt == "Windows":
        system_type = "Windows"
    elif plt == "Linux" or "Linux".lower() in plt.lower():
        system_type = "Linux"
    elif plt == "Darwin":
        system_type = "MacOS"
    else:
        system_type = "Other"
    return system_type


def system_type_detail_get():
    """
    返回具体操作系统的类型
    :return: 具体操作系统的类型
    """
    system_type = platform.platform()
    return system_type
