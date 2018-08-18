#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/7/22 00:25
Author  : jiangchao08
Site    : 
File    : produce_seed.py
Software: PyCharm Community Edition

"""
import numpy as np

alpha = 10
beta = 0.5
T = 98


def tell_p_constraint(instance, machine, appsMap, residual_machine_p):
    # instances = machine_instances_map[machine.machineId]
    # p_value = 0
    # for instance1 in instances:
    #     p_value += appsMap[instance1.appId].p
    # if p_value + appsMap[instance.appId].p > machine.p:
    #     return True
    # return False
    if appsMap[instance.appId].p > residual_machine_p[machine.machineId]:
        return True
    return False


def tell_m_constraint(instance, machine, appsMap, residual_machine_m):
    # instances = machine_instances_map[machine.machineId]
    # m_value = 0
    # for instance1 in instances:
    #     m_value += appsMap[instance1.appId].m
    # if m_value + appsMap[instance.appId].m > machine.m:
    #     return True
    # return False
    if appsMap[instance.appId].m > residual_machine_m[machine.machineId]:
        return True
    return False


def tell_pm_constraint(instance, machine, appsMap, residual_machine_pm):
    # instances = machine_instances_map[machine.machineId]
    # pm_value = 0
    # for instance1 in instances:
    #     pm_value += appsMap[instance1.appId].pm
    # if pm_value + appsMap[instance.appId].pm > machine.pm:
    #     return True
    # return False
    if appsMap[instance.appId].pm > residual_machine_pm[machine.machineId]:
        return True
    return False


def tell_cpu_constraint(instance, machine, appsMap, residual_machine_cpu):
    # instances = machine_instances_map[machine.machineId]
    # for i in range(T):
    #     cpu = 0
    #     for instance1 in instances:
    #         app = appsMap[instance1.appId]
    #         cpu += app.cpus[i]
    #     # print(appsMap[instance.appId].cpus[i])
    #     cpu += appsMap[instance.appId].cpus[i]
    #     if cpu > machine.cpu:
    #         return True
    # return False
    for i in range(T):
        if appsMap[instance.appId].cpus[i] > residual_machine_cpu[machine.machineId][i]:
            return True
    return False


def tell_mem_constraint(instance, machine, appsMap, residual_machine_mem):
    # instances = machine_instances_map[machine.machineId]
    # for i in range(T):
    #     mem = 0
    #     for instance1 in instances:
    #         app = appsMap[instance1.appId]
    #         mem += app.mems[i]
    #     mem += appsMap[instance.appId].mems[i]
    #     if mem > machine.mem:
    #         return True
    # return False
    for i in range(T):
        if appsMap[instance.appId].mems[i] > round(residual_machine_mem[machine.machineId][i], 12):
            # print('mem:', i, appsMap[instance.appId].mems[i],
            #       round(residual_machine_mem[machine.machineId][i], 12))
            return True
    return False


def tell_disk_constraint(instance, machine, appsMap, residual_machine_disk):
    # instances = machine_instances_map[machine.machineId]
    # disk_value = 0
    # for instance1 in instances:
    #     disk_value += appsMap[instance1.appId].disk
    # if disk_value + appsMap[instance.appId].disk > machine.disk:
    #     return True
    # return False
    if appsMap[instance.appId].disk > residual_machine_disk[machine.machineId]:
        print(instance.instanceId, machine.machineId, appsMap[instance.appId].disk, residual_machine_disk[machine.machineId])
        return True
    return False


def tell_app_interference_constraint(instance, machine, appsMap, machine_instances_num_map,
                                     instance_interferences, print_info=False):
    instances_num_map = machine_instances_num_map[machine.machineId]
    # 判断新的app在不在已有的app中的影响数组里
    for appId, num in instances_num_map.items():
        if num == 0:
            continue
        conflictAppMap = instance_interferences.get(appId)
        if conflictAppMap is None:
            continue
        for appId2, num2 in conflictAppMap.items():
            if instance.appId == appId2:
                if appId == appId2:
                    if instances_num_map[appId2] > num2:
                        return True
                else:
                    if print_info:
                        print(appId, appId2)
                    count = 0
                    if instances_num_map.get(appId2) is not None:
                        count = instances_num_map.get(appId2)
                    if count + 1 > num2:
                        return True

    # 判断新的app的影响数组里，包不包含已有的app
    conflictAppMap = instance_interferences.get(instance.appId)
    if conflictAppMap is None:
        return False
    # print(conflictAppMap)
    for appId, num in conflictAppMap.items():
        if instances_num_map.get(appId) is not None:
            if instances_num_map[appId] > num:
                return True
    return False


def compute_cpu_constraint(instance, machine, appsMap, used_machine_cpu, machine_cpu_score):
    # instances = machine_instances_map[machine.machineId]
    # for i in range(T):
    #     cpu = 0
    #     for instance1 in instances:
    #         app = appsMap[instance1.appId]
    #         cpu += app.cpus[i]
    #     # print(appsMap[instance.appId].cpus[i])
    #     cpu += appsMap[instance.appId].cpus[i]
    #     if cpu > machine.cpu:
    #         return True
    # return False
    # pre_score = sum(machine_cpu_score[machine.machineId])
    time_used = (np.array(used_machine_cpu[machine.machineId]) + np.array(
        appsMap[instance.appId].cpus)) / machine.cpu
    increment_score = 0
    for i in range(T):
        s = alpha * (np.e ** max(0, time_used[i] - beta) - 1)
        increment_score += s
    increment_score -= machine_cpu_score[machine.machineId]
    return increment_score


def randomGreedy(instances, appsMap, machinesList, instance_interferences):
    """
    贪心算法，生成不同的种子
    :param flights:
    :return:
    """
    machine_instances_map, residual_machine_p, residual_machine_m, residual_machine_pm, \
    residual_machine_disk, residual_machine_cpu, half_residual_machine_cpu, used_machine_cpu, \
    machine_cpu_score, residual_machine_mem, machine_instances_num_map = init_exist_instances(
        machinesList, 0.5)
    assignSize = 0
    app_half_index_map = {}
    app_index_map = {}
    for instance in instances:
        # print(instance, machine_instances_num_map)
        bestMachine = None
        min_increment_score = 9800
        index = 0
        if app_half_index_map.get(instance.appId) is not None:
            index = app_half_index_map[instance.appId]
        for i in range(index, len(machinesList)):
            machine = machinesList[i][1]
            # for machineId, machine in machinesList:
            # if machineId == 'machine_249':
            #     print('安排实例', instance.instanceId)
            if tell_disk_constraint(instance, machine, appsMap, residual_machine_disk):
                continue
            if tell_mem_constraint(instance, machine, appsMap, residual_machine_mem):
                continue
            if tell_app_interference_constraint(instance, machine, appsMap,
                                                machine_instances_num_map, instance_interferences):
                continue
            if tell_m_constraint(instance, machine, appsMap, residual_machine_m):
                continue
            if tell_p_constraint(instance, machine, appsMap, residual_machine_p):
                continue
            if tell_pm_constraint(instance, machine, appsMap, residual_machine_pm):
                continue
            if tell_cpu_constraint(instance, machine, appsMap, half_residual_machine_cpu):
                continue
            bestMachine = machine
            app_half_index_map[instance.appId] = i
            break
            # increment_score = compute_cpu_constraint(instance, machine, appsMap, used_machine_cpu,
            #                                          machine_cpu_score)
            # if increment_score == 0:
            #     bestMachine = machine
            #     break
            # else:
            #     if increment_score < min_increment_score:
            #         bestMachine = machine
            #         min_increment_score = increment_score
        if bestMachine is None:
            app_half_index_map[instance.appId] = len(machinesList)
            # print('第一次未分配instance:', instance.instanceId)
            index = 0
            if app_index_map.get(instance.appId) is not None:
                index = app_index_map[instance.appId]
            # 贪心兜底
            for i in range(index, len(machinesList)):
                machine = machinesList[i][1]
                # for machineId, machine in machinesList:
                # print(machineId)
                if tell_disk_constraint(instance, machine, appsMap, residual_machine_disk):
                    # print('无满足的disk')
                    continue
                if tell_mem_constraint(instance, machine, appsMap, residual_machine_mem):
                    # print('无满足的mem')
                    continue
                if tell_app_interference_constraint(instance, machine, appsMap,
                                                    machine_instances_num_map,
                                                    instance_interferences):
                    # print('无满足的inter')
                    continue
                if tell_m_constraint(instance, machine, appsMap, residual_machine_m):
                    # print('无满足的m')
                    continue
                if tell_p_constraint(instance, machine, appsMap, residual_machine_p):
                    # print('无满足p')
                    continue
                if tell_pm_constraint(instance, machine, appsMap, residual_machine_pm):
                    # print('无满足的pm')
                    continue
                if tell_cpu_constraint(instance, machine, appsMap, residual_machine_cpu):
                    # print('无满足的cpu')
                    continue
                bestMachine = machine
                app_index_map[instance.appId] = i
                break
        if bestMachine is None:
            app_index_map[instance.appId] = len(machinesList)
            print('第二次未分配instance:', instance.instanceId)

        if bestMachine is not None:
            # if machineId == 'machine_249':
            #     print('成功安排实例进机器', instance.instanceId, instance.appId, bestMachine.machineId)
            #     print('此实例cpu占用：', appsMap[instance.appId].cpus)
            machine_instances_map[bestMachine.machineId].append(instance)
            if machine_instances_num_map.get(bestMachine.machineId).get(instance.appId) is None:
                machine_instances_num_map[bestMachine.machineId][instance.appId] = 1
            else:
                machine_instances_num_map[bestMachine.machineId][instance.appId] += 1
            residual_machine_p[bestMachine.machineId] -= appsMap[instance.appId].p
            residual_machine_m[bestMachine.machineId] -= appsMap[instance.appId].m
            residual_machine_pm[bestMachine.machineId] -= appsMap[instance.appId].pm
            residual_machine_disk[bestMachine.machineId] -= appsMap[instance.appId].disk
            machine_cpu_score[bestMachine.machineId] += min_increment_score
            for i in range(T):
                residual_machine_cpu[bestMachine.machineId][i] -= appsMap[instance.appId].cpus[i]
                half_residual_machine_cpu[bestMachine.machineId][i] -= appsMap[instance.appId].cpus[
                    i]
                used_machine_cpu[bestMachine.machineId][i] += appsMap[instance.appId].cpus[i]
            for i in range(T):
                residual_machine_mem[bestMachine.machineId][i] -= appsMap[instance.appId].mems[i]
            assignSize += 1
            # if machineId == 'machine_249':
            #     print('剩余cpu:', residual_machine_cpu)
        if assignSize % 100 == 0:
            print(assignSize)
    return machine_instances_map, assignSize


# 初始化已经在机器上的实例
def init_exist_instances(machinesList, cpu_threhold=1):
    """
    初始化已经在机器上的实例
    :return:
    """
    machine_instances_map = {}
    machine_instances_num_map = {}
    residual_machine_cpu = {}
    half_residual_machine_cpu = {}
    used_machine_cpu = {}
    machine_cpu_score = {}
    residual_machine_mem = {}
    residual_machine_disk = {}
    residual_machine_p = {}
    residual_machine_m = {}
    residual_machine_pm = {}
    for machineId, machine in machinesList:
        machine_instances_map[machineId] = []
        residual_machine_p[machineId] = machine.p
        residual_machine_m[machineId] = machine.m
        residual_machine_pm[machineId] = machine.pm
        residual_machine_disk[machineId] = machine.disk
        residual_machine_cpu[machineId] = [machine.cpu for i in range(T)]
        used_machine_cpu[machineId] = [0 for i in range(T)]
        machine_cpu_score[machineId] = 0
        half_residual_machine_cpu[machineId] = [cpu_threhold * machine.cpu for i in range(T)]
        residual_machine_mem[machineId] = [machine.mem for i in range(T)]
        machine_instances_num_map[machineId] = {}
    return machine_instances_map, residual_machine_p, residual_machine_m, residual_machine_pm, \
           residual_machine_disk, residual_machine_cpu, half_residual_machine_cpu, used_machine_cpu, \
           machine_cpu_score, residual_machine_mem, machine_instances_num_map
