#!/usr/bin/env python
# coding=utf-8
#
# Copyright (c) 2018 Baidu.com, Inc. All Rights Reserved
#

"""
File: exe_time.py
Author: lixiaohui01(lixiaohui01@baidu.com)
Date: 2018/3/20 15:19
使用装饰器“@”取得函数执行时间
"""
import time


def exeTime(func):
    """
    取得函数执行时间
    :param func:
    :return:
    """
    def newFunc(*args, **args2):
        """
        装饰器“@”取得函数执行时间
        :param args:
        :param args2:
        :return:
        """
        t0 = time.time()
        # print("@%s, {%s} start" % (time.strftime("%X", time.localtime()), func.__name__))
        back = func(*args, **args2)
        # print("@%s, {%s} end" % (time.strftime("%X", time.localtime()), func.__name__))
        print("@%.3fs taken for {%s}" % (time.time() - t0, func.__name__))
        return back

    return newFunc
