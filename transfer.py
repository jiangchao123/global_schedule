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


def tell_constrains(instance, machine, appsMap, residual_machine_disk, residual_machine_cpu,
                    residual_machine_mem, machine_instances_num_map, residual_machine_m,
                    residual_machine_p, residual_machine_pm, instance_interferences,
                    print_info=False):
    if produce_seed.tell_disk_constraint(instance, machine, appsMap, residual_machine_disk):
        if print_info:
            print('检测disk不合')
        return False
    if produce_seed.tell_cpu_constraint(instance, machine, appsMap, residual_machine_cpu):
        if print_info:
            print('检测cpu不合')
        return False
    if produce_seed.tell_mem_constraint(instance, machine, appsMap, residual_machine_mem):
        if print_info:
            print('检测mem不合')
        return False
    if produce_seed.tell_app_interference_constraint(instance, machine, appsMap,
                                                     machine_instances_num_map,
                                                     instance_interferences, print_info):
        if print_info:
            print('检测app interfere不合')
            print(machine_instances_num_map[machine.machineId])
        return False
    if produce_seed.tell_m_constraint(instance, machine, appsMap, residual_machine_m):
        if print_info:
            print('检测m不合')
        return False
    if produce_seed.tell_p_constraint(instance, machine, appsMap, residual_machine_p):
        if print_info:
            print('检测p不合')
        return False
    if produce_seed.tell_pm_constraint(instance, machine, appsMap, residual_machine_pm):
        if print_info:
            print('检测pm不合')
        return False
    return True


def update_state(instance, original_machineId, target_machineId, machine_instances_map,
                 machine_instances_num_map, appsMap,
                 residual_machine_p, residual_machine_m, residual_machine_pm, residual_machine_disk,
                 residual_machine_cpu, residual_machine_mem):
    machine_instances_map[target_machineId].append(instance)
    machine_instances_map[original_machineId].remove(instance)
    # init_instance_map.pop(instance_id)
    if machine_instances_num_map.get(target_machineId).get(instance.appId) is None:
        machine_instances_num_map[target_machineId][instance.appId] = 1
    else:
        machine_instances_num_map[target_machineId][instance.appId] += 1
    machine_instances_num_map[original_machineId][instance.appId] -= 1
    residual_machine_p[original_machineId] += appsMap[instance.appId].p
    residual_machine_m[original_machineId] += appsMap[instance.appId].m
    residual_machine_pm[original_machineId] += appsMap[instance.appId].pm
    residual_machine_disk[original_machineId] += appsMap[instance.appId].disk
    residual_machine_p[target_machineId] -= appsMap[instance.appId].p
    residual_machine_m[target_machineId] -= appsMap[instance.appId].m
    residual_machine_pm[target_machineId] -= appsMap[instance.appId].pm
    residual_machine_disk[target_machineId] -= appsMap[instance.appId].disk
    for i in range(T):
        residual_machine_cpu[original_machineId][i] += appsMap[instance.appId].cpus[
            i]
        residual_machine_cpu[target_machineId][i] -= appsMap[instance.appId].cpus[
            i]
    for i in range(T):
        residual_machine_mem[original_machineId][i] += appsMap[instance.appId].mems[
            i]
        residual_machine_mem[target_machineId][i] -= appsMap[instance.appId].mems[
            i]


def transfer_instance():
    # machinesMap, sortedMachineList = data_process.handle_machine(
    #     'data/scheduling_preliminary_machine_resources_20180606.csv')
    # appsMap, sortedAppList = data_process.handle_app(
    #     'data/scheduling_preliminary_app_resources_20180606.csv')
    # instancesMap, sortedInstanceList = data_process.handle_instance(
    #     'data/scheduling_preliminary_instance_deploy_20180606.csv')
    # instance_interferences = data_process.handle_app_interference(
    #     'data/scheduling_preliminary_app_interference_20180606.csv')
    # res_file = open('2018-8-7-a-final.csv', 'w')
    # final_instancesMap, final_sortedInstanceList = data_process.handle_instance(
    #     '2018-8-7-a-res.csv')
    # print(len(final_instancesMap))

    # def transfer_instance():
    machinesMap, sortedMachineList = data_process.handle_machine(
        'data/b/scheduling_preliminary_b_machine_resources_20180726.csv')
    appsMap, sortedAppList = data_process.handle_app(
        'data/b/scheduling_preliminary_b_app_resources_20180726.csv')
    instancesMap, sortedInstanceList = data_process.handle_instance(
        'data/b/scheduling_preliminary_b_instance_deploy_20180726.csv')
    instance_interferences = data_process.handle_app_interference(
        'data/b/scheduling_preliminary_b_app_interference_20180726.csv')
    res_file = open('2018-8-7-b-final.csv', 'w')
    final_instancesMap, final_sortedInstanceList = data_process.handle_instance(
        '2018-8-7-b-res.csv')
    print(len(final_instancesMap))

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

    print(len(init_instance_map))
    for i in range(4):
        count = 0
        # for instance_id, instance in init_instance_map.items():
        reversed = True
        if i % 2 == 0:
            reversed = False
        init_instances = sorted(init_instance_map.items(), reverse=reversed)
        print(init_instances[0][1])
        # init_instances = init_instance_map.items().sort(reverse=reversed)
        for j in range(len(init_instance_map)):
            instance_id = init_instances[j][0]
            instance = init_instances[j][1]
        # for key in init_instance_map.keys().
            if instance_id == 'inst_87783':
                print('安排实例', instance_id, instance.appId, instance.machineId)
            if instance.final_machineId is not None:
                continue
            final_instance = final_instancesMap.get(instance_id)
            if final_instance is None:
                if instance_id == 'inst_87783':
                    print('无目标机器')
                continue
            machine = machinesMap.get(final_instance.final_machineId)
            if instance_id == 'inst_87783':
                print('目标机器:', machine.machineId)
            if instance.machineId == final_instance.final_machineId:
                instance.final_machineId = final_instance.final_machineId
                res_file.write(instance.instanceId + ',' + machine.machineId + '\n')
                if instance_id == 'inst_87783':
                    print('实例目标机器和当前所在机器一值')
                continue
            assign_path = []
            if tell_constrains(instance, machine, appsMap, residual_machine_disk,
                               residual_machine_cpu,
                               residual_machine_mem, machine_instances_num_map, residual_machine_m,
                               residual_machine_p, residual_machine_pm, instance_interferences, False):
                instance.final_machineId = machine.machineId
                assign_path.append([instance.instanceId, machine.machineId])
                res_file.write(instance.instanceId + ',' + machine.machineId + '\n')
                update_state(instance, instance.machineId, instance.final_machineId,
                             machine_instances_map, machine_instances_num_map, appsMap,
                             residual_machine_p, residual_machine_m, residual_machine_pm,
                             residual_machine_disk,
                             residual_machine_cpu, residual_machine_mem)
            else:
                instances = machine_instances_map.get(machine.machineId)
                # if instances is not None:
                    # if instance_id == 'inst_87783':
                    #     print('先去安排目标机器中的已有实例', len(instances))
                for instance2 in instances:
                    if instance2.instanceId == 'inst_87783':
                        print('instanceId:', instance2.instanceId, instance2.appId, instance2.machineId)
                    final_instance2 = final_instancesMap.get(instance2.instanceId)
                    if final_instance2 is None:
                        continue
                    machine2 = machinesMap.get(final_instance2.final_machineId)
                    if instance2.instanceId == 'inst_87783':
                        print('目标机器：', machine2.machineId)
                    if instance2.final_machineId is not None:
                        if instance2.instanceId == 'inst_87783':
                            print('此实例一倍安排')
                        continue
                    if instance2.machineId == final_instance2.final_machineId:
                        instance2.final_machineId = final_instance2.final_machineId
                        res_file.write(instance2.instanceId + ',' + machine2.machineId + '\n')
                        if instance2.instanceId == 'inst_87783':
                            print('此实例的目标机器与当前所在机器一致')
                        continue
                    if tell_constrains(instance2, machine2, appsMap, residual_machine_disk,
                                       residual_machine_cpu,
                                       residual_machine_mem, machine_instances_num_map,
                                       residual_machine_m,
                                       residual_machine_p, residual_machine_pm,
                                       instance_interferences, False):
                        instance2.final_machineId = machine2.machineId
                        assign_path.append([instance2.instanceId, machine2.machineId])
                        res_file.write(instance2.instanceId + ',' + machine2.machineId + '\n')
                        update_state(instance2, instance2.machineId, instance2.final_machineId,
                                     machine_instances_map, machine_instances_num_map, appsMap,
                                     residual_machine_p, residual_machine_m, residual_machine_pm,
                                     residual_machine_disk,
                                     residual_machine_cpu, residual_machine_mem)
                    else:
                        if instance2.instanceId == 'inst_87783':
                            print('遍历机器寻找可插入空间')
                        is_assign = False
                        for machineId, machine3 in sortedMachineList:
                            if instance2.machineId == machineId:
                                continue
                            if tell_constrains(instance2, machine3, appsMap, residual_machine_disk,
                                               residual_machine_cpu,
                                               residual_machine_mem, machine_instances_num_map,
                                               residual_machine_m,
                                               residual_machine_p, residual_machine_pm,
                                               instance_interferences):
                                assign_path.append([instance2.instanceId, machine3.machineId])
                                update_state(instance2, instance2.machineId, machine3.machineId,
                                             machine_instances_map, machine_instances_num_map,
                                             appsMap,
                                             residual_machine_p, residual_machine_m,
                                             residual_machine_pm,
                                             residual_machine_disk,
                                             residual_machine_cpu, residual_machine_mem)
                                instance2.machineId = machine3.machineId
                                if instance2.instanceId == 'inst_87783':
                                    print('插在机器：', machine3.machineId)
                                res_file.write(
                                    instance2.instanceId + ',' + machine3.machineId + '\n')
                                break
                    if tell_constrains(instance, machine, appsMap, residual_machine_disk,
                                       residual_machine_cpu,
                                       residual_machine_mem, machine_instances_num_map,
                                       residual_machine_m,
                                       residual_machine_p, residual_machine_pm,
                                       instance_interferences):
                        instance.final_machineId = machine.machineId
                        update_state(instance, instance.machineId, instance.final_machineId,
                                     machine_instances_map, machine_instances_num_map, appsMap,
                                     residual_machine_p, residual_machine_m, residual_machine_pm,
                                     residual_machine_disk,
                                     residual_machine_cpu, residual_machine_mem)
                        res_file.write(instance.instanceId + ',' + machine.machineId + '\n')
                        break
            if instance.final_machineId is not None:
                # print(assign_path)
                pass
            else:
                if instance.instanceId == 'inst_87783':
                    print('instance未迁移成功:', instance.instanceId)
                count += 1
        print('第', i, '次全部未安排:', count)

    # count = 0
    # for instance_id, instance in init_instance_map.items():
    #     # print('安排实例', instance_id)
    #     if instance.final_machineId is not None:
    #         continue
    #     final_instance = final_instancesMap.get(instance_id)
    #     if final_instance is None:
    #         continue
    #     machine = machinesMap.get(final_instance.final_machineId)
    #     if instance.machineId == final_instance.final_machineId:
    #         instance.final_machineId = final_instance.final_machineId
    #         continue
    #     assign_path = []
    #     if tell_constrains(instance, machine, appsMap, residual_machine_disk, residual_machine_cpu,
    #                        residual_machine_mem, machine_instances_num_map, residual_machine_m,
    #                        residual_machine_p, residual_machine_pm, instance_interferences):
    #         instance.final_machineId = machine.machineId
    #         assign_path.append([instance.instanceId, machine.machineId])
    #         update_state(instance, instance.machineId, instance.final_machineId, machine_instances_map, machine_instances_num_map, appsMap,
    #                      residual_machine_p, residual_machine_m, residual_machine_pm,
    #                      residual_machine_disk,
    #                      residual_machine_cpu, residual_machine_mem)
    #         res_file.write(instance.instanceId + ',' + machine.machineId + '\n')
    #     else:
    #         instances = machine_instances_map.get(machine.machineId)
    #         for instance2 in instances:
    #             final_instance2 = final_instancesMap.get(instance2.instanceId)
    #             if final_instance2 is None:
    #                 continue
    #             machine2 = machinesMap.get(final_instance2.final_machineId)
    #             if instance2.final_machineId is not None:
    #                 continue
    #             if instance2.machineId == final_instance2.final_machineId:
    #                 instance2.final_machineId = final_instance2.final_machineId
    #                 continue
    #             if tell_constrains(instance2, machine2, appsMap, residual_machine_disk,
    #                                residual_machine_cpu,
    #                                residual_machine_mem, machine_instances_num_map,
    #                                residual_machine_m,
    #                                residual_machine_p, residual_machine_pm, instance_interferences):
    #                 instance2.final_machineId = machine2.machineId
    #                 assign_path.append([instance2.instanceId, machine2.machineId])
    #                 update_state(instance2, instance2.machineId, instance2.final_machineId,
    #                              machine_instances_map, machine_instances_num_map, appsMap,
    #                              residual_machine_p, residual_machine_m, residual_machine_pm,
    #                              residual_machine_disk,
    #                              residual_machine_cpu, residual_machine_mem)
    #                 res_file.write(instance2.instanceId + ',' + machine2.machineId + '\n')
    #             else:
    #                 for machineId, machine3 in sortedMachineList:
    #                     if instance2.machineId == machineId:
    #                         continue
    #                     if tell_constrains(instance2, machine3, appsMap, residual_machine_disk,
    #                                        residual_machine_cpu,
    #                                        residual_machine_mem, machine_instances_num_map,
    #                                        residual_machine_m,
    #                                        residual_machine_p, residual_machine_pm,
    #                                        instance_interferences):
    #
    #                         assign_path.append([instance2.instanceId, machine3.machineId])
    #                         update_state(instance2, instance2.machineId, machine3.machineId,
    #                                      machine_instances_map, machine_instances_num_map, appsMap,
    #                                      residual_machine_p, residual_machine_m,
    #                                      residual_machine_pm,
    #                                      residual_machine_disk,
    #                                      residual_machine_cpu, residual_machine_mem)
    #                         instance2.machineId = machine3.machineId
    #                         res_file.write(instance2.instanceId + ',' + machine3.machineId + '\n')
    #                         break
    #             if tell_constrains(instance, machine, appsMap, residual_machine_disk,
    #                                residual_machine_cpu,
    #                                residual_machine_mem, machine_instances_num_map,
    #                                residual_machine_m,
    #                                residual_machine_p, residual_machine_pm,
    #                                instance_interferences):
    #                 instance.final_machineId = machine.machineId
    #                 update_state(instance, instance.machineId, instance.final_machineId,
    #                              machine_instances_map, machine_instances_num_map, appsMap,
    #                              residual_machine_p, residual_machine_m, residual_machine_pm,
    #                              residual_machine_disk,
    #                              residual_machine_cpu, residual_machine_mem)
    #                 res_file.write(instance.instanceId + ',' + machine.machineId + '\n')
    #                 break
    #     if instance.final_machineId is not None:
    #         # print(assign_path)
    #         pass
    #     else:
    #         # print('instance未迁移成功:', instance.instanceId)
    #         count += 1
    # print('第二次全部未安排:', count)
    #
    # count = 0
    # for instance_id, instance in init_instance_map.items():
    #     if instance.final_machineId is not None:
    #         continue
    #     final_instance = final_instancesMap.get(instance_id)
    #     if final_instance is None:
    #         continue
    #     machine = machinesMap.get(final_instance.final_machineId)
    #     print('安排实例', instance_id, instance.appId, ' target machine:', machine.machineId)
    #     if instance.machineId == final_instance.final_machineId:
    #         instance.final_machineId = final_instance.final_machineId
    #         continue
    #     assign_path = []
    #     instances = machine_instances_map.get(machine.machineId)
    #     print('机器已有实例数量:', len(instances))
    #
    #     if tell_constrains(instance, machine, appsMap, residual_machine_disk, residual_machine_cpu,
    #                        residual_machine_mem, machine_instances_num_map, residual_machine_m,
    #                        residual_machine_p, residual_machine_pm, instance_interferences, True):
    #         instance.final_machineId = machine.machineId
    #         assign_path.append([instance.instanceId, machine.machineId])
    #         update_state(instance, instance.machineId, instance.final_machineId,
    #                      machine_instances_map, machine_instances_num_map, appsMap,
    #                      residual_machine_p, residual_machine_m, residual_machine_pm,
    #                      residual_machine_disk,
    #                      residual_machine_cpu, residual_machine_mem)
    #         res_file.write(instance.instanceId + ',' + machine.machineId + '\n')
    #     else:
    #         instances = machine_instances_map.get(machine.machineId)
    #         for instance2 in instances:
    #             print(instance2.instanceId, instance2.appId, instance2.final_machineId)
    #             final_instance2 = final_instancesMap.get(instance2.instanceId)
    #             if final_instance2 is None:
    #                 print('-=-=-=-=-==-')
    #                 continue
    #             machine2 = machinesMap.get(final_instance2.final_machineId)
    #             if instance2.final_machineId is not None:
    #                 print('此实例被固定住1：', instance2.instanceId, instance2.appId, instance2.final_machineId)
    #                 continue
    #             if instance2.machineId == final_instance2.final_machineId:
    #                 instance2.final_machineId = final_instance2.final_machineId
    #                 print('此实例被固定住2：', instance2.instanceId, instance2.appId, instance2.final_machineId)
    #                 continue
    #             print('准备迁移实例', instance2.instanceId)
    #             if tell_constrains(instance2, machine2, appsMap, residual_machine_disk,
    #                                residual_machine_cpu,
    #                                residual_machine_mem, machine_instances_num_map,
    #                                residual_machine_m,
    #                                residual_machine_p, residual_machine_pm, instance_interferences):
    #                 instance2.final_machineId = machine2.machineId
    #                 assign_path.append([instance2.instanceId, machine2.machineId])
    #                 update_state(instance2, instance2.machineId, instance2.final_machineId,
    #                              machine_instances_map, machine_instances_num_map, appsMap,
    #                              residual_machine_p, residual_machine_m, residual_machine_pm,
    #                              residual_machine_disk,
    #                              residual_machine_cpu, residual_machine_mem)
    #                 res_file.write(instance2.instanceId + ',' + machine2.machineId + '\n')
    #             else:
    #                 for machineId, machine3 in sortedMachineList:
    #                     if instance2.machineId == machineId:
    #                         continue
    #                     if tell_constrains(instance2, machine3, appsMap, residual_machine_disk,
    #                                        residual_machine_cpu,
    #                                        residual_machine_mem, machine_instances_num_map,
    #                                        residual_machine_m,
    #                                        residual_machine_p, residual_machine_pm,
    #                                        instance_interferences):
    #                         assign_path.append([instance2.instanceId, machine3.machineId])
    #                         update_state(instance2, instance2.machineId, machine3.machineId,
    #                                      machine_instances_map, machine_instances_num_map, appsMap,
    #                                      residual_machine_p, residual_machine_m,
    #                                      residual_machine_pm,
    #                                      residual_machine_disk,
    #                                      residual_machine_cpu, residual_machine_mem)
    #                         instance2.machineId = machine3.machineId
    #                         res_file.write(instance2.instanceId + ',' + machine3.machineId + '\n')
    #                         break
    #             if tell_constrains(instance, machine, appsMap, residual_machine_disk,
    #                                residual_machine_cpu,
    #                                residual_machine_mem, machine_instances_num_map,
    #                                residual_machine_m,
    #                                residual_machine_p, residual_machine_pm,
    #                                instance_interferences):
    #                 instance.final_machineId = machine.machineId
    #                 update_state(instance, instance.machineId, instance.final_machineId,
    #                              machine_instances_map, machine_instances_num_map, appsMap,
    #                              residual_machine_p, residual_machine_m, residual_machine_pm,
    #                              residual_machine_disk,
    #                              residual_machine_cpu, residual_machine_mem)
    #                 res_file.write(instance.instanceId + ',' + machine.machineId + '\n')
    #                 break
    #     if instance.final_machineId is not None:
    #         # print(assign_path)
    #         pass
    #     else:
    #         print('instance未迁移成功:', instance.instanceId)
    #         count += 1
    # print('第三次全部未安排:', count)

    # count = 0
    # while count < len(init_instance_map):
    #     has_assign_num = 0
    #     count2 = 0
    #     for instance_id, instance in init_instance_map.items():
    #         print('count2:', count2, len(init_instance_map))
    #         count2 += 1
    #         if instance.final_machineId is not None:
    #             has_assign_num += 1
    #             continue
    #         final_instance = final_instancesMap.get(instance_id)
    #         # if instance_id == 'inst_23673':
    #         #     print(instance_id, instance, final_instance)
    #         machine = machinesMap.get(final_instance.final_machineId)
    #         if produce_seed.tell_disk_constraint(instance, machine, appsMap, residual_machine_disk):
    #             continue
    #         if produce_seed.tell_cpu_constraint(instance, machine, appsMap, residual_machine_cpu):
    #             continue
    #         if produce_seed.tell_mem_constraint(instance, machine, appsMap, residual_machine_mem):
    #             continue
    #         if produce_seed.tell_app_interference_constraint(instance, machine, appsMap,
    #                                                          machine_instances_num_map,
    #                                                          instance_interferences):
    #             continue
    #         if produce_seed.tell_m_constraint(instance, machine, appsMap, residual_machine_m):
    #             continue
    #         if produce_seed.tell_p_constraint(instance, machine, appsMap, residual_machine_p):
    #             continue
    #         if produce_seed.tell_pm_constraint(instance, machine, appsMap, residual_machine_pm):
    #             continue
    #         instance.final_machineId = final_instance.final_machineId
    #         machine_instances_map[instance.final_machineId].append(instance)
    #         # if instance_id == 'inst_23673':
    #         #     print(instance.machineId)
    #         if instance in machine_instances_map[instance.machineId]:
    #             machine_instances_map[instance.machineId].remove(instance)
    #         # init_instance_map.pop(instance_id)
    #         if machine_instances_num_map.get(instance.final_machineId).get(instance.appId) is None:
    #             machine_instances_num_map[instance.final_machineId][instance.appId] = 1
    #         else:
    #             machine_instances_num_map[instance.final_machineId][instance.appId] += 1
    #         machine_instances_num_map[instance.machineId][instance.appId] -= 1
    #         residual_machine_p[instance.machineId] += appsMap[instance.appId].p
    #         residual_machine_m[instance.machineId] += appsMap[instance.appId].m
    #         residual_machine_pm[instance.machineId] += appsMap[instance.appId].pm
    #         residual_machine_disk[instance.machineId] += appsMap[instance.appId].disk
    #         residual_machine_p[instance.final_machineId] -= appsMap[instance.appId].p
    #         residual_machine_m[instance.final_machineId] -= appsMap[instance.appId].m
    #         residual_machine_pm[instance.final_machineId] -= appsMap[instance.appId].pm
    #         residual_machine_disk[instance.final_machineId] -= appsMap[instance.appId].disk
    #         for i in range(T):
    #             residual_machine_cpu[instance.machineId][i] += appsMap[instance.appId].cpus[
    #                 i]
    #             residual_machine_cpu[instance.final_machineId][i] -= appsMap[instance.appId].cpus[
    #                 i]
    #         for i in range(T):
    #             residual_machine_mem[instance.machineId][i] += appsMap[instance.appId].mems[
    #                 i]
    #             residual_machine_mem[instance.final_machineId][i] -= appsMap[instance.appId].mems[
    #                 i]
    #         count += 1
    #         res_file.write(instance.instanceId + ',' + instance.machineId + '\n')
    #     if has_assign_num == len(init_instance_map):
    #         print(has_assign_num, len(init_instance_map))
    #         break
    for instance_id, instance in instancesMap.items():
        # if instance_id == 'inst_21379':
        #     print(appsMap[instance.appId].cpus)
        #     score = [0 for i in range(T)]
        #     for instance in machine_instances_map.get(final_instancesMap.get(instance_id).final_machineId):
        #         print(instance.instanceId, appsMap[instance.appId].cpus)
        #         for i in range(T):
        #             score[i] += appsMap[instance.appId].cpus[i]
        #     print('score:', score, max(score))
        if instance.final_machineId is None:
            res_file.write(
                instance_id + ',' + final_instancesMap.get(instance_id).final_machineId + '\n')
    res_file.close()


transfer_instance()
