#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/9/1 16:49
Author  : jiangchao08
Site    : 
File    : init_state.py
Software: PyCharm Community Edition

"""
import common.final.fitness as fitness


def read_init_solution(sortedInstanceList, sortedMachineList, machinesMap, appsMap, instancesMap):
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