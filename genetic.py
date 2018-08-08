#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/7/22 01:33
Author  : jiangchao08
Site    : 
File    : genetic.py
Software: PyCharm Community Edition

"""
import common.fitness as fitness
import common.produce_seed as produce_seed
from common.exe_time import exeTime
import array
import random
import numpy
import data_preprocess.data_process as data_process
import model.ga_crossover as ga_crossover

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

machinesMap, sortedMachineList = data_process.handle_machine(
    'data/scheduling_preliminary_machine_resources_20180606.csv')
for machineId, machine in sortedMachineList:
    print(machineId)
appsMap, sortedAppList = data_process.handle_app(
    'data/scheduling_preliminary_app_resources_20180606.csv')
instancesMap, sortedInstanceList = data_process.handle_instance(
    'data/scheduling_preliminary_instance_deploy_20180606.csv')
instance_interferences = data_process.handle_app_interference(
    'data/scheduling_preliminary_app_interference_20180606.csv')
app_possible_machines, instance_possible_machines_length, sorted_instance_possible_machines_length_list = \
    data_process.handle_app_possible_machines(
        appsMap,
        sortedInstanceList,
        sortedMachineList)

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", array.array, typecode='i', fitness=creator.FitnessMin)


# def generate_instance_possibleMachines():

def individualToInstance(individual):
    instances = []
    for index in individual:
        instance = sortedInstanceList[index][1]
        instances.append(instance)
    return instances


def evalTSP(individual):
    # print('init_individual: ', individual)
    # flight_possiblePositions = generate_instance_possibleMachines()
    instances = individualToInstance(individual)
    machine_instances_map, assignSize = produce_seed.randomGreedy(instances, appsMap,
                                                                  sortedMachineList,
                                                                  instance_interferences)
    obj = fitness.fitnessfun(machine_instances_map, machinesMap, appsMap, assignSize,
                             len(instances))
    return obj,


def init_individual():
    res = []
    for length, instanceIndexs in sorted_instance_possible_machines_length_list:
        res_sub = random.sample(instanceIndexs, len(instanceIndexs))
        res.extend(res_sub)
    return res


@exeTime
def train_model():
    random.seed(169)

    # IND_SIZE = len(instancesMap)
    toolbox = base.Toolbox()

    # # Attribute generator
    # toolbox.register("indices", random.sample, range(IND_SIZE), IND_SIZE)
    #
    # # Structure initializers
    # toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)


    # # Structure initializers
    toolbox.register("individual", tools.initIterate, creator.Individual, init_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("mate", ga_crossover.cxPartialyMatched,
                     instance_possible_machines_length=instance_possible_machines_length)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", evalTSP)

    pop = toolbox.population(n=300)

    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    algorithms.eaSimple(pop, toolbox, 0.7, 0.2, 1, stats=stats,
                        halloffame=hof)
    # print(hof[0])
    print(evalTSP(hof[0]))
    machine_instances_map = produce_seed.randomGreedy(individualToInstance(hof[0]),
                                                      appsMap, sortedMachineList,
                                                      instance_interferences)
    # print(machine_instances_map)
    return machine_instances_map


if __name__ == '__main__':
    res_file = open('2018-7-23-res.csv', 'w')
    machine_instances_map, _ = train_model()
    for machineId, instances in machine_instances_map.items():
        for instance in instances:
            res_file.write(str(instance.instanceId) + ',' + str(machineId) + '\n')
    res_file.close()
