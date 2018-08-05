#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/7/26 08:13
Author  : jiangchao08
Site    : 
File    : transfer.py
Software: PyCharm Community Edition

"""
import pandas as pd
import data_preprocess.data_process as data_process
import common.produce_seed as produce_seed

T = 98


def transfer_instance():
    machinesMap, sortedMachineList = data_process.handle_machine(
        'data/scheduling_preliminary_machine_resources_20180606.csv')
    appsMap, sortedAppList = data_process.handle_app(
        'data/scheduling_preliminary_app_resources_20180606.csv')
    instancesMap, sortedInstanceList = data_process.handle_instance(
        'data/scheduling_preliminary_instance_deploy_20180606.csv')
    instance_interferences = data_process.handle_app_interference(
        'data/scheduling_preliminary_app_interference_20180606.csv')
    res_file = open('2018-7-23-final.csv', 'w')

    machine_instances_map = {}
    machine_instances_num_map = {}
    residual_machine_cpu = {}
    residual_machine_mem = {}
    residual_machine_disk = {}
    residual_machine_p = {}
    residual_machine_m = {}
    residual_machine_pm = {}
    for machineId, machine in sortedMachineList:
        machine_instances_map[machineId] = []
        residual_machine_p[machineId] = machine.p
        residual_machine_m[machineId] = machine.m
        residual_machine_pm[machineId] = machine.pm
        residual_machine_disk[machineId] = machine.disk
        residual_machine_cpu[machineId] = [machine.cpu for i in range(T)]
        residual_machine_mem[machineId] = [machine.mem for i in range(T)]
        machine_instances_num_map[machineId] = {}
    init_instance_map = {}
    for instance_id, instance in instancesMap.items():
        if instance.machineId is not None and instance.machineId != '':
            init_instance_map[instance_id] = instance
            machine_instances_map[instance.machineId].append(instance)
            if machine_instances_num_map.get(instance.machineId).get(instance.appId) is None:
                machine_instances_num_map[instance.machineId][instance.appId] = 1
            else:
                machine_instances_num_map[instance.machineId][instance.appId] += 1
            residual_machine_p[instance.machineId] -= appsMap[instance.appId].p
            residual_machine_m[instance.machineId] -= appsMap[instance.appId].m
            residual_machine_pm[instance.machineId] -= appsMap[instance.appId].pm
            residual_machine_disk[instance.machineId] -= appsMap[instance.appId].disk
            for i in range(T):
                residual_machine_cpu[instance.machineId][i] -= appsMap[instance.appId].cpus[
                    i]
            for i in range(T):
                residual_machine_mem[instance.machineId][i] -= appsMap[instance.appId].mems[
                    i]

    final_instancesMap, final_sortedInstanceList = data_process.handle_instance(
        '2018-7-23-res.csv')
    print(len(final_instancesMap))
    count = 0
    while count < len(init_instance_map):
        for instance_id, instance in init_instance_map.items():
            final_instance = final_instancesMap.get(instance_id)
            print(instance_id, final_instance)
            machine = machinesMap.get(final_instance.final_machineId)
            if produce_seed.tell_disk_constraint(instance, machine, appsMap, residual_machine_disk):
                continue
            if produce_seed.tell_cpu_constraint(instance, machine, appsMap, residual_machine_cpu):
                continue
            if produce_seed.tell_mem_constraint(instance, machine, appsMap, residual_machine_mem):
                continue
            if produce_seed.tell_app_interference_constraint(instance, machine, appsMap,
                                                             machine_instances_num_map,
                                                             instance_interferences):
                continue
            if produce_seed.tell_m_constraint(instance, machine, appsMap, residual_machine_m):
                continue
            if produce_seed.tell_p_constraint(instance, machine, appsMap, residual_machine_p):
                continue
            if produce_seed.tell_pm_constraint(instance, machine, appsMap, residual_machine_pm):
                continue
            instance.final_machineId = final_instance.final_machineId
            machine_instances_map[instance.final_machineId].append(instance)
            machine_instances_map[instance.machineId].remove(instance)
            if machine_instances_num_map.get(instance.final_machineId).get(instance.appId) is None:
                machine_instances_num_map[instance.final_machineId][instance.appId] = 1
            else:
                machine_instances_num_map[instance.final_machineId][instance.appId] += 1
            machine_instances_num_map[instance.machineId][instance.appId] -= 1
            residual_machine_p[instance.machineId] += appsMap[instance.appId].p
            residual_machine_m[instance.machineId] += appsMap[instance.appId].m
            residual_machine_pm[instance.machineId] += appsMap[instance.appId].pm
            residual_machine_disk[instance.machineId] += appsMap[instance.appId].disk
            residual_machine_p[instance.final_machineId] -= appsMap[instance.appId].p
            residual_machine_m[instance.final_machineId] -= appsMap[instance.appId].m
            residual_machine_pm[instance.final_machineId] -= appsMap[instance.appId].pm
            residual_machine_disk[instance.final_machineId] -= appsMap[instance.appId].disk
            for i in range(T):
                residual_machine_cpu[instance.machineId][i] += appsMap[instance.appId].cpus[
                    i]
                residual_machine_cpu[instance.final_machineId][i] -= appsMap[instance.appId].cpus[
                    i]
            for i in range(T):
                residual_machine_mem[instance.machineId][i] += appsMap[instance.appId].mems[
                    i]
                residual_machine_mem[instance.final_machineId][i] -= appsMap[instance.appId].mems[
                    i]
            count += 1
            res_file.write(instance.instanceId + ',' + instance.machineId + '\n')

    for instance_id, instance in instancesMap.items():
        if instance.final_machineId is None:
            res_file.write(
                instance_id + ',' + final_instancesMap.get(instance_id).final_machineId + '\n')
    res_file.close()

transfer_instance()
