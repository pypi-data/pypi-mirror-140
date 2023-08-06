#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from zyr.time import time_now_get


def debug_normal(text):  # 普通调试
    """
    传入一个字符串，在其最前方加入[DEBUG]字样
    这样做虽然需要给每个语句加入注释，
    但能方便找出具体错误位置和原因，
    也可做成日志系统
    """
    print("[DEBUG]%s" % text)


def debug_with_time(text, accuracy):  # 带时间追踪的调试
    """
    传入一个字符串，在其最前方加入[DEBUG]字样，
    相比于debug()，加入了时间戳，
    这样做虽然需要给每个语句加入注释，
    但能方便找出具体错误位置和原因，
    也可做成带时间记录的日志系统
    """
    print("[DEBUG,%s]%s" % (time_now_get(accuracy), text))


def debug_error_notice(source="", text="", passage="", printout=1):
    """
    给定错误来源和错误提示内容，将给予相应提示
    :param source: 错误来源,仅在passage参数不为空时允许缺省
    :param text: 错误提示内容,仅在passage参数不为空时允许缺省
    :param passage: 错误提示的头部文字，若缺省则使用DEBUG功能的默认头部‍，且此时参数source、text不允许缺省
    :param printout: 是否输出为印屏幕，1为是，0为否，若缺省则印屏幕，2为印屏幕同时返回，否则返回为字符串
    :return: 返回错误信息字符串，仅在printout参数为0或2时生效
    """
    if passage == "":
        text = "[DEBUG]", "在运行时发现了一个致命错误，程序设计者提供的报告指出它来自：%s，错误内容如下：%s" % (source, text)
    else:
        text = "[DEBUG]%s" % passage
    if printout == 0:
        return text
    elif printout == 1:
        print(text)
    elif printout == 2:
        print(text)
        return text
    else:
        return "形参错误！问题形参出现在 debug_error_notice 函数体，问题形参为printout：是否输出为印屏幕错误，详情请阅读zyr模块README文件。"
