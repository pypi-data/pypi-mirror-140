#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import msvcrt


def password_get(text):
    """
    给定一个提示信息，程序将提供密码输入栏，用户输入回车标定为密码输入完成，用户输入退格删除一个字符，用户输入Esc清空密码栏
    :param text: 密码提示信息
    :return: 用户确认完成的密码
    """
    print("%s" % text, end='', flush=True)  # 关于输入的提示性信息
    pass_got = []  # 存放密码的列表
    while 1:
        key = msvcrt.getch()  # 获取键入
        if key == b'\r':  # 回车
            msvcrt.putch(b'\n')
            password_user = (b''.join(pass_got).decode())
            break
        elif key == b'\x08':  # 退格
            if pass_got:
                pass_got.pop()
                msvcrt.putch(b'\b')
                msvcrt.putch(b' ')
                msvcrt.putch(b'\b')
        elif key == b'\x1b':  # Esc
            while pass_got:
                pass_got.pop()
                msvcrt.putch(b'\b')
                msvcrt.putch(b' ')
                msvcrt.putch(b'\b')
        else:  # 其他
            pass_got.append(key)
            msvcrt.putch(b'*')
    return password_user
