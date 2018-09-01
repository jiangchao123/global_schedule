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


class Job(object):
    def __init__(self, jobId=None, cpu=None, mem=None, nums=None, run_time=None, pre_jobs=None):
        self.jobId = jobId
        self.cpu = cpu
        self.mem = mem
        self.nums = nums
        self.run_time = run_time
        self.pre_jobs = pre_jobs
        self.finish_time = None
