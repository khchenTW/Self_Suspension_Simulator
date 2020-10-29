""" The time-demand analysis functions.

:filename TDA.py
:Author: Kuan-Hsun Chen (kuan-hsun.chen@tu-dortmund.de)
:Date: 03.09.19

"""


from __future__ import division
import math
import random
import numpy

def determineWorkload(task, higherPriorityTasks, criteria, time):
    workload = task[criteria]
    for i in higherPriorityTasks:
        jobs = math.ceil(time / i['period'])
        workload += jobs * i[criteria]
    return workload

def min_time(tasks, criteria, numD):
    # test deadline first
    #workload = determineWorkload(task, higherPriorityTasks, criteria, task['deadline'])
    # initiate starting time for recursive TDA
    copy = list(tasks)
    task = copy[len(copy)-1]
    del copy[len(copy)-1]
    t = task[criteria]
    for i in copy:
        t += i[criteria]
    # resursive TDA
    while(t < task['deadline']*numD):
        workload = determineWorkload(task, copy, criteria, t)
        if workload <= t:
            return t
        else:
            t = workload
    return -1


def Workload_Contrained(T,C,t):
    return C*math.ceil((t)/T)

def Workload_Contrained_transient(respTimeFirstSub, suspTime, partialC,T,C,t):
    return partialC + C*math.ceil((t-(T-(respTimeFirstSub+suspTime)))/T)

def TDA(task,HPTasks):
    # workload from all tasks suspension
    #C=task['execution']
    C=task['firstSub']+task['secondSub']+task['suspTime']
    R=C
    D=task['deadline']

    while True:
        I=0
        for itask in HPTasks:
            I=I+Workload_Contrained(itask['period'], itask['execution'],R)
            # I=I+Workload_Contrained(itask['period'], itask['firstSub']+itask['secondSub']+itask['suspTime'],R)
        if R>D:
            return R
        if R < I+C:
            R=I+C
        else:
            return R

def TDAhard(task,HPTasks):
    # workload only from hard tasks
    C=task['firstSub']+task['secondSub']+task['local']
    R=C
    D=task['deadline']

    while True:
        I=0
        for itask in HPTasks:
            #I=I+Workload_Contrained(itask['period'], itask['execution'],R)
            I=I+Workload_Contrained(itask['period'], itask['firstSub']+itask['secondSub']+itask['local'],R)
        if R>D:
            return R
        if R < I+C:
            R=I+C
        else:
            return R

# def TDAhard_onlySecondSub(C,D,HPTasks):
#     # workload only from hard tasks
#     # C=task['secondSub']
#     R=C
#     # D=task['deadline']
#
#     while True:
#         I=0
#         for itask in HPTasks:
#             #I=I+Workload_Contrained(itask['period'], itask['execution'],R)
#             I=I+Workload_Contrained(itask['period'], itask['firstSub']+itask['secondSub']+itask['local'],R)
#         if R>D:
#             return R
#         if R < I+C:
#             R=I+C
#         else:
#             return R

def TDAhard_transient(task,HPTasks, respTimeFirstSub):
    # workload only from hard tasks
    C=task['firstSub']+task['secondSub']+task['local']
    R=C
    D=task['deadline']

    while True:
        I=0
        for itask in HPTasks:
            #I=I+Workload_Contrained(itask['period'], itask['execution'],R)
            I=I+Workload_Contrained_transient(respTimeFirstSub, itask['suspTime'], itask['firstSub'] + itask['secondSub'], itask['period'], itask['firstSub']+itask['secondSub']+itask['local'], R)
        if R>D:
            return R
        if R < I+C:
            R=I+C
        else:
            return R

def TDAtest(tasks):
    x = 0
    fail = 0
    for i in tasks:
        hpTasks = tasks[:x]
        RT=TDA(i, hpTasks)
        if RT > i['deadline']:
            fail = 1
            break
        #after this for loop, fail should be 0
        x+=1
    return fail

def hardTDAtest(tasks):
    hardTasks = []
    for task in tasks:
        if task['type'] == 'hard':
            hardTasks.append(task)
    print "The number of hard tasks is :", len(hardTasks)

    x = 0
    fail = 0
    for i in hardTasks:
        hpTasks = hardTasks[:x]
        RT=TDAhard(i, hpTasks)
        if RT > i['deadline']:
            fail = 1
            break
        #after this for loop, fail should be 0
        x+=1
    return fail
def sort(tasks, criteria, reverse_order):
    return sorted(tasks, key=lambda item:item[criteria], reverse=reverse_order)
