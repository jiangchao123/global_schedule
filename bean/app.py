#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/7/21 16:28
Author  : jiangchao08
Site    : 
File    : app.py
Software: PyCharm Community Edition

"""


class App(object):
    def __init__(self, appId=None, cpus=None, mems=None, disk=None, p=None, m=None, pm=None):
        self.appId = appId
        self.cpus = cpus
        self.mems = mems
        self.disk = disk
        self.p = p
        self.m = m
        self.pm = pm
