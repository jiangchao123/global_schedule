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
import data_preprocess.data_process as data_process
import final_solver as final_solver
import common.final.sa_util as sa_util
import common.final.init_state as init_state_util
import common.final.constraints_util as constraints_util
import common.final.produce_seed as produce_seed
import copy
import common.final.transfer_util as transfer_util

alpha = 10
beta = 0.5
T = 98

data_name = 'a'
time = '9-1'

origin_machinesMap, origin_sortedMachineList = data_process.handle_machine(
    'data/final/machine_resources.' + data_name + '.csv')
for machineId, machine in origin_sortedMachineList:
    print(machineId)
appsMap, sortedAppList = data_process.handle_app(
    'data/final/app_resources.csv')
instancesMap, sortedInstanceList = data_process.handle_instance(
    'data/final/instance_deploy.' + data_name + '.csv')
instance_interferences = data_process.handle_app_interference(
    'data/final/app_interference.csv')

jobsMap, sortedJobList = data_process.handle_job('data/final/job_info.' + data_name + '.csv')

machine_instances_map, instance_machine_map, fit, unassigned_machines, unassigned_machineIds, \
assigned_machines_instances_map = init_state_util.read_init_solution(
    sortedInstanceList, origin_sortedMachineList, origin_machinesMap, appsMap, instancesMap)
print(fit)
origin_fit = fit

origin_assigned_machines_instances_map = copy.deepcopy(assigned_machines_instances_map)

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
# assigned_machines_instances_map, instance_machine_map, machinesMap, sortedMachineList = sa_util.select_sa_machines(
#     assigned_machines_instances_map,
#     unassigned_machineIds, 5000, machinesMap, sortedMachineList, appsMap, instance_interferences, instance_machine_map)
#
# fit = fitness.fitnessfun(assigned_machines_instances_map, machinesMap, appsMap, len(instancesMap),
#                          len(instancesMap))
# print('扩展机器后得分：', fit)
#
# residual_machine_p, residual_machine_m, residual_machine_pm, residual_machine_disk, \
# residual_machine_mem, used_machine_cpu, residual_machine_cpu, machine_apps_num_map, machine_cpu_score = sa_util.compute_residual_info(
#     assigned_machines_instances_map, sortedMachineList, machinesMap, appsMap)
#
# val, best_score = final_solver.sa(instancesMap, appsMap, sortedInstanceList, sortedMachineList,
#                                   instance_machine_map,
#                                   machinesMap, machine_cpu_score, residual_machine_p,
#                                   residual_machine_m,
#                                   residual_machine_pm, residual_machine_disk, residual_machine_mem,
#                                   machine_apps_num_map, instance_interferences,
#                                   assigned_machines_instances_map, used_machine_cpu,
#                                   residual_machine_cpu)
# print(val, best_score)
#
# # static_tool.static_machine(machine_instances_map, machinesMap, appsMap)
# fit = fitness.fitnessfun(assigned_machines_instances_map, machinesMap, appsMap, len(instancesMap),
#                          len(instancesMap))
# print(fit)
# constraints_util.post_check(machinesMap, sortedMachineList, assigned_machines_instances_map,
#                             appsMap,
#                             instance_interferences)
# sa_util.generate_origin_result(assigned_machines_instances_map, '8-31', data_name)


#####third version###########
assigned_machines_instances_map, instance_machine_map, machinesMap, sortedMachineList, unused_machine_instances = sa_util.select_sa_machines(
    assigned_machines_instances_map,
    unassigned_machineIds, 5000, origin_machinesMap, origin_sortedMachineList, appsMap,
    instance_interferences, instance_machine_map)

fit = fitness.fitnessfun(assigned_machines_instances_map, machinesMap, appsMap, len(instancesMap),
                         len(instancesMap))
print('扩展机器后得分：', fit)
residual_machine_p, residual_machine_m, residual_machine_pm, residual_machine_disk, \
residual_machine_mem, used_machine_cpu, residual_machine_cpu, machine_apps_num_map, machine_cpu_score = sa_util.compute_residual_info(
    assigned_machines_instances_map, sortedMachineList, machinesMap, appsMap)

val, best_score = final_solver.sa(instancesMap, appsMap, sortedInstanceList, sortedMachineList,
                                  instance_machine_map,
                                  machinesMap, machine_cpu_score, residual_machine_p,
                                  residual_machine_m,
                                  residual_machine_pm, residual_machine_disk, residual_machine_mem,
                                  machine_apps_num_map, instance_interferences,
                                  assigned_machines_instances_map, used_machine_cpu,
                                  residual_machine_cpu)
print(val, best_score)

# static_tool.static_machine(machine_instances_map, machinesMap, appsMap)
fit = fitness.fitnessfun(assigned_machines_instances_map, machinesMap, appsMap, len(instancesMap),
                         len(instancesMap))
print(fit)
constraints_util.post_check(machinesMap, sortedMachineList, assigned_machines_instances_map,
                            appsMap,
                            instance_interferences)
sa_util.generate_origin_result(assigned_machines_instances_map, time, data_name)

# 放置离线job
# machine_jobs, _ = produce_seed.randomGreedy(sortedJobList, jobsMap, assigned_machines_instances_map,
#                                             machinesMap, appsMap, sortedMachineList)
machine_jobs, _ = produce_seed.randomGreedy(sortedJobList, jobsMap, unused_machine_instances,
                                            origin_machinesMap, appsMap, origin_sortedMachineList,
                                            cpu_thresh=1.0)

sa_util.generate_job_result(machine_jobs, time, data_name)

# 对实例进行迁移
first_rounds, second_rounds, third_rounds = transfer_util.transfer(
    origin_assigned_machines_instances_map, assigned_machines_instances_map,
    origin_machinesMap, origin_sortedMachineList, appsMap,
    instance_interferences)
