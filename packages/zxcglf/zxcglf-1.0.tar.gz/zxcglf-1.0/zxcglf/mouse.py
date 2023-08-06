#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pyautogui

'''
由于实现原理较为简单，在这里不详细说明，若存在疑问请参阅pypi或github上的README文件
'''


def mouse_move(x, y, duration=0):
    pyautogui.moveTo(x, y, duration=duration)


def mouse_click_left(x, y):
    pyautogui.click(x, y, button='left')


def mouse_click_right(x, y):
    pyautogui.click(x, y, button='right')


def mouse_click_middle(x, y):
    pyautogui.middleClick(x, y)


def mouse_get_position():
    position = pyautogui.position()
    return position


def mouse_drag(x, y, duration=0):
    pyautogui.dragTo(x, y, duration=duration)


def mouse_scroll_up(x):
    pyautogui.scroll(x)


def mouse_scroll_down(x):
    pyautogui.scroll(-x)
