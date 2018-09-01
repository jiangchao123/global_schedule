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
import common.final.produce_seed as produce_seed

from common.exe_time import exeTime
import array
import random
import numpy as np
import pandas as pd
import data_preprocess.data_process as data_process
import static.static_info as static_tool
import math

alpha = 10
beta = 0.5
T = 98

data_name = 'd'

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
    return machine_instances_map, instance_machine_map, fit, unassigned_machines


machine_instances_map, instance_machine_map, fit, unassigned_machines = read_init_solution(
    sortedInstanceList)
print(fit)
origin_fit = fit

machine_jobs, _ = produce_seed.randomGreedy(sortedJobList, jobsMap, unassigned_machines,
                                            machinesMap, appsMap, sortedMachineList)

res_file = open('2018-8-29-final-' + data_name + '-1.0-res.csv', 'w')
cpu = 0
mem = 0
for (machineId, jobId, start_timme), nums in machine_jobs.items():
    res_file.write(
        str(jobId) + ',' + str(machineId) + ',' + str(start_timme) + ',' + str(nums) + '\n')
res_file.close()
