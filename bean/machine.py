#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/7/21 13:58
Author  : jiangchao08
Site    : 
File    : machine.py
Software: PyCharm Community Edition

"""


class Machine(object):
    def __init__(self, machineId=None, cpu=None, mem=None, disk=None, p=None, m=None, pm=None):
        self.machineId = machineId
        self.cpu = cpu
        self.mem = mem
        self.disk = disk
        self.p = p
        self.m = m
        self.pm = pm
