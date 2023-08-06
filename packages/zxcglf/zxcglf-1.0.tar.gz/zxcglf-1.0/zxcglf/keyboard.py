#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pyautogui

'''
由于实现原理较为简单，在这里不详细说明，若存在疑问请参阅pypi或github上的README文件
'''


def keyboard_type_string(sentence, interval=0):
    pyautogui.typewrite(message=sentence, interval=interval)


def keyboard_press(keys):
    pyautogui.press(keys)


def keyboard_down(key):
    pyautogui.keyDown(key)


def keyboard_up(key):
    pyautogui.keyUp(key)


def keyboard_hotkey(*args, **kwargs):
    pyautogui.hotkey(*args, **kwargs)
