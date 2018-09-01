#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/7/21 16:43
Author  : jiangchao08
Site    : 
File    : fitness.py
Software: PyCharm Community Edition

"""
import numpy as np

alpha = 10
beta = 0.5
T = 98


# 目标函数
def fitnessfun(machine_instances_map, machinesMap, appsMap, assignSize, instanceSize):
    """
    目标函数
    :param X:
    :return:
    """
    notAssignMachineCount = 0
    instance_count = 0
    total_obj = None
    print('assignSize', assignSize, 'instanceSize', instanceSize)
    if assignSize < instanceSize:
        # print('assignSize', assignSize, 'instanceSize', instanceSize)
        total_obj = 50000 * (instanceSize - assignSize)
    for machineId, instances in machine_instances_map.items():
        val = 0
        if len(instances) <= 0:
            # print('未分配机器：', machineId, machine)
            notAssignMachineCount += 1
            continue
        machine = machinesMap[machineId]
        instance_count += len(instances)
        for i in range(T):
            cpu = 0
            for instance in instances:
                app = appsMap[instance.appId]
                cpu += app.cpus[i]
            cpuUseRate = cpu / machine.cpu
            s = 1 + alpha * (np.e ** max(0, cpuUseRate - beta) - 1)
            val += s
        if total_obj is None:
            total_obj = val
        else:
            total_obj += val
    total_cost_score = total_obj / T
    print('共多少台机器未分配实例 ', notAssignMachineCount, ' 分配实例数量：', instance_count)
    print('total score:', total_cost_score)
    return total_cost_score
