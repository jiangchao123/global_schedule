#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/7/22 09:28
Author  : jiangchao08
Site    : 
File    : test.py
Software: PyCharm Community Edition

"""

print([5 for i in range(4)])
a = set()
a.add((1,2))
a.add((3,4))
if (1,2) in a:
    print('---------')
if (3,4) in a:
    print('==========')


length_map = {}
length_map[11] = 55
length_map[2] = 33
length_map[12] = 44

lengthList = sorted(length_map.items())
print(lengthList)