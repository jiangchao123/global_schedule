#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/9/2 09:35
Author  : jiangchao08
Site    : 
File    : transfer_util.py
Software: PyCharm Community Edition

"""
import common.produce_seed as produce_seed


def transfer(origin_assigned_machines_instances_map, assigned_machines_instances_map,
             origin_machinesMap, origin_sortedMachineList, appsMap, instance_interferences):
    # 初始化使用的机器
    origin_used_machines = []
    # 最终未使用机器
    last_unused_machines = []
    # 最终使用的全部机器
    last_used_machines = []
    # 新使用的机器
    new_used_machines = []

    # first_round
    first_rounds = []
    # second_round
    second_rounds = []
    # third_round
    third_rounds = []
    # 设计实例的目标机器
    for machineId, instances in assigned_machines_instances_map.items():
        for instance in instances:
            instance.final_machineId = machineId

    for machineId, instances in origin_assigned_machines_instances_map.items():
        origin_used_machines.append(machineId)
    for machineId, machine in origin_machinesMap.items():
        if assigned_machines_instances_map.get(machineId) is None or len(
                assigned_machines_instances_map.get(machineId)) == 0:
            last_unused_machines.append(machineId)
        else:
            last_used_machines.append(machineId)
    for machineId in last_used_machines:
        if machineId not in origin_used_machines:
            new_used_machines.append(machineId)

    # 开始迁移第一.1步：实例迁移至新增机器；
    new_used_machine_instances = []
    for machineId, instances in assigned_machines_instances_map.items():
        if machineId in new_used_machines:
            for instance in instances:
                first_rounds.append([instance.instanceId, machineId])
                new_used_machine_instances.append(instance)

    # 开始迁移第一.2步：将实例先放置于未使用机器；
    transfer_instances = []
    for machineId, instances in origin_assigned_machines_instances_map.items():
        for instance in instances:
            if instance.machineId != instance.final_machineId:
                transfer_instances.append(instance)
    transfer_machineList = []
    for machineId, machine in origin_sortedMachineList:
        if machineId in last_unused_machines:
            transfer_machineList.append((machineId, machine))

    transfer_machine_instances_map, assignSize = produce_seed.randomGreedy(transfer_instances,
                                                                           appsMap,
                                                                           transfer_machineList,
                                                                           instance_interferences)
    print('transfer size:', len(transfer_instances), ' final transfer size:', assignSize)
    for machineId, instances in transfer_machine_instances_map.items():
        for instance in instances:
            first_rounds.append([instance.instanceId, machineId])
    # 第二步：从未使用机器进行最终安放
    for instance in transfer_instances:
        second_rounds.append([instance, instance.final_machineId])

    return first_rounds, second_rounds, third_rounds
