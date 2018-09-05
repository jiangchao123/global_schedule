#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/9/1 11:37
Author  : jiangchao08
Site    : 
File    : final_solver.py
Software: PyCharm Community Edition

"""
import random
import common.final.sa_util2 as sa_util
import common.final.constraints_util as constraints_util


def sa(instancesMap, appsMap, sortedInstanceList, sortedMachineList, instance_machine_map,
       machinesMap, machine_cpu_score, residual_machine_p, residual_machine_m,
       residual_machine_pm, residual_machine_disk, residual_machine_mem,
       machine_apps_num_map, instance_interferences, machine_instances_map, used_machine_cpu, residual_machine_cpu):
    T_current = 150000
    T_min = 50
    r = 0.8
    cross_step = 5
    val = 0
    while T_current > T_min:
        print(T_current, T_min)
        change_list = []
        diff = 0
        machine_scores = []
        if random.random() < 0.5:
            # 交叉
            step = 0
            change_machines = []
            while True:
                instance_index1 = random.randint(0, len(instancesMap) - 1)
                instance_index2 = random.randint(0, len(instancesMap) - 1)
                app1 = appsMap.get(sortedInstanceList[instance_index1][1].appId)
                app2 = appsMap.get(sortedInstanceList[instance_index2][1].appId)
                machineId1 = instance_machine_map.get(sortedInstanceList[instance_index1][0])
                machineId2 = instance_machine_map.get(sortedInstanceList[instance_index2][0])
                if machineId1 in change_machines or machineId2 in change_machines or machineId1 == machineId2:
                    continue
                # print('m1, m2', machineId1, machineId2)
                if not constraints_util.tell_cross_constraint(machineId1, machineId2, app1, app2,
                                                              residual_machine_p,
                                                              residual_machine_m,
                                                              residual_machine_pm,
                                                              residual_machine_disk,
                                                              residual_machine_mem,
                                                              machine_apps_num_map,
                                                              instance_interferences, residual_machine_cpu, tell_cpu=True):
                    step += 1
                    change_machines.append(machineId1)
                    change_machines.append(machineId2)
                    machine_val1, machine_val2 = sa_util.score_cross_change(app1,
                                                                            machinesMap[machineId1],
                                                                            app2,
                                                                            machinesMap[machineId2],
                                                                            used_machine_cpu, machine_instances_map)
                    machine_scores.append([machine_val1, machine_val2])
                    change_list.append(
                        [machineId1, machineId2, instance_index1, instance_index2, app1,
                         app2, machine_val1, machine_val2])
                    origin_val1 = machine_cpu_score[machineId1]
                    origin_val2 = machine_cpu_score[machineId2]
                    diff += (origin_val1 + origin_val2) - (machine_val1 + machine_val2)
                    if step == cross_step:
                        break
            # print('cross:', diff)
            if diff > 0:
                print('cross', val, diff)
                val += diff
                for machineId1, machineId2, instance_index1, instance_index2, app1, app2, machine_val1, machine_val2 in change_list:
                    instance_machine_map[sortedInstanceList[instance_index1][0]] = machineId2
                    instance_machine_map[sortedInstanceList[instance_index2][0]] = machineId1
                    sa_util.cross_update_info(machineId1, machineId2, instance_index1,
                                              instance_index2,
                                              app1,
                                              app2, machine_val1, machine_val2,
                                              machine_instances_map, sortedInstanceList,
                                              residual_machine_p, residual_machine_m,
                                              residual_machine_pm,
                                              residual_machine_disk, used_machine_cpu,
                                              residual_machine_mem,
                                              machine_apps_num_map, machine_cpu_score)
        # else:
        #     # 变异
        #     while True:
        #
        #         instance_index1 = random.randint(0, len(instancesMap) - 1)
        #         app1 = appsMap.get(sortedInstanceList[instance_index1][1].appId)
        #         origin_machineId = instance_machine_map.get(sortedInstanceList[instance_index1][0])
        #         machine_index = random.randint(0, len(machinesMap) - 1)
        #         machineId = sortedMachineList[machine_index][0]
        #         if not constraints_util.tell_mut_constraint(machineId, app1, residual_machine_p,
        #                                                     residual_machine_m, residual_machine_pm,
        #                                                     residual_machine_disk,
        #                                                     residual_machine_mem,
        #                                                     machine_apps_num_map,
        #                                                     instance_interferences,
        #                                                     residual_machine_cpu, has_cpu=True):
        #             break
        #     change_list.append([sortedInstanceList[instance_index1][0], machineId])
        #     origin_machine_val, target_machine_val = sa_util.score_mut_change(
        #         machinesMap[machineId], app1,
        #         machinesMap[origin_machineId], machine_instances_map, used_machine_cpu)
        #     origin_origin_val = machine_cpu_score[origin_machineId]
        #     target_origin_val = machine_cpu_score[machineId]
        #     diff = (origin_origin_val + target_origin_val) - (
        #         origin_machine_val + target_machine_val)
        #     # print('mut:', diff)
        #     if diff > 0:
        #         print('mut', val, diff)
        #         val += diff
        #         for change in change_list:
        #             instance_machine_map[change[0]] = change[1]
        #             sa_util.mut_update_info(machineId, sortedInstanceList[instance_index1][1], app1,
        #                                     origin_machineId, machine_instances_map,
        #                                     residual_machine_p, residual_machine_m,
        #                                     residual_machine_pm,
        #                                     residual_machine_disk, used_machine_cpu,
        #                                     residual_machine_mem,
        #                                     machine_apps_num_map, residual_machine_cpu)
        #         machine_cpu_score[machineId] = target_machine_val
        #         machine_cpu_score[origin_machineId] = origin_machine_val
        T_current -= 1
    return val, 0
