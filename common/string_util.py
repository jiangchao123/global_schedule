#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/7/21 16:53
Author  : jiangchao08
Site    : 
File    : string_util.py
Software: PyCharm Community Edition

"""


def stringToVector(sourceStr):
    """
    按照|对字符串进行切分
    :param sourceStr:
    :return:
    """
    try:
        results = sourceStr.split('|')
        floatRes = []
        for res in results:
            floatRes.append(float(res))
        return floatRes
    except AttributeError:
        return []
    except TypeError:
        return []
