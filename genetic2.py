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
import common.fitness2 as fitness
from common.exe_time import exeTime
import array
import random
import numpy
import data_preprocess.data_process as data_process

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from scoop import futures

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", array.array, typecode='i', fitness=creator.FitnessMin)

machinesMap, sortedMachineList = data_process.handle_machine(
    'data/scheduling_preliminary_machine_resources_20180606.csv')
appsMap, sortedAppList = data_process.handle_app(
    'data/scheduling_preliminary_app_resources_20180606.csv')
instancesMap, sortedInstanceList = data_process.handle_instance(
    'data/scheduling_preliminary_instance_deploy_20180606.csv')
instance_interferences = data_process.handle_app_interference(
    'data/scheduling_preliminary_app_interference_20180606.csv')

app_possible_machines, instance_possible_machines_length = data_process.handle_app_possible_machines(
    appsMap,
    sortedInstanceList,
    sortedMachineList)


# def generate_instance_possibleMachines():

def individualToInstance(individual):
    instances = []
    for index in individual:
        instance = sortedInstanceList[index][1]
        instances.append(instance)
    return instances


def evalTSP(individual):
    # print(individual)
    machine_instances_map, assignSize = individual_to_machine_instanses(individual)
    obj = fitness.fitnessfun(machine_instances_map, machinesMap, appsMap, instance_interferences,
                             assignSize,
                             assignSize)
    return obj,


def individual_to_machine_instanses(individual):
    machine_instances_map = {}
    for i in range(len(individual)):
        machineId = sortedMachineList[individual[i]][0]
        instance = sortedInstanceList[i][1]
        if machine_instances_map.get(machineId) is None:
            machine_instances_map[machineId] = []
        machine_instances_map[machineId].append(instance)
    return machine_instances_map, len(individual)


def cxTwoPoint(ind1, ind2):
    """Executes a two-point crossover on the input :term:`sequence`
    individuals. The two individuals are modified in place and both keep
    their original length.

    :param ind1: The first individual participating in the crossover.
    :param ind2: The second individual participating in the crossover.
    :returns: A tuple of two individuals.

    This function uses the :func:`~random.randint` function from the Python
    base :mod:`random` module.
    """
    size = min(len(ind1), len(ind2))
    step = 0
    while step < 200:
        step += 1
        if random.random() < 0.5:
            cxpoint1 = random.randint(1, size - 1)
            cxpoint2 = random.randint(1, size - 2)
            if cxpoint2 >= cxpoint1:
                cxpoint2 += 1
            else:  # Swap the two cx points
                cxpoint1, cxpoint2 = cxpoint2, cxpoint1
            # print(ind1[cxpoint1], ind1[cxpoint2])
            tmp = ind1[cxpoint1]
            ind1[cxpoint1] = ind1[cxpoint2]
            ind1[cxpoint2] = tmp
            # print(ind1[cxpoint1], ind1[cxpoint2])

            tmp = ind2[cxpoint1]
            ind2[cxpoint1] = ind2[cxpoint2]
            ind2[cxpoint2] = tmp
    return ind1, ind2


@exeTime
def train_model():
    random.seed(169)

    IND_SIZE = len(instancesMap)
    toolbox = base.Toolbox()

    # Attribute generator
    toolbox.register("indices", random.randint, 0, len(machinesMap) - 1)

    # Structure initializers
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.indices, IND_SIZE)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("mate", cxTwoPoint)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.005)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", evalTSP)
    toolbox.register("map", futures.map)

    pop = toolbox.population(n=80)

    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    algorithms.eaSimple(pop, toolbox, 0.7, 0.2, 300, stats=stats,
                        halloffame=hof)
    # print(hof[0])
    print(evalTSP(hof[0]))
    machine_instances_map, _ = individual_to_machine_instanses(hof[0])
    # print(machine_instances_map)
    return machine_instances_map


if __name__ == '__main__':

    res_file = open('2018-7-23-res.csv', 'w')
    machine_instances_map, _ = train_model()
    for machineId, instances in machine_instances_map.items():
        for instance in instances:
            res_file.write(str(instance.instanceId) + ',' + str(machineId) + '\n')
    res_file.close()
