#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import win32ui
import os


def file_list(path, file_type=""):
    """
    给定路径以及文件拓展名
    返回一个含有该目录下指定拓展名的文件的列表
    当文件拓展名参数被缺省时
    将返回一个含有该路径下所有的文件以及文件夹的列表
    """
    files = os.listdir(path)
    if file_type == "":
        return files
    else:
        i = 0
        files_selected = []
        while i < len(files):
            if ".%s" % file_type in files[i]:
                files_selected.append(files[i])
            else:
                pass
            i = i + 1
        return files_selected


def file_select(index_path):
    """
    给定一个主页路径
    打开文件选择器浏览文件
    若直接关闭文件选择器，将无法跳出循环
    """
    while 1:
        dlg = win32ui.CreateFileDialog(1)
        dlg.SetOFNInitialDir(index_path)
        dlg.DoModal()
        filename = dlg.GetPathName()
        if filename == "":
            pass
        else:
            return filename


def file_folder_create_if_non_exist(folder_path):
    """
    检查目录是否存在
    若不存在则创建
    """
    if os.path.exists(folder_path):
        pass
    else:
        os.mkdir(folder_path)


def file_file_create_if_non_exist(root_path, file_name, file_type=""):
    """
    检查文件及其根目录是否存在
    若不存在则创建
    拓展名可缺省
    """
    file_folder_create_if_non_exist(root_path)
    if file_type == "":
        file = root_path + "\\%s" % file_name
    else:
        file = root_path + "\\%s.%s" % (file_name, file_type)
    if not os.path.exists(file):
        open(file, "w").close()
    else:
        pass


def file_file_exist(file_path):
    """
    检查一个文件是否存在
    若不存在则返回False
    存在则返回True
    """
    return os.path.exists(file_path)
