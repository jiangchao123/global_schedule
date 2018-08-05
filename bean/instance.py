#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/7/21 13:59
Author  : jiangchao08
Site    : 
File    : instanse.py
Software: PyCharm Community Edition

"""


class Instance(object):
    def __init__(self, instanceId=None, appId=None, machineId=None, finalMachineId=None):
        self.instanceId = instanceId
        self.appId = appId
        self.machineId = machineId
        self.final_machineId = finalMachineId
