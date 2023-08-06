# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import time
import borax.calendars


def time_now_get(accuracy):  # 返回当前已格式化的时间
    """
    该函数提供日期
    通过给定精度参数，
    精度表示可使用中文，
    若使用英文须以"."分隔
    返回当前的具体日期，
    最终日期数据通过变量now_time返回
    精度参数为"0"时相当于返回时分秒，
    精度参数为"1"时相当于返回时分秒毫秒
    """
    accuracy = str(accuracy)
    if accuracy.lower() == "s".lower() or accuracy == "秒钟" or accuracy == "秒":
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    elif accuracy.lower() == "ms".lower() or accuracy == "毫秒":
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    elif accuracy.lower() == "m".lower or accuracy == "分钟" or accuracy == "分":
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    elif accuracy.lower() == "h".lower() or accuracy == "小时" or accuracy == "时":
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H')
    elif accuracy.lower() == "d".lower() or accuracy == "天" or accuracy == "日":
        now_time = datetime.datetime.now().strftime('%d')
    elif accuracy.lower() == "month".lower() or accuracy == "月":
        now_time = datetime.datetime.now().strftime('%m')
    elif accuracy.lower() == "y".lower() or accuracy == "年":
        now_time = datetime.datetime.now().strftime('%Y')
    elif accuracy.lower() == "h.m.s".lower() or accuracy == "分秒":
        now_time = datetime.datetime.now().strftime('%M:%S')
    elif accuracy.lower() == "h.m.s".lower() or accuracy == "时分秒" or accuracy == "0":
        now_time = datetime.datetime.now().strftime('%H:%M:%S')
    elif accuracy.lower() == "d.h.m.s".lower() or accuracy == "日时分秒":
        now_time = datetime.datetime.now().strftime('%d %H:%M:%S')
    elif accuracy.lower() == "month.d.h.m.s".lower() or accuracy == "月日时分秒":
        now_time = datetime.datetime.now().strftime('%m-%d %H:%M:%S')
    elif accuracy.lower() == "y.d.h.m.s".lower() or accuracy == "年月日时分秒":
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    elif accuracy.lower() == "h.m.s.ms".lower() or accuracy == "时分秒毫秒 " or accuracy == "1":
        now_time = datetime.datetime.now().strftime('%H:%M:%S.%f')
    elif accuracy.lower() == "d.h.m.s.ms".lower() or accuracy == "日时分秒毫秒":
        now_time = datetime.datetime.now().strftime('%d %H:%M:%S.%f')
    elif accuracy.lower() == "month.d.h.m.s.ms".lower() or accuracy == "月日时分秒毫秒":
        now_time = datetime.datetime.now().strftime('%m-%d %H:%M:%S.%f')
    elif accuracy.lower() == "y.d.h.m.s.ms".lower() or accuracy == "年月日时分秒毫秒":
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    elif accuracy.lower() == "y.m.d".lower() or accuracy == "年月日":
        now_time = datetime.datetime.now().strftime('%Y-%m-%d')
    else:
        now_time = "形参错误！问题形参出现在 time_now_get 函数体，问题形参为accuracy：格式化的时间精度错误，详情请阅读zyr模块README文件。"
    return now_time


def time_change_stamp(stamp, accuracy):
    """
    将时间戳转换为时间
    将返回格式化的时间
    精度格式同time_now_get()
    """
    if "毫秒" in accuracy:
        print("时间戳精度不应存在 毫秒")
    else:
        pass
    local_time = time.localtime(stamp)
    if accuracy.lower() == "s".lower() or accuracy == "秒钟" or accuracy == "秒":
        time_changed = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
    elif accuracy.lower() == "m".lower or accuracy == "分钟" or accuracy == "分":
        time_changed = time.strftime('%Y-%m-%d %H:%M', local_time)
    elif accuracy.lower() == "h".lower() or accuracy == "小时" or accuracy == "时":
        time_changed = time.strftime('%Y-%m-%d %H', local_time)
    elif accuracy.lower() == "d".lower() or accuracy == "天" or accuracy == "日":
        time_changed = time.strftime('%d', local_time)
    elif accuracy.lower() == "month".lower() or accuracy == "月":
        time_changed = time.strftime('%m', local_time)
    elif accuracy.lower() == "y".lower() or accuracy == "年":
        time_changed = time.strftime('%Y', local_time)
    elif accuracy.lower() == "h.m.s".lower() or accuracy == "分秒":
        time_changed = time.strftime('%M:%S', local_time)
    elif accuracy.lower() == "h.m.s".lower() or accuracy == "时分秒" or accuracy == "0":
        time_changed = time.strftime('%H:%M:%S', local_time)
    elif accuracy.lower() == "d.h.m.s".lower() or accuracy == "日时分秒":
        time_changed = time.strftime('%d %H:%M:%S', local_time)
    elif accuracy.lower() == "month.d.h.m.s".lower() or accuracy == "月日时分秒":
        time_changed = time.strftime('%m-%d %H:%M:%S', local_time)
    elif accuracy.lower() == "y.d.h.m.s".lower() or accuracy == "年月日时分秒":
        time_changed = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
    elif accuracy.lower() == "y.m.d".lower() or accuracy == "年月日":
        time_changed = time.strftime('%Y-%m-%d', local_time)
    else:
        time_changed = "形参错误！问题形参出现在 time_change_stamp 函数体，问题形参为accuracy：格式化的时间精度错误，详情请阅读zyr模块README文件。"
    return time_changed


def time_lunar_now_get(accuracy=""):
    """
    返回当前日期下的农历日期
    :param accuracy: 给定一个时间精度参数(形如:年月日)，参数缺省则为数字日期
    :return: 按照精度返回当前日期下的农历日期
    """
    lunar_date = borax.calendars.LunarDate.from_solar_date(int(time_now_get("年")), int(time_now_get("月")),
                                                           int(time_now_get("日")))
    if accuracy == "":
        return lunar_date
    elif accuracy == "年":
        return lunar_date.year
    elif accuracy == "月":
        return lunar_date.month
    elif accuracy == "日":
        return lunar_date.day
    elif accuracy == "年月":
        return lunar_date.year, lunar_date.month
    elif accuracy == "月日":
        return lunar_date.month, lunar_date.day
    elif accuracy == "年日":
        return lunar_date.year, lunar_date.day
    elif accuracy == "年月日":
        return lunar_date.year, lunar_date.month, lunar_date.day
    elif accuracy == "中年":
        return lunar_date.cn_year
    elif accuracy == "中月":
        return lunar_date.cn_month
    elif accuracy == "中日":
        return lunar_date.cn_day
    elif accuracy == "中年月":
        return lunar_date.cn_year + lunar_date.cn_month
    elif accuracy == "中月日":
        return lunar_date.cn_month + lunar_date.cn_day
    elif accuracy == "中年日":
        return lunar_date.cn_year + lunar_date.cn_day
    elif accuracy == "中年月日":
        return lunar_date.cn_year + lunar_date.cn_month + lunar_date.cn_day
    else:
        return "形参错误！问题形参出现在 time_lunar_now_get 函数体，问题形参为accuracy：给定的时间精度错误，详情请阅读zyr模块README文件。"


def time_lunar_from_solar(year, month, day, accuracy=""):
    """
    给定一个公历日期，返回对应农历日期，仅支持1900-2100年
    :param year: 公历日期年份
    :param month: 公历日期月份
    :param day: 公历日期日
    :param accuracy: 给定一个时间精度参数(形如:年月日)，参数缺省则为数字日期
    :return: 按照精度返回对应公历日期下的农历日期
    """
    lunar_date = borax.calendars.LunarDate.from_solar_date(year, month, day)
    if accuracy == "":
        return lunar_date
    elif accuracy == "年":
        return lunar_date.year
    elif accuracy == "月":
        return lunar_date.month
    elif accuracy == "日":
        return lunar_date.day
    elif accuracy == "年月":
        return lunar_date.year, lunar_date.month
    elif accuracy == "月日":
        return lunar_date.month, lunar_date.day
    elif accuracy == "年日":
        return lunar_date.year, lunar_date.day
    elif accuracy == "年月日":
        return lunar_date.year, lunar_date.month, lunar_date.day
    elif accuracy == "中年":
        return lunar_date.cn_year
    elif accuracy == "中月":
        return lunar_date.cn_month
    elif accuracy == "中日":
        return lunar_date.cn_day
    elif accuracy == "中年月":
        return lunar_date.cn_year + lunar_date.cn_month
    elif accuracy == "中月日":
        return lunar_date.cn_month + lunar_date.cn_day
    elif accuracy == "中年日":
        return lunar_date.cn_year + lunar_date.cn_day
    elif accuracy == "中年月日":
        return lunar_date.cn_year + lunar_date.cn_month + lunar_date.cn_day
    else:
        return "形参错误！问题形参出现在 time_lunar_now_get 函数体，问题形参为accuracy：给定的时间精度错误，详情请阅读zyr模块README文件。"


def time_lunar_now_get_animal():
    """
    获取当前农历日期对应的的属相
    :return: 当前农历日期对应的属相
    """
    lunar_date = borax.calendars.LunarDate.from_solar_date(int(time_now_get("年")), int(time_now_get("月")),
                                                           int(time_now_get("日")))
    animal = lunar_date.animal
    return animal


def time_lunar_from_solar_animal(year, month, day):
    """
    给定一个公历日期，返回对应农历日期对应的的属相
    :param year: 公历日期年份
    :param month: 公历日期月份
    :param day: 公历日期日
    :return: 返回给定的公历日期对应的农历日期对应的的属相
    """
    lunar_date = borax.calendars.LunarDate.from_solar_date(year, month, day)
    animal = lunar_date.animal
    return animal


def time_lunar_to_solar(year, month, day):
    """
    给定一个农历日期，返回对应公历日期
    :param year: 农历日期年份
    :param month: 农历日期月份
    :param day: 农历日期日
    :return: 返回给定农历日期对应的公历日期
    """
    day = borax.calendars.LunarDate(year, month, day)
    return day.to_solar_date()
