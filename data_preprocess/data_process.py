#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/7/21 14:10
Author  : jiangchao08
Site    : 
File    : data_process.py
Software: PyCharm Community Edition

"""
import pandas as pd
import bean.machine as bean_machine
import common.string_util as string_util
import bean.app as bean_app
import bean.instance as bean_instance
import numpy as np

T = 98


def handle_machine(filepath):
    """
    加载机器文件
    :param filepath:
    :return:
    """
    data_set = pd.read_csv(filepath, header=None, index_col=None)
    print(data_set.head())
    machinesMap = {}
    for row in data_set.values:
        machineId = row[0]
        cpu = row[1]
        mem = row[2]
        disk = row[3]
        p = row[4]
        m = row[5]
        pm = row[6]
        if machineId not in machinesMap:
            machine = bean_machine.Machine(machineId, cpu, mem, disk, p, m, pm)
            machinesMap[machineId] = machine
    return machinesMap, sorted(machinesMap.items(), key=lambda d: d[1].cpu, reverse=True)


def handle_app(filepath):
    """
    加载应用列表文件
    :param filepath:
    :return:
    """
    data_set = pd.read_csv(filepath, header=None, index_col=None)
    appsMap = {}
    for row in data_set.values:
        appid = row[0]
        cpus = string_util.stringToVector(row[1])
        mems = string_util.stringToVector(row[2])
        disk = row[3]
        p = row[4]
        m = row[5]
        pm = row[6]
        if appid not in appsMap:
            app = bean_app.App(appid, cpus, mems, disk, p, m, pm)
            appsMap[appid] = app
    return appsMap, sorted(appsMap.items())


def handle_instance(filepath):
    """
    加载实例文件
    :param filepath:
    :return:
    """
    data_set = pd.read_csv(filepath, header=None, index_col=None)
    instancesMap = {}
    for row in data_set.values:
        if len(row) == 3:
            instanceId = row[0]
            appId = row[1]
            machineId = row[2]
            try:
                if np.isnan(machineId):
                    machineId = None
            except TypeError:
                pass
            if instanceId not in instancesMap:
                # print(instanceId, appId, machineId)
                instance = bean_instance.Instance(instanceId, appId, machineId, None)
                instancesMap[instanceId] = instance
        else:
            instanceId = row[0]
            machineId = row[1]
            if instanceId not in instancesMap:
                instance = bean_instance.Instance(instanceId, None, None, machineId)
                instancesMap[instanceId] = instance
    return instancesMap, sorted(instancesMap.items())


def handle_app_interference(filepath):
    """
    加载应用约束文件
    :return:
    """
    data_set = pd.read_csv(filepath, header=None, index_col=None)
    app_interferences = {}
    for row in data_set.values:
        if app_interferences.get(row[0]) is None:
            app_interferences[row[0]] = {}
        app_interferences[row[0]][row[1]] = row[2]
    return app_interferences


def handle_app_possible_machines(appsMap, sortedInstanceList, sortedMachineList):
    print('handle_app_possible_machines')
    app_possible_machines = {}
    instance_possible_machines_length = []
    instance_possible_machines_length_map = {}
    for appId, app in appsMap.items():
        app_possible_machines[appId] = []
        for machineId, machine in sortedMachineList:
            if app.disk > machine.disk:
                continue
            if app.p > machine.p:
                continue
            if app.m > machine.m:
                continue
            if app.pm > machine.pm:
                continue
            for i in range(T):
                if app.cpus[i] > machine.cpu:
                    continue
                if app.mems[i] > machine.mem:
                    continue
            app_possible_machines[appId].append(machineId)
    index = 0
    for instanceId, instance in sortedInstanceList:
        instance_possible_machines_length.append(len(app_possible_machines[instance.appId]))
        if instance_possible_machines_length_map.get(
                len(app_possible_machines[instance.appId])) is None:
            instance_possible_machines_length_map[len(app_possible_machines[instance.appId])] = []
        instance_possible_machines_length_map[len(app_possible_machines[instance.appId])].append(
            index)
        index += 1
    print('instance_possible_machines_length: ', instance_possible_machines_length)
    return app_possible_machines, instance_possible_machines_length, sorted(
        instance_possible_machines_length_map.items())

# handle_machine('../data/scheduling_preliminary_machine_resources_20180606.csv')