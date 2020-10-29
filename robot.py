import sys
import numpy as np
import time
import csv

# laserscan = []
# odom = []
# tf = []
#
# with open('rb1_base__move_base/rb1_base__front_laser__scan__1.csv') as f:
#     laserscan = [float(s) for line in f.readlines() for s in line[:-1].split(',')]
#
# with open('rb1_base__move_base/rb1_base__robotnik_base_control__odom__1.csv') as f:
#     odom = [float(s) for line in f.readlines() for s in line[:-1].split(',')]
#     print(odom)
#
# with open('rb1_base__move_base/tf__1.csv') as f:
#     tf = [float(s) for line in f.readlines() for s in line[:-1].split(',')]
#     print(tf)
#
# period_laserscan = 60.0 / len(laserscan) * 1000.0 # to milliseconds
# wcet_laserscan = max(laserscan)
# print(period_laserscan)
# print(wcet_laserscan)
#
# period_odom = 60.0 / len(odom) * 1000.0 # to milliseconds
# wcet_odom = max(odom)
# print(period_odom)
# print(wcet_odom)
#
# period_tf = 60.0 / len(tf) * 1000.0 # to milliseconds
# wcet_tf = max(tf)
# print(period_tf)
# print(wcet_tf)

# offloaded_share = 0.2
# offloaded_share = 0.4
# offloaded_share = 0.6
offloaded_share = 0.7

wcet_laserscan = 6.73193
period_laserscan = 64.51612903225806
wcet_odom = 1.04565
period_odom = 60.0
wcet_tf = 0.332764
period_tf = 60.0

p_q_laserscan = wcet_laserscan * 0.1
p_q_odom = wcet_odom * 0.1
p_q_tf = wcet_tf * 0.1

local_laserscan = wcet_laserscan * offloaded_share
local_odom = wcet_odom * offloaded_share
local_tf = wcet_tf * offloaded_share

susp_laserscan = 0.5 * local_laserscan # due to alpha
susp_odom = 0.5 * local_odom
susp_tf = 0.5 * local_tf

laserscan = {'firstSub': ((wcet_laserscan - local_laserscan - p_q_laserscan - p_q_laserscan) / 2.0), 'secondSub': ((wcet_laserscan - local_laserscan - p_q_laserscan - p_q_laserscan) / 2.0),
             'execution': wcet_laserscan, 'pPart': p_q_laserscan, 'qPart': p_q_laserscan, 'local': local_laserscan, 'response': susp_laserscan, 'suspTime': susp_laserscan, 'deadline': period_laserscan, 'period': period_laserscan, 'mode': 0, 'type': 'soft'}

tf = {'firstSub': ((wcet_tf - local_tf - p_q_tf - p_q_tf) / 2.0), 'secondSub': ((wcet_tf - local_tf - p_q_tf - p_q_tf) / 2.0),
             'response': susp_tf, 'deadline': period_tf, 'execution': wcet_tf, 'pPart': p_q_tf, 'qPart': p_q_tf, 'local': local_tf, 'suspTime': susp_tf, 'period': period_tf, 'mode': 0, 'type': 'soft'}

odom = {'firstSub': ((wcet_odom - local_odom - p_q_odom - p_q_odom) / 2.0), 'secondSub': ((wcet_odom - local_odom - p_q_odom - p_q_odom) / 2.0),
             'execution': wcet_odom, 'pPart': p_q_odom, 'qPart': p_q_odom, 'local': local_odom, 'response': susp_odom, 'suspTime': susp_odom, 'deadline': period_odom, 'period': period_odom, 'mode': 0, 'type': 'hard'}

tasks = [laserscan,tf,odom]
print(tasks)