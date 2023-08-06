#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2 as cv


def img_read(img_path):
    """
    给定图片的路径，返回带有图片的变量
    :param img_path: 图片的路径，必须不含中文字符
    :return: 带有图片的变量
    """
    pic = cv.imread(img_path)
    return pic


def img_gray(file):
    """
    给定一张图片，返回转化为灰度图片的该图的变量
    :param file:图片变量
    :return: 转化为灰度图片的该图的变量
    """
    gray = cv.cvtColor(file, cv.COLOR_BGR2GRAY)
    return gray


def img_display(file, window_title="", delay=0, destroy=1):
    """
    给定一张图片，然后显示
    :param file: 图片变量
    :param window_title: 窗口的标题，必须不含中文字符，缺省则为空
    :param delay: 等待键盘输入以关闭窗口的时间，单位：秒，缺省则为0，意为无限等待
    :param destroy: 执行完成后是否自动关闭窗口，默认为1，意为关闭，0则不关闭
    :return: 无返回值
    """
    cv.imshow(window_title, file)
    cv.waitKey(delay * 1000)
    if destroy == 1:
        cv.destroyAllWindows()
    elif destroy == 0:
        pass
    else:
        print("传递的“destroy”参数错误，将执行缺省值")
        cv.destroyAllWindows()


def img_resize(file, width, height):
    """
    给定一张图片，转换的目标宽高，返回改变长宽后的图片
    :param file: 图片变量
    :param width: 目标宽度
    :param height: 目标高度
    :return: 改变长宽后的图片变量
    """
    resize = cv.resize(file, dsize=(width, height))
    return resize
