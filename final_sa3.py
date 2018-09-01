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
import common.final.fitness as fitness
import common.final.produce_seed as produce_seed

from common.exe_time import exeTime
import array
import random
import numpy as np
import pandas as pd
import data_preprocess.data_process as data_process
import static.static_info as static_tool
import math
import final_solver as final_solver
import common.final.sa_util as sa_util

alpha = 10
beta = 0.5
T = 98

data_name = 'a'

machinesMap, sortedMachineList = data_process.handle_machine(
    'data/final/machine_resources.' + data_name + '.csv')
for machineId, machine in sortedMachineList:
    print(machineId)
appsMap, sortedAppList = data_process.handle_app(
    'data/final/app_resources.csv')
instancesMap, sortedInstanceList = data_process.handle_instance(
    'data/final/instance_deploy.' + data_name + '.csv')
instance_interferences = data_process.handle_app_interference(
    'data/final/app_interference.csv')

jobsMap, sortedJobList = data_process.handle_job('data/final/job_info.' + data_name + '.csv')


def read_init_solution(sortedInstanceList):
    machine_instances_map = {}
    unassigned_machines = {}
    assigned_machines_instances_map = {}
    unassigned_machineIds = []
    instance_machine_map = {}
    for machineId, machine in sortedMachineList:
        machine_instances_map[machineId] = []
    unassigned_instances = []
    assign_count = 0
    for instanceId, instance in sortedInstanceList:
        if instance.machineId is None:
            unassigned_instances.append(instanceId)
        else:
            assign_count += 1
            instance.final_machineId = instance.machineId
            instance_machine_map[instanceId] = instance.machineId
            machine_instances_map[instance.machineId].append(instance)

    fit = fitness.fitnessfun(machine_instances_map, machinesMap, appsMap, assign_count,
                             len(instancesMap))
    for machineId, instances in machine_instances_map.items():
        if len(instances) == 0:
            unassigned_machines[machineId] = []
            unassigned_machineIds.append(machineId)
        else:
            assigned_machines_instances_map[machineId] = instances
    print('已使用机器数量:', len(assigned_machines_instances_map))
    return machine_instances_map, instance_machine_map, fit, unassigned_machines, unassigned_machineIds, assigned_machines_instances_map


machine_instances_map, instance_machine_map, fit, unassigned_machines, unassigned_machineIds, assigned_machines_instances_map = read_init_solution(
    sortedInstanceList)
print(fit)
origin_fit = fit

####### first version ##########
# machine_jobs, _ = produce_seed.randomGreedy(sortedJobList, jobsMap, unassigned_machines,
#                                             machinesMap, appsMap, sortedMachineList)
# res_file = open('2018-8-31-final-' + data_name + '-1.0-res.csv', 'w')
# cpu = 0
# mem = 0
# for (machineId, jobId, start_timme), nums in machine_jobs.items():
#     res_file.write(
#         str(jobId) + ',' + str(machineId) + ',' + str(start_timme) + ',' + str(nums) + '\n')
# res_file.close()

####### second version ##########
assigned_machines_instances_map, machinesMap, sortedMachineList = sa_util.select_sa_machines(
    assigned_machines_instances_map,
    unassigned_machineIds, 5000, machinesMap)
residual_machine_p, residual_machine_m, residual_machine_pm, residual_machine_disk, \
residual_machine_mem, used_machine_cpu, residual_machine_cpu, machine_apps_num_map, machine_cpu_score = sa_util.compute_residual_info(
    assigned_machines_instances_map, sortedMachineList, machinesMap, appsMap)

val, best_score = final_solver.sa(instancesMap, appsMap, sortedInstanceList, sortedMachineList,
                                  instance_machine_map,
                                  machinesMap, machine_cpu_score, residual_machine_p,
                                  residual_machine_m,
                                  residual_machine_pm, residual_machine_disk, residual_machine_mem,
                                  machine_apps_num_map, instance_interferences,
                                  machine_instances_map, used_machine_cpu)
print(val, best_score)

# static_tool.static_machine(machine_instances_map, machinesMap, appsMap)
fit = fitness.fitnessfun(machine_instances_map, machinesMap, appsMap, len(instancesMap),
                         len(instancesMap))
print(fit)

sa_util.post_check(machinesMap, sortedMachineList, machine_instances_map, appsMap,
                   instance_interferences)
sa_util.generate_origin_result(machine_instances_map, '8-31', data_name)
