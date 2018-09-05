#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/9/1 11:49
Author  : jiangchao08
Site    : 
File    : constraints_util.py
Software: PyCharm Community Edition

"""
import common.produce_seed as produce_seed

alpha = 10
beta = 0.5
T = 98


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


def tell_cross_constraint(machineId1, machineId2, app1, app2, residual_machine_p,
                          residual_machine_m,
                          residual_machine_pm, residual_machine_disk, residual_machine_mem,
                          machine_apps_num_map, instance_interferences, residual_machine_cpu,
                          tell_cpu=False):
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
    if tell_cpu:
        for i in range(T):
            if residual_machine_cpu[machineId1][i] < app2.cpus[i] - app1.cpus[i] or \
                            residual_machine_cpu[machineId2][i] < app1.cpus[i] - app2.cpus[i]:
                return True
    if machine_apps_num_map[machineId1].get(app1.appId) is not None:
        machine_apps_num_map[machineId1][app1.appId] -= 1
        if tell_app_interference_constraint(app2, machineId1, machine_apps_num_map,
                                            instance_interferences):
            machine_apps_num_map[machineId1][app1.appId] += 1
            return True
        machine_apps_num_map[machineId1][app1.appId] += 1
    if machine_apps_num_map[machineId2].get(app2.appId) is not None:
        machine_apps_num_map[machineId2][app2.appId] -= 1
        if tell_app_interference_constraint(app1, machineId2, machine_apps_num_map,
                                            instance_interferences):
            machine_apps_num_map[machineId2][app2.appId] += 1
            return True
        machine_apps_num_map[machineId2][app2.appId] += 1
    return False


def tell_mut_constraint(machineId, app, residual_machine_p, residual_machine_m, residual_machine_pm,
                        residual_machine_disk, residual_machine_mem, machine_apps_num_map,
                        instance_interferences, residual_machine_cpu, has_cpu=False):
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
        if has_cpu:
            if residual_machine_cpu[machineId][i] < app.cpus[i]:
                return True
    if tell_app_interference_constraint(app, machineId, machine_apps_num_map,
                                        instance_interferences):
        return True
    return False


def post_check(machinesMap, sortedMachineList, machine_instances_map, appsMap,
               instance_interferences):
    new_machine_instances_map, residual_machine_p, residual_machine_m, residual_machine_pm, \
    residual_machine_disk, residual_machine_cpu, half_residual_machine_cpu, used_machine_cpu, \
    machine_cpu_score, residual_machine_mem, machine_instances_num_map = produce_seed.init_exist_instances(
        sortedMachineList, appsMap, cpu_threhold=1)
    for machineId, instances in machine_instances_map.items():
        if machinesMap.get(machineId) is None:
            # print('instances 数量', len(instances))
            continue
        machine = machinesMap[machineId]
        for instance in instances:
            # print('instance:', instance.instanceId)
            if produce_seed.tell_disk_constraint(instance, machine, appsMap, residual_machine_disk):
                print('不满足disk约束')
                continue
            if produce_seed.tell_mem_constraint(instance, machine, appsMap, residual_machine_mem):
                print('不满足mem约束')
                continue
            if produce_seed.tell_app_interference_constraint(instance, machine, appsMap,
                                                             machine_instances_num_map,
                                                             instance_interferences):
                print('不满足app interfer约束')
                continue
            if produce_seed.tell_m_constraint(instance, machine, appsMap, residual_machine_m):
                print('不满足m约束')
                continue
            if produce_seed.tell_p_constraint(instance, machine, appsMap, residual_machine_p):
                print('不满足p约束')
                continue
            if produce_seed.tell_pm_constraint(instance, machine, appsMap, residual_machine_pm):
                continue
            if produce_seed.tell_cpu_constraint(instance, machine, appsMap,
                                                half_residual_machine_cpu):
                print('不满足cpu约束')
                continue
            new_machine_instances_map[machineId].append(instance)
            if machine_instances_num_map.get(machineId).get(instance.appId) is None:
                machine_instances_num_map[machineId][instance.appId] = 1
            else:
                machine_instances_num_map[machineId][instance.appId] += 1
            residual_machine_p[machineId] -= appsMap[instance.appId].p
            residual_machine_m[machineId] -= appsMap[instance.appId].m
            residual_machine_pm[machineId] -= appsMap[instance.appId].pm
            residual_machine_disk[machineId] -= appsMap[instance.appId].disk
            for i in range(T):
                residual_machine_cpu[machineId][i] -= appsMap[instance.appId].cpus[i]
                half_residual_machine_cpu[machineId][i] -= appsMap[instance.appId].cpus[
                    i]
                used_machine_cpu[machineId][i] += appsMap[instance.appId].cpus[i]
            for i in range(T):
                residual_machine_mem[machineId][i] -= appsMap[instance.appId].mems[i]
