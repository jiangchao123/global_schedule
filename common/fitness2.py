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


def disk_over_num(machine_instances_map, machinesMap, appsMap):
    over_num = 0
    for machineId, instances in machine_instances_map.items():
        disk = 0
        for instance in instances:
            disk += appsMap[instance.appId].disk
        if disk > machinesMap[machineId].disk:
            over_num += 1
    return over_num


def mem_over_num(machine_instances_map, machinesMap, appsMap):
    over_num = 0
    for machineId, instances in machine_instances_map.items():
        mem_list = np.zeros(T)
        for instance in instances:
            mem_list += appsMap[instance.appId].mems
        for mem in mem_list:
            if mem > machinesMap[machineId].mem:
                over_num += 1
                break
    return over_num


def app_interference_over_num(machine_instances_map, instance_interferences):
    over_num = 0
    for machineId, instances in machine_instances_map.items():
        instances_num_map = {}
        for instance in instances:
            if instances_num_map.get(instance.appId) is None:
                instances_num_map[instance.appId] = 0
            instances_num_map[instance.appId] += 1
        for appId, num in instances_num_map.items():
            conflictAppMap = instance_interferences.get(appId)
            if conflictAppMap is None:
                continue
            for appId2, num2 in conflictAppMap.items():
                if instance.appId == appId2:
                    if appId == appId2:
                        if instances_num_map[appId2] > num2:
                            over_num += 1
                    elif instances_num_map.get(appId2) is not None:
                        if instances_num_map[appId2] + 1 > num2:
                            over_num += 1
    return over_num


def m_over_num(machine_instances_map, machinesMap, appsMap):
    over_num = 0
    for machineId, instances in machine_instances_map.items():
        m = 0
        for instance in instances:
            m += appsMap[instance.appId].m
        if m > machinesMap[machineId].m:
            over_num += 1
    return over_num


def p_over_num(machine_instances_map, machinesMap, appsMap):
    over_num = 0
    for machineId, instances in machine_instances_map.items():
        p = 0
        for instance in instances:
            p += appsMap[instance.appId].p
        if p > machinesMap[machineId].p:
            over_num += 1
    return over_num


def pm_over_num(machine_instances_map, machinesMap, appsMap):
    over_num = 0
    for machineId, instances in machine_instances_map.items():
        pm = 0
        for instance in instances:
            pm += appsMap[instance.appId].pm
        if pm > machinesMap[machineId].pm:
            over_num += 1
    return over_num


# 目标函数
def fitnessfun(machine_instances_map, machinesMap, appsMap, instance_interferences, assignSize,
               instanceSize):
    """
    目标函数
    :param X:
    :return:
    """

    total_obj = None
    # print('assignSize', assignSize, 'instanceSize', instanceSize)
    if assignSize < instanceSize:
        # print('assignSize', assignSize, 'instanceSize', instanceSize)
        total_obj = 50000
    # over_num = 0
    # over_num += disk_over_num(machine_instances_map, machinesMap, appsMap)
    # over_num += mem_over_num(machine_instances_map, machinesMap, appsMap)
    # over_num += app_interference_over_num(machine_instances_map, instance_interferences)
    # over_num += m_over_num(machine_instances_map, machinesMap, appsMap)
    # over_num += p_over_num(machine_instances_map, machinesMap, appsMap)
    # over_num += pm_over_num(machine_instances_map, machinesMap, appsMap)
    # if total_obj is None:
    #     total_obj = over_num * 1000
    # else:
    #     total_obj += (over_num * 1000)

    for machineId, instances in machine_instances_map.items():
        val = 0
        machine = machinesMap[machineId]
        if len(instances) <= 0:
            print('未分配机器：', machineId, machine)
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
    return total_cost_score
