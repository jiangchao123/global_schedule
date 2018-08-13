#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/8/12 02:01
Author  : jiangchao08
Site    : 
File    : static.py
Software: PyCharm Community Edition

"""
import pandas as pd


def static_num(filepath):
    """
    加载机器文件
    :param filepath:
    :return:
    """
    data_set = pd.read_csv(filepath, header=None, index_col=None)
    print(data_set.head())
    instancesMap = {}
    for row in data_set.values:
        instanceId = row[0]
        machineId = row[1]
        instancesMap[instanceId] = machineId
    print(len(instancesMap))
    return instancesMap

instancesMap = static_num('2018-8-7-b-final.csv')
instancesMap2 = static_num('2018-8-7-b-res.csv')

# print(instancesMap.keys() not in instancesMap2.keys())
for instanceId in instancesMap2.keys():
    if instanceId not in instancesMap.keys():
        print(instanceId)