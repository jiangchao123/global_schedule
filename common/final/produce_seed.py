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


def randomGreedy(jobs, jobsMap, machine_instances_map, machinesMap, appsMap, machinesList):
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
    job_half_index_map = {}
    job_half_time_index_map = {}
    job_index_map = {}
    job_time_index_map = {}
    assigned_jobs_end_time = {}
    for job in jobs:


        assignSize += 1
    return machine_jobs, assignSize


def assign_job(job, jobsMap, assigned_jobs_end_time, residual_machine_cpu, used_machine_cpu, residual_machine_mem, machinesList):
    assign_jobs = []
    machine_index = 0
    time_index = 0
    pre_jobs = job.pre_jobs
    start_time = 0
    for jobId in pre_jobs:
        if assigned_jobs_end_time.get(jobId) is None:
            assign_job(jobsMap[jobId], jobsMap, assigned_jobs_end_time, residual_machine_cpu, used_machine_cpu, residual_machine_mem, machinesList)
        end_time = assigned_jobs_end_time.get(start_time)
        if start_time < end_time:
            start_time = end_time
    for k in range(job.nums):
        assign = False
        for i in range(machine_index, len(machinesList)):
            for j in range(time_index, 1470 - job.run_time):
                machine = machinesList[i][1]
                if tell_mem_constraint(job, machine, residual_machine_mem, j):
                    continue
                if tell_cpu_constraint(job, machine, residual_machine_cpu, j):
                    continue
                machine_index = i
                time_index = j
                assign_jobs.append((job.jobId, machine.machineId, j))
                assign = True
                break
            if assign:
                break
            time_index = 0
        if not assign:
            print('job:', job.jobId, '未能全部安放')

    for jobId, machineId, start_time in assign_jobs:
        for i in range(start_time, start_time + job.run_time):
            residual_machine_cpu[machineId][i] -= job.cpu
            used_machine_cpu[machineId][i] += job.cpu
        for i in range(start_time, start_time + job.run_time):
            residual_machine_mem[machineId][i] -= job.mem


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
        residual_cpus = [machinesMap[machineId].cpu for i in range(T * 15)]
        used_machine_cpu[machineId] = [0 for i in range(T * 15)]
        residual_mems = [machinesMap[machineId].mem for i in range(T * 15)]
        machine_cpu_score[machineId] = compute_machine_score(instances, machine, appsMap)
        for instance in instances:
            residual_disk -= appsMap[instance.appId].disk
            residual_m -= appsMap[instance.appId].m
            residual_p -= appsMap[instance.appId].p
            residual_pm -= appsMap[instance.appId].pm
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
        residual_machine_disk[machineId] = residual_disk
        residual_machine_m[machineId] = residual_m
        residual_machine_p[machineId] = residual_p
        residual_machine_pm[machineId] = residual_pm
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
