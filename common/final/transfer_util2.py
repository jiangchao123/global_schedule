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
    # 最终实例对应的机器
    instance_machine_map = {}

    # first_round
    first_rounds = []
    # second_round
    second_rounds = []
    # third_round
    third_rounds = []

    # 原始机器和目标机器相同的数量
    same_machine_count = 0

    # 设计实例的目标机器
    for machineId, instances in assigned_machines_instances_map.items():
        for instance in instances:
            instance_machine_map[instance.instanceId] = machineId
            if instance.machineId == machineId:
                same_machine_count += 1
    print('原始机器和目标机器相同的数量: ', same_machine_count)

    count = 0
    for machineId, instances in origin_assigned_machines_instances_map.items():
        origin_used_machines.append(machineId)
        count += len(instances)
    # print('原始实例数量:', count)
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
    # new_used_machine_instances_map = {}
    for machineId, instances in assigned_machines_instances_map.items():
        if machineId in new_used_machines:
            for instance in instances:
                first_rounds.append([instance.instanceId, machineId])
                new_used_machine_instances.append(instance.instanceId)
    print('first 1 rounds:', len(first_rounds), print(len(new_used_machine_instances)))

    # 开始迁移第一.2步：将实例先放置于未使用机器；
    transfer_machineList = []
    for machineId, machine in origin_sortedMachineList:
        if machineId in last_unused_machines:
            transfer_machineList.append((machineId, machine))
            # print('transfer_machineList:', machineId)

    print('transfer machines size:', len(transfer_machineList))

    sorted_origin_assigned_machines_instances_map = sorted(
        origin_assigned_machines_instances_map.items(), key=lambda d: origin_machinesMap[d[0]].cpu,
        reverse=True)
    transfer_instances = []
    # 先进行等价机器映射
    transfer_machine_instances_map = {}
    index = 0
    for machineId, instances in sorted_origin_assigned_machines_instances_map:
        tmp_instances = []
        for instance in instances:
            if machineId != instance_machine_map[instance.instanceId]:
                # print(machineId, instance_machine_map[instance.instanceId])
                if instance.instanceId not in new_used_machine_instances:
                    # print('----------------------------')
                    tmp_instances.append(instance)
        if index < len(transfer_machineList) and origin_machinesMap[machineId].cpu <= transfer_machineList[index][1].cpu and \
                        origin_machinesMap[machineId].mem <= transfer_machineList[index][1].mem:
            # print('=======================', len(tmp_instances))
            transfer_machine_instances_map[transfer_machineList[index][0]] = tmp_instances
            index += 1
            continue
        for instance in instances:
            if machineId != instance_machine_map[
                instance.instanceId] and instance.instanceId not in new_used_machine_instances:
                transfer_instances.append(instance)

    # 加入新增使用机器
    for machineId, instances in assigned_machines_instances_map.items():
        if machineId in new_used_machines:
            transfer_machine_instances_map[machineId] = instances
            transfer_machineList.append((machineId, origin_machinesMap[machineId]))
    print('transfer instances size:', len(transfer_instances))
    if len(transfer_instances) != 0:
        transfer_machine_instances_map, assignSize = produce_seed.randomGreedy(transfer_instances,
                                                                               appsMap,
                                                                               transfer_machineList,
                                                                               instance_interferences,
                                                                               transfer_machine_instances_map)
        print('transfer size:', len(transfer_instances), ' final transfer size:', assignSize)
    for machineId, instances in transfer_machine_instances_map.items():
        for instance in instances:
            first_rounds.append([instance.instanceId, machineId])
    print('first 2 rounds:', len(first_rounds))
    # 第二步：从未使用机器进行最终安放
    for machineId, instances in transfer_machine_instances_map.items():
        for instance in instances:
            second_rounds.append([instance.instanceId, instance_machine_map[instance.instanceId]])
    print('second ronuds:', len(second_rounds))
    return first_rounds, second_rounds, third_rounds
