#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/8/12 22:06
Author  : jiangchao08
Site    : 
File    : sa.py
Software: PyCharm Community Edition

"""
import common.fitness as fitness
import common.produce_seed as produce_seed
from common.exe_time import exeTime
import array
import random
import numpy as np
import pandas as pd
import data_preprocess.data_process as data_process
import static.static_info as static_tool

alpha = 10
beta = 0.5
T = 98

machinesMap, sortedMachineList = data_process.handle_machine(
    'data/scheduling_preliminary_machine_resources_20180606.csv')
for machineId, machine in sortedMachineList:
    print(machineId)
appsMap, sortedAppList = data_process.handle_app(
    'data/scheduling_preliminary_app_resources_20180606.csv')
instancesMap, sortedInstanceList = data_process.handle_instance(
    'data/scheduling_preliminary_instance_deploy_20180606.csv')
instance_interferences = data_process.handle_app_interference(
    'data/scheduling_preliminary_app_interference_20180606.csv')


def read_init_solution(filepath):
    data_set = pd.read_csv(filepath, header=None, index_col=None)
    print(len(data_set), data_set.head())
    machine_instances_map = {}
    instance_machine_map = {}
    for machineId, machine in sortedMachineList:
        machine_instances_map[machineId] = []
    for row in data_set.values:
        instanceId = row[0]
        machineId = row[1]
        instance_machine_map[instanceId] = machineId
        machine_instances_map[machineId].append(instancesMap.get(instanceId))
    fit = fitness.fitnessfun(machine_instances_map, machinesMap, appsMap, len(data_set),
                             len(instancesMap))
    return machine_instances_map, instance_machine_map, fit


machine_instances_map, instance_machine_map, fit = read_init_solution('2018-8-7-a-res.csv')
# static_tool.static_machine(machine_instances_map, machinesMap, appsMap)
print(fit)


def compute_machine_score(instances, machine):
    if instances is None or len(instances) == 0:
        return 0
    val = 0
    for i in range(T):
        cpu = 0
        for instance in instances:
            app = appsMap[instance.appId]
            cpu += app.cpus[i]
        cpuUseRate = cpu / machine.cpu
        s = 1 + alpha * (np.e ** max(0, cpuUseRate - beta) - 1)
        val += s
    return val / float(T)


def compute_residual_info(machine_instances_map):
    machine_apps_num_map = {}
    residual_machine_cpu = {}
    half_residual_machine_cpu = {}
    used_machine_cpu = {}
    machine_cpu_score = {}
    residual_machine_mem = {}
    residual_machine_disk = {}
    residual_machine_p = {}
    residual_machine_m = {}
    residual_machine_pm = {}
    for machineId, machine in sortedMachineList:

        machine_apps_num_map[machineId] = {}
        instances = machine_instances_map.get(machineId)
        residual_disk = machinesMap[machineId].disk
        residual_m = machinesMap[machineId].m
        residual_p = machinesMap[machineId].p
        residual_pm = machinesMap[machineId].pm
        residual_cpus = [machinesMap[machineId].cpu for i in range(T)]
        used_machine_cpu[machineId] = [0 for i in range(T)]
        residual_mems = [machinesMap[machineId].mem for i in range(T)]
        machine_cpu_score[machineId] = compute_machine_score(instances, machine)
        for instance in instances:
            residual_disk -= appsMap[instance.appId].disk
            residual_m -= appsMap[instance.appId].m
            residual_p -= appsMap[instance.appId].p
            residual_pm -= appsMap[instance.appId].pm
            for i in range(T):
                residual_cpus[i] -= appsMap[instance.appId].cpus[i]
                used_machine_cpu[machineId][i] += appsMap[instance.appId].cpus[i]
            for i in range(T):
                residual_mems[i] -= appsMap[instance.appId].mems[i]
            if machine_apps_num_map.get(machineId).get(instance.appId) is None:
                machine_apps_num_map[machineId][instance.appId] = 1
            else:
                machine_apps_num_map[machineId][instance.appId] += 1
        residual_machine_disk[machineId] = residual_disk
        residual_machine_m[machineId] = residual_m
        residual_machine_p[machineId] = residual_p
        residual_machine_pm[machineId] = residual_pm
        residual_machine_mem[machineId] = residual_mems
        residual_machine_cpu[machineId] = residual_cpus
    return residual_machine_p, residual_machine_m, residual_machine_pm, residual_machine_disk, \
           residual_machine_mem, used_machine_cpu, residual_machine_cpu, machine_apps_num_map, machine_cpu_score


residual_machine_p, residual_machine_m, residual_machine_pm, residual_machine_disk, \
residual_machine_mem, used_machine_cpu, residual_machine_cpu, machine_apps_num_map, machine_cpu_score = compute_residual_info(
    machine_instances_map)


def tell_app_interference_constraint(app, machineId, machine_instances_num_map,
                                     instance_interferences, print_info=False):
    instances_num_map = machine_instances_num_map[machineId]
    # 判断新的app在不在已有的app中的影响数组里
    for appId, num in instances_num_map.items():
        if num == 0:
            continue
        conflictAppMap = instance_interferences.get(appId)
        if conflictAppMap is None:
            continue
        for appId2, num2 in conflictAppMap.items():
            if app.appId == appId2:
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
    conflictAppMap = instance_interferences.get(app.appId)
    if conflictAppMap is None:
        return False
    # print(conflictAppMap)
    for appId, num in conflictAppMap.items():
        if instances_num_map.get(appId) is not None:
            if instances_num_map[appId] > num:
                return True
    return False


def tell_cross_constraint(machineId1, machineId2, app1, app2):
    if residual_machine_p[machineId1] < app2.p - app1.p or residual_machine_p[
        machineId2] < app1.p - app2.p:
        return True
    if residual_machine_m[machineId1] < app2.m - app1.m or residual_machine_m[
        machineId2] < app1.m - app2.m:
        return True
    if residual_machine_pm[machineId1] < app2.pm - app1.pm or residual_machine_pm[
        machineId2] < app1.pm - app2.pm:
        return True
    if residual_machine_disk[machineId1] < app2.disk - app1.disk or residual_machine_disk[
        machineId2] < app1.disk - app2.disk:
        return True
    for i in range(T):
        if residual_machine_mem[machineId1][i] < app2.mems[i] - app1.mems[i] or \
                        residual_machine_mem[machineId2][i] < app1.mems[i] - app2.mems[i]:
            return True
    if machine_apps_num_map[machineId1].get(app1.appId) is not None:
        machine_apps_num_map[machineId1][app1.appId] -= 1
        if tell_app_interference_constraint(app2, machineId1, machine_apps_num_map,
                                            instance_interferences):
            machine_apps_num_map[machineId1][app1.appId] += 1
            return True
    if machine_apps_num_map[machineId2].get(app2.appId) is not None:
        machine_apps_num_map[machineId2][app2.appId] -= 1
        if tell_app_interference_constraint(app1, machineId2, machine_apps_num_map,
                                            instance_interferences):
            machine_apps_num_map[machineId2][app2.appId] += 1
            return True
    return False


def tell_mut_constraint(machineId, app):
    if residual_machine_p[machineId] < app.p:
        return True
    if residual_machine_m[machineId] < app.m:
        return True
    if residual_machine_pm[machineId] < app.pm:
        return True
    if residual_machine_disk[machineId] < app.disk:
        return True
    for i in range(T):
        if residual_machine_mem[machineId][i] < app.mems[i]:
            return True
    if tell_app_interference_constraint(app, machineId, machine_apps_num_map,
                                        instance_interferences):
        return True
    return False


best_solution = None


def score_cross_change(app1, machine1, app2, machine2):
    machine_val1 = 0
    machine_val2 = 0
    for i in range(T):
        cpus = used_machine_cpu[machine1.machineId]
        cpus[i] += (app2.cpus[i] - app1.cpus[i])
        cpuUseRate = cpus[i] / machine1.cpu
        s = 1 + alpha * (np.e ** max(0, cpuUseRate - beta) - 1)
        machine_val1 += s
        cpus[i] -= (app2.cpus[i] - app1.cpus[i])
    for i in range(T):
        cpus = used_machine_cpu[machine2.machineId]
        cpus[i] += (app1.cpus[i] - app2.cpus[i])
        cpuUseRate = cpus[i] / machine2.cpu
        s = 1 + alpha * (np.e ** max(0, cpuUseRate - beta) - 1)
        machine_val1 += s
        cpus[i] -= (app1.cpus[i] - app2.cpus[i])
    return machine_val1 / float(T), machine_val2 / float(T)


def score_mut_change(machine, app):
    val = 0
    for i in range(T):
        cpus = used_machine_cpu[machine.machineId]
        cpus[i] += app.cpus[i]
        cpuUseRate = cpus[i] / machine.cpu
        s = 1 + alpha * (np.e ** max(0, cpuUseRate - beta) - 1)
        val += s
        cpus[i] -= app.cpus[i]
    return val / float(T)


def sa():
    T_current = 1000
    T_min = 50
    r = 0.8
    while T_current > T_min:
        change_list = []
        if random.random() < 0.5:
            # 交叉
            while True:
                instance_index1 = random.randint(0, len(instancesMap) - 1)
                instance_index2 = random.randint(0, len(instancesMap) - 1)
                app1 = appsMap.get(sortedInstanceList[instance_index1][1].appId)
                app2 = appsMap.get(sortedInstanceList[instance_index2][1].appId)
                machineId1 = instance_machine_map.get(sortedInstanceList[instance_index1][0])
                machineId2 = instance_machine_map.get(sortedInstanceList[instance_index2][0])
                if not tell_cross_constraint(machineId1, machineId2, app1, app2):
                    break
            change_list.append([sortedInstanceList[instance_index1][0], machineId2])
            change_list.append([sortedInstanceList[instance_index2][0], machineId1])
            machine_val1, machine_val2 = score_cross_change(app1, machinesMap[machineId1], app2,
                                                            machinesMap[machineId2])
            origin_val1 = machine_cpu_score[machineId1]
            origin_val2 = machine_cpu_score[machineId2]
            diff = (origin_val1 + origin_val2) - (machine_val1 + machine_val2)
            print('cross:', diff)
            if diff >= 0:
                for change in change_list:
                    instance_machine_map[change[0]] = change[1]
                machine_instances_map[machineId1].append(sortedInstanceList[instance_index2][1])
                machine_instances_map[machineId1].remove(sortedInstanceList[instance_index1][1])
                machine_instances_map[machineId2].append(sortedInstanceList[instance_index1][1])
                machine_instances_map[machineId2].remove(sortedInstanceList[instance_index2][1])
                residual_machine_p[machineId1] -= (app2.p - app1.p)
                residual_machine_p[machineId2] -= (app1.p - app2.p)
                residual_machine_m[machineId1] -= (app2.m - app1.m)
                residual_machine_m[machineId2] -= (app1.m - app2.m)
                residual_machine_pm[machineId1] -= (app2.pm - app1.pm)
                residual_machine_pm[machineId2] -= (app1.pm - app2.pm)
                residual_machine_disk[machineId1] -= (app2.disk - app1.disk)
                residual_machine_disk[machineId2] -= (app1.disk - app2.disk)
                for i in range(T):
                    # print(used_machine_cpu[machineId1][i], used_machine_cpu[machineId2][i])
                    used_machine_cpu[machineId1][i] += (app2.cpus[i] - app1.cpus[i])
                    used_machine_cpu[machineId2][i] += (app1.cpus[i] - app2.cpus[i])
                for i in range(T):
                    residual_machine_mem[machineId1][i] -= (app2.mems[i] - app1.mems[i])
                    residual_machine_mem[machineId2][i] -= (app1.mems[i] - app2.mems[i])
                machine_apps_num_map[machineId1][app1.appId] -= 1
                if machine_apps_num_map.get(machineId1).get(app2.appId) is None:
                    machine_apps_num_map[machineId1][app2.appId] = 1
                else:
                    machine_apps_num_map[machineId1][app2.appId] += 1
                machine_apps_num_map[machineId2][app2.appId] -= 1
                if machine_apps_num_map.get(machineId2).get(app1.appId) is None:
                    machine_apps_num_map[machineId2][app1.appId] = 1
                else:
                    machine_apps_num_map[machineId2][app1.appId] += 1
        else:
            # 变异
            while True:
                instance_index1 = random.randint(0, len(instancesMap) - 1)
                app1 = appsMap.get(sortedInstanceList[instance_index1][1].appId)
                machine_index = random.randint(0, len(machinesMap) - 1)
                machineId = sortedMachineList[machine_index][0]
                if not tell_mut_constraint(machineId, app1):
                    break
            change_list.append([sortedInstanceList[instance_index1][0], machineId])
            machine_val = score_mut_change(machinesMap[machineId], app1)
            origin_val = machine_cpu_score[machineId]
            diff = origin_val - machine_val
            print('mut:', diff)
            if diff >= 0:
                for change in change_list:
                    instance_machine_map[change[0]] = change[1]
                machine_instances_map[machineId].append(sortedInstanceList[instance_index1][1])
                residual_machine_p[machineId] -= app1.p
                residual_machine_m[machineId] -= app1.m
                residual_machine_pm[machineId] -= app1.pm
                residual_machine_disk[machineId] -= app1.disk
                for i in range(T):
                    used_machine_cpu[machineId][i] += app1.cpus[i]
                for i in range(T):
                    residual_machine_mem[machineId][i] -= app1.mems[i]
                if machine_apps_num_map.get(machineId).get(app1.appId) is None:
                    machine_apps_num_map[machineId][app1.appId] = 1
                else:
                    machine_apps_num_map[machineId][app1.appId] += 1
                    # else:
                    #     if exp(df / T) > random.random(0, 1):
                    #         for change in change_list:
                    #             instance_machine_map[change[0]] = change[1]
        T_current = r * T_current

sa()
