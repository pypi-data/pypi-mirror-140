#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import winreg
import os


def path_desktop():
    """
    获取Windows系统下的桌面路径并返回
    """
    path = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    return winreg.QueryValueEx(path, "Desktop")[0]


def path_user():
    """
    获取Windows系统下的用户主目录路径并返回
    """
    path = os.path.expanduser('~')
    return path


def path_documents():
    """
    获取Windows系统下的用户文档目录路径并返回
    """
    path = path_user() + "\\Documents"
    return path


def path_downloads():
    """
    获取Windows系统下的用户下载目录路径并返回
    """
    path = path_user() + "\\Downloads"
    return path


def path_pictures():
    """
    获取Windows系统下的用户图片目录路径并返回
    """
    path = path_user() + "\\Pictures"
    return path


def path_videos():
    """
    获取Windows系统下的用户视频目录路径并返回
    """
    path = path_user() + "\\Videos"
    return path


def path_music():
    """
    获取Windows系统下的用户音乐目录路径并返回
    """
    path = path_user() + "\\Music"
    return path


def path_favorites():
    """
    获取Windows系统下的用户收藏目录路径并返回
    """
    path = path_user() + "\\Favorites"
    return path
