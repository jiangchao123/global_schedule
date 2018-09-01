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


def tell_cpu_constraint(job, machine, residual_machine_cpu, start_time):
    for i in range(start_time, start_time+job.run_time):
        if job.cpu > residual_machine_cpu[machine.machineId][i]:
            return True
    return False


def tell_mem_constraint(job, machine, residual_machine_mem, start_time):
    for i in range(start_time, start_time + job.run_time):
        if job.mem > round(residual_machine_mem[machine.machineId][i], 12):
            return True
    return False


def compute_cpu_constraint(instance, machine, appsMap, used_machine_cpu, machine_cpu_score):
    time_used = (np.array(used_machine_cpu[machine.machineId]) + np.array(
        appsMap[instance.appId].cpus)) / machine.cpu
    increment_score = 0
    for i in range(T):
        s = alpha * (np.e ** max(0, time_used[i] - beta) - 1)
        increment_score += s
    increment_score -= machine_cpu_score[machine.machineId]
    return increment_score


def randomGreedy(sortedJobList, jobsMap, machine_instances_map, machinesMap, appsMap, machinesList):
    """
    贪心算法，生成不同的种子
    :param flights:
    :return:
    """
    machine_jobs = {}
    residual_machine_p, residual_machine_m, residual_machine_pm, residual_machine_disk, \
    residual_machine_mem, used_machine_cpu, residual_machine_cpu, machine_apps_num_map, machine_cpu_score = compute_residual_info(
        machine_instances_map, machinesList, machinesMap, appsMap, 1.0)
    assignSize = 0
    assigned_jobs_end_time = {}
    for jobId, job in sortedJobList:
        assign_job(job, jobsMap, machine_jobs, assigned_jobs_end_time, residual_machine_cpu,
                   used_machine_cpu, residual_machine_mem, machinesList)
        assignSize += 1
    return machine_jobs, assignSize


def assign_job(job, jobsMap, machine_jobs, assigned_jobs_end_time, residual_machine_cpu, used_machine_cpu, residual_machine_mem, machinesList):
    if assigned_jobs_end_time.get(job.jobId) is not None:
        return
    print('assign job:', job.jobId)
    assign_jobs = []
    machine_index = 0
    time_index = 0
    pre_jobs = job.pre_jobs
    start_time = 0
    max_start_time = 0
    for jobId in pre_jobs:
        if assigned_jobs_end_time.get(jobId) is None:
            assign_job(jobsMap[jobId], jobsMap, machine_jobs, assigned_jobs_end_time, residual_machine_cpu, used_machine_cpu, residual_machine_mem, machinesList)
        end_time = assigned_jobs_end_time.get(jobId)
        # print(job.jobId, jobId, pre_jobs, end_time)
        if start_time < end_time:
            start_time = end_time
    # print('start_time: ', start_time)
    time_index = start_time
    for k in range(job.nums):
        assign = False
        for j in range(time_index, 1470 - job.run_time):
            for i in range(machine_index, len(machinesList)):
                machine = machinesList[i][1]
                if residual_machine_cpu.get(machine.machineId) is None:
                    continue
                if tell_mem_constraint(job, machine, residual_machine_mem, j):
                    # print('cpu不足')
                    continue
                if tell_cpu_constraint(job, machine, residual_machine_cpu, j):
                    # print('mem不足')
                    continue
                machine_index = i
                time_index = j
                if machine_jobs.get((machine.machineId, job.jobId, j)) is None:
                    machine_jobs[(machine.machineId, job.jobId, j)] = 0
                machine_jobs[(machine.machineId, job.jobId, j)] += 1
                assign_jobs.append((job.jobId, machine.machineId, j))
                for i in range(start_time, start_time + job.run_time):
                    residual_machine_cpu[machine.machineId][i] -= job.cpu
                    used_machine_cpu[machine.machineId][i] += job.cpu
                for i in range(start_time, start_time + job.run_time):
                    residual_machine_mem[machine.machineId][i] -= job.mem
                assign = True
                break
            if assign:
                break
            machine_index = 0
        if not assign:
            print('job:', job.jobId, ' 第', k, '个实例未能全部安放')

    for jobId, machineId, start_time in assign_jobs:
        if max_start_time < start_time:
            max_start_time = start_time
    assigned_jobs_end_time[job.jobId] = max_start_time + job.run_time


# # 初始化已经在机器上的实例
# def init_exist_instances(machinesList, cpu_threhold=1):
#     """
#     初始化已经在机器上的实例
#     :return:
#     """
#     machine_instances_map = {}
#     machine_instances_num_map = {}
#     residual_machine_cpu = {}
#     half_residual_machine_cpu = {}
#     used_machine_cpu = {}
#     machine_cpu_score = {}
#     residual_machine_mem = {}
#     residual_machine_disk = {}
#     residual_machine_p = {}
#     residual_machine_m = {}
#     residual_machine_pm = {}
#     for machineId, machine in machinesList:
#         machine_instances_map[machineId] = []
#         residual_machine_p[machineId] = machine.p
#         residual_machine_m[machineId] = machine.m
#         residual_machine_pm[machineId] = machine.pm
#         residual_machine_disk[machineId] = machine.disk
#         residual_machine_cpu[machineId] = [machine.cpu for i in range(T)]
#         used_machine_cpu[machineId] = [0 for i in range(T)]
#         machine_cpu_score[machineId] = 0
#         half_residual_machine_cpu[machineId] = [cpu_threhold * machine.cpu for i in range(T)]
#         residual_machine_mem[machineId] = [machine.mem for i in range(T)]
#         machine_instances_num_map[machineId] = {}
#     return machine_instances_map, residual_machine_p, residual_machine_m, residual_machine_pm, \
#            residual_machine_disk, residual_machine_cpu, half_residual_machine_cpu, used_machine_cpu, \
#            machine_cpu_score, residual_machine_mem, machine_instances_num_map

def compute_residual_info(machine_instances_map, sortedMachineList, machinesMap, appsMap,
                          cpu_thresh=1.0):
    machine_apps_num_map = {}
    residual_machine_cpu = {}
    used_machine_cpu = {}
    machine_cpu_score = {}
    residual_machine_mem = {}
    residual_machine_disk = {}
    residual_machine_p = {}
    residual_machine_m = {}
    residual_machine_pm = {}
    for machineId, instances in machine_instances_map.items():
        machine_apps_num_map[machineId] = {}
        residual_cpus = [machinesMap[machineId].cpu for i in range(T * 15)]
        used_machine_cpu[machineId] = [0 for i in range(T * 15)]
        residual_mems = [machinesMap[machineId].mem for i in range(T * 15)]
        machine_cpu_score[machineId] = compute_machine_score(instances, machinesMap[machineId], appsMap)
        for instance in instances:
            for i in range(T):
                for j in range(15):
                    residual_cpus[i * j + j] -= appsMap[instance.appId].cpus[i]
                    used_machine_cpu[machineId][i * j + j] += appsMap[instance.appId].cpus[i]
            for i in range(T):
                for j in range(15):
                    residual_mems[i * j + j] -= appsMap[instance.appId].mems[i]
            if machine_apps_num_map.get(machineId).get(instance.appId) is None:
                machine_apps_num_map[machineId][instance.appId] = 1
            else:
                machine_apps_num_map[machineId][instance.appId] += 1
        residual_machine_mem[machineId] = residual_mems
        residual_machine_cpu[machineId] = residual_cpus
    return residual_machine_p, residual_machine_m, residual_machine_pm, residual_machine_disk, \
           residual_machine_mem, used_machine_cpu, residual_machine_cpu, machine_apps_num_map, machine_cpu_score


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
        s = 1 + alpha * (np.e ** max(0, cpuUseRate - beta) - 1)
        val += s
    return val
