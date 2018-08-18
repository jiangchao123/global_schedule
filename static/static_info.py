#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/8/15 10:25
Author  : jiangchao08
Site    : 
File    : static_info.py
Software: PyCharm Community Edition

"""
T = 98


def static_machine(machine_instances_map, machinesMap, appsMap):
    """
    统计每台机器的当前状态
    :param machine_instances_map:
    :return:
    """
    for machineId, instances in machine_instances_map.items():
        print('machine', machineId, machinesMap[machineId].cpu, machinesMap[machineId].mem,
              machinesMap[machineId].disk, machinesMap[machineId].p, machinesMap[machineId].m,
              machinesMap[machineId].pm)
        cpus = [0 for i in range(T)]
        cpus_ratio = [0 for i in range(T)]
        mems = [0 for i in range(T)]
        mems_ratio = [0 for i in range(T)]
        disk = 0
        p = 0
        m = 0
        pm = 0
        for instance in instances:
            app = appsMap[instance.appId]
            for i in range(T):
                cpus[i] += app.cpus[i]
                mems[i] += app.mems[i]
            disk += app.disk
            p += app.p
            m += app.m
            pm += app.pm
        for i in range(T):
            cpus_ratio[i] = cpus[i] / machinesMap[machineId].cpu
            mems_ratio[i] = mems[i] / machinesMap[machineId].mem
        print('cpu use:', cpus, cpus_ratio)
        print('mem use:', mems, mems_ratio)
        print('disk use:', disk, disk / machinesMap[machineId].disk)
        print('p use:', p, p / machinesMap[machineId].p)
        print('m use:', m, m / machinesMap[machineId].m)
        print('pm use:', pm, pm / machinesMap[machineId].pm)
