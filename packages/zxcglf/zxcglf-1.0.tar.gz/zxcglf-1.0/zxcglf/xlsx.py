#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import openpyxl


def xlsx_open(file_path):
    """
    给定一个xlsx文件的路径，将其作为一个变量返回
    """
    wb = openpyxl.load_workbook(file_path)
    return wb


def xlsx_open_sheet(workbook, sheetname=""):
    if sheetname == "":
        print("所有工作表：", workbook.get_sheet_names())
        sheetname = input("请输入要打开的工作表：")
    else:
        pass
    sheet = workbook["%s" % sheetname]
    return sheet
