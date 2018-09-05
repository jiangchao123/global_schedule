#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/9/1 11:47
Author  : jiangchao08
Site    : 
File    : sa_util.py
Software: PyCharm Community Edition

"""
import numpy as np
import common.final.constraints_util as constraints_util

beta = 0.5
T = 98


def select_sa_machines(assigned_machines_instances_map, unassigned_machineIds, nums, machinesMap,
                       sortedMachineList, appsMap, instance_interferences, instance_machine_map):
    new_machinesMap = {}
    total_instances_count = 0
    # 要补充的机器数量
    need_add_machines_nums = nums - len(assigned_machines_instances_map)
    if need_add_machines_nums < 0:
        need_add_machines_nums = 0
    unused_machine_instances = {}
    # 补充的空机器
    add_machines = []
    for i in range(0, need_add_machines_nums):
        assigned_machines_instances_map[unassigned_machineIds[i]] = []
        add_machines.append(unassigned_machineIds[i])
    for i in range(need_add_machines_nums, len(unassigned_machineIds)):
        unused_machine_instances[unassigned_machineIds[i]] = []
    for machineId, instances in assigned_machines_instances_map.items():
        total_instances_count += len(instances)
        new_machinesMap[machineId] = machinesMap[machineId]
    print('扩展前实例数量:', total_instances_count, ' 预计使用机器数量：', len(assigned_machines_instances_map))
    mean_instances_count = int(total_instances_count / nums)
    # 均匀扩展实例unused_machine_instances
    # new_machine_index = 0
    residual_machine_p, residual_machine_m, residual_machine_pm, residual_machine_disk, \
    residual_machine_mem, used_machine_cpu, residual_machine_cpu, machine_apps_num_map, machine_cpu_score = compute_residual_info(
        assigned_machines_instances_map, sortedMachineList, machinesMap, appsMap)
    # app可存放的最早机器下标
    app_machine_index = {}
    for machineId, instances in assigned_machines_instances_map.items():
        if len(instances) <= mean_instances_count:
            continue
        if machineId in add_machines:
            continue
        # print('扩展机器:', machineId)
        be_deleted_instances = []
        for i in range(mean_instances_count, len(instances)):
            be_deleted_instances.append(instances[i])
        for instance in be_deleted_instances:
            app = appsMap[instance.appId]
            index = 0
            if app_machine_index.get(app.appId) is not None:
                index = app_machine_index[app.appId]
            for j in range(index, len(add_machines)):
                machineId2 = add_machines[j]
                if len(assigned_machines_instances_map[machineId2]) >= mean_instances_count:
                    continue
                if not constraints_util.tell_mut_constraint(machineId2, app,
                                                            residual_machine_p, residual_machine_m,
                                                            residual_machine_pm,
                                                            residual_machine_disk,
                                                            residual_machine_mem,
                                                            machine_apps_num_map,
                                                            instance_interferences,
                                                            residual_machine_cpu, has_cpu=True):
                    mut_update_info(machineId2, instance, app,
                                    machineId,
                                    assigned_machines_instances_map,
                                    residual_machine_p, residual_machine_m, residual_machine_pm,
                                    residual_machine_disk, used_machine_cpu, residual_machine_mem,
                                    machine_apps_num_map, residual_machine_cpu)
                    app_machine_index[app.appId] = j
                    instance_machine_map[instance.instanceId] = machineId2
                    break

    total_instances_count = 0
    for machineId, instances in assigned_machines_instances_map.items():
        total_instances_count += len(instances)
    print('扩展后实例数量:', total_instances_count, ' 使用机器数量：', len(assigned_machines_instances_map))
    return assigned_machines_instances_map, instance_machine_map, new_machinesMap, sorted(
        new_machinesMap.items(),
        key=lambda d: d[1].cpu,
        reverse=True), unused_machine_instances


def compute_machine_score(instances, machine, appsMap):
    if instances is None or len(instances) == 0:
        return 0
    val = 0
    for i in range(T):
        cpu = 0
        for instance in instances:
            app = appsMap[instance.appId]
            cpu += app.cpus[i]
        cpuUseRate = cpu / machine.cpu
        s = 1 + len(instances) * (np.e ** max(0, cpuUseRate - beta) - 1)
        val += s
    return val


def compute_residual_info(machine_instances_map, sortedMachineList, machinesMap, appsMap):
    machine_apps_num_map = {}
    residual_machine_cpu = {}
    used_machine_cpu = {}
    machine_cpu_score = {}
    residual_machine_mem = {}
    residual_machine_disk = {}
    residual_machine_p = {}
    residual_machine_m = {}
    residual_machine_pm = {}
    for machineId, machine in sortedMachineList:
        if machine_instances_map.get(machineId) is None:
            continue
        machine_apps_num_map[machineId] = {}
        instances = machine_instances_map.get(machineId)
        residual_disk = machinesMap[machineId].disk
        residual_m = machinesMap[machineId].m
        residual_p = machinesMap[machineId].p
        residual_pm = machinesMap[machineId].pm
        residual_cpus = [machinesMap[machineId].cpu for i in range(T)]
        used_machine_cpu[machineId] = [0 for i in range(T)]
        residual_mems = [machinesMap[machineId].mem for i in range(T)]
        machine_cpu_score[machineId] = compute_machine_score(instances, machine, appsMap)
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


def compute_residual_info2(machine_instances_map, machine_jobs, sortedMachineList, machinesMap,
                           appsMap):
    machine_apps_num_map = {}
    residual_machine_cpu = {}
    used_machine_cpu = {}
    machine_cpu_score = {}
    residual_machine_mem = {}
    residual_machine_disk = {}
    residual_machine_p = {}
    residual_machine_m = {}
    residual_machine_pm = {}
    for machineId, machine in sortedMachineList:
        if machine_instances_map.get(machineId) is None:
            continue
        machine_apps_num_map[machineId] = {}
        instances = machine_instances_map.get(machineId)
        residual_disk = machinesMap[machineId].disk
        residual_m = machinesMap[machineId].m
        residual_p = machinesMap[machineId].p
        residual_pm = machinesMap[machineId].pm
        residual_cpus = [machinesMap[machineId].cpu for i in range(T)]
        used_machine_cpu[machineId] = [0 for i in range(T)]
        residual_mems = [machinesMap[machineId].mem for i in range(T)]
        machine_cpu_score[machineId] = compute_machine_score(instances, machine, appsMap)
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


def score_cross_change(app1, machine1, app2, machine2, used_machine_cpu, machine_instances_map):
    machine_val1 = 0
    machine_val2 = 0
    for i in range(T):
        cpus = used_machine_cpu[machine1.machineId]
        cpus[i] += (app2.cpus[i] - app1.cpus[i])
        cpuUseRate = cpus[i] / machine1.cpu
        s = 1 + len(machine_instances_map[machine1.machineId]) * (
        np.e ** max(0, cpuUseRate - beta) - 1)
        machine_val1 += s
        cpus[i] -= (app2.cpus[i] - app1.cpus[i])
    for i in range(T):
        cpus = used_machine_cpu[machine2.machineId]
        cpus[i] += (app1.cpus[i] - app2.cpus[i])
        cpuUseRate = cpus[i] / machine2.cpu
        s = 1 + len(machine_instances_map[machine2.machineId]) * (
        np.e ** max(0, cpuUseRate - beta) - 1)
        machine_val2 += s
        cpus[i] -= (app1.cpus[i] - app2.cpus[i])
    return machine_val1, machine_val2


def score_mut_change(machine, app, origin_machine, machine_instances_map, used_machine_cpu):
    origin_val = 0
    target_val = 0
    if len(machine_instances_map[origin_machine.machineId]) == 1:
        origin_val = 0
    else:
        for i in range(T):
            cpus = used_machine_cpu[origin_machine.machineId]
            cpus[i] -= app.cpus[i]
            cpuUseRate = cpus[i] / machine.cpu
            s = 1 + (len(machine_instances_map[origin_machine.machineId]) - 1) * (
            np.e ** max(0, cpuUseRate - beta) - 1)
            origin_val += s
            cpus[i] += app.cpus[i]
    for i in range(T):
        cpus = used_machine_cpu[machine.machineId]
        cpus[i] += app.cpus[i]
        cpuUseRate = cpus[i] / machine.cpu
        s = 1 + (len(machine_instances_map[machine.machineId]) + 1) * (
        np.e ** max(0, cpuUseRate - beta) - 1)
        target_val += s
        cpus[i] -= app.cpus[i]
    return origin_val, target_val


def cross_update_info(machineId1, machineId2, instance_index1, instance_index2, app1, app2,
                      machine_val1, machine_val2, machine_instances_map, sortedInstanceList,
                      residual_machine_p, residual_machine_m, residual_machine_pm,
                      residual_machine_disk, used_machine_cpu, residual_machine_mem,
                      machine_apps_num_map, machine_cpu_score):
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
    machine_cpu_score[machineId1] = machine_val1
    machine_cpu_score[machineId2] = machine_val2


def mut_update_info(machineId, instance, app1, origin_machineId, machine_instances_map,
                    residual_machine_p, residual_machine_m, residual_machine_pm,
                    residual_machine_disk, used_machine_cpu, residual_machine_mem,
                    machine_apps_num_map, residual_machine_cpu):
    machine_instances_map[machineId].append(instance)
    machine_instances_map[origin_machineId].remove(instance)
    residual_machine_p[machineId] -= app1.p
    residual_machine_m[machineId] -= app1.m
    residual_machine_pm[machineId] -= app1.pm
    residual_machine_disk[machineId] -= app1.disk

    residual_machine_p[origin_machineId] += app1.p
    residual_machine_m[origin_machineId] += app1.m
    residual_machine_pm[origin_machineId] += app1.pm
    residual_machine_disk[origin_machineId] += app1.disk
    for i in range(T):
        used_machine_cpu[machineId][i] += app1.cpus[i]
        residual_machine_cpu[machineId][i] -= app1.cpus[i]
        used_machine_cpu[origin_machineId][i] -= app1.cpus[i]
        residual_machine_cpu[origin_machineId][i] += app1.cpus[i]
    for i in range(T):
        residual_machine_mem[machineId][i] -= app1.mems[i]
        residual_machine_mem[origin_machineId][i] += app1.mems[i]
    if machine_apps_num_map.get(machineId).get(app1.appId) is None:
        machine_apps_num_map[machineId][app1.appId] = 1
    else:
        machine_apps_num_map[machineId][app1.appId] += 1
    machine_apps_num_map[origin_machineId][app1.appId] -= 1


def generate_origin_result(machine_instances_map, time, data_name):
    res_file = open('2018-' + time + '-origin-' + data_name + '-1.0-res.csv', 'w')
    for machineId, instances in machine_instances_map.items():
        for instance in instances:
            res_file.write(instance.instanceId + ',' + machineId + '\n')
    res_file.close()


def generate_job_result(machine_jobs, time, data_name):
    res_file = open('2018-' + time + '-origin-job-' + data_name + '-1.0-res.csv', 'w')
    for (machineId, jobId, start_timme), nums in machine_jobs.items():
        res_file.write(
            str(jobId) + ',' + str(machineId) + ',' + str(start_timme) + ',' + str(nums) + '\n')
    res_file.close()


def generate_instance_transfer_result(first_rounds, second_rounds, third_rounds, time, data_name):
    res_file = open('2018-' + time + '-transfer-instance-' + data_name + '-1.0-res.csv', 'w')
    for instanceId, machineId in first_rounds:
        res_file.write('1' + ',' + instanceId + ',' + machineId + '\n')
    for instanceId, machineId in second_rounds:
        res_file.write('2' + ',' + instanceId + ',' + machineId + '\n')
    for instanceId, machineId in third_rounds:
        res_file.write('3' + ',' + instanceId + ',' + machineId + '\n')
    res_file.close()
