#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import win32console
import win32gui
import win32con


def window_delete_button_close():
    hwnd = win32console.GetConsoleWindow()
    if hwnd:
        hmenu = win32gui.GetSystemMenu(hwnd, 0)
        if hmenu:
            win32gui.DeleteMenu(hmenu, win32con.SC_CLOSE, win32con.MF_BYCOMMAND)


def window_delete_button_max():
    hwnd = win32console.GetConsoleWindow()
    if hwnd:
        hmenu = win32gui.GetSystemMenu(hwnd, 0)
        if hmenu:
            win32gui.DeleteMenu(hmenu, win32con.SC_MAXIMIZE, win32con.MF_BYCOMMAND)


def window_delete_button_min():
    hwnd = win32console.GetConsoleWindow()
    if hwnd:
        hmenu = win32gui.GetSystemMenu(hwnd, 0)
        if hmenu:
            win32gui.DeleteMenu(hmenu, win32con.SC_MINIMIZE, win32con.MF_BYCOMMAND)


def window_delete_size():
    hwnd = win32console.GetConsoleWindow()
    if hwnd:
        hmenu = win32gui.GetSystemMenu(hwnd, 0)
        if hmenu:
            win32gui.DeleteMenu(hmenu, win32con.SC_SIZE, win32con.MF_BYCOMMAND)


def window_set_title(title):
    hwnd = win32console.GetConsoleWindow()
    if hwnd:
        win32console.SetConsoleTitle(title)
