#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#

"""
Time    : 18/9/6 01:46
Author  : jiangchao08
Site    : 
File    : tmp.py
Software: PyCharm Community Edition

"""


def merge(file_a, file_b, file_c, file_d, file_e, out_put_name):
    dataset_a = open(file_a)
    dataset_b = open(file_b)
    dataset_c = open(file_c)
    dataset_d = open(file_d)
    dataset_e = open(file_e)

    res_file = open(out_put_name, 'w')

    for line in dataset_a:
        res_file.write(line)
    res_file.write('\n#\n')
    for line in dataset_b:
        res_file.write(line)
    res_file.write('\n#\n')
    for line in dataset_c:
        res_file.write(line)
    res_file.write('\n#\n')
    for line in dataset_d:
        res_file.write(line)
    res_file.write('\n#\n')
    for line in dataset_e:
        res_file.write(line)


merge('2018-9-1-final-a-1.0-res.csv', '2018-9-1-final-b-1.0-res.csv',
      '2018-9-1-final-c-1.0-res.csv', '2018-9-1-final-d-1.0-res.csv',
      '2018-9-1-final-e-1.0-res.csv', '2018-9-1-final-merge.csv')
