from __future__ import division
import random
import math
import sys, getopt
import json
import numpy as np
import rad
import TDA
import mixed_task_builder
import task_generator

tasksinBkt=10
UStart=1
UEnd=100
totalRuns = 50
hardTaskPercentage = 20
numOfTasks = 10

resultstring = ''

for uti in xrange(UStart, UEnd + 1, 1):
    numfail = 0 # per utilization level

    percentageU = uti / 100

    for tasksets_amount in range(1,totalRuns + 1,1):


        tasks = task_generator.taskGeneration_rounded(numOfTasks, uti)
        # use mixed_task_builder to put some add-on in the set
        hardTasks = []
        softTasks = []
        # here I set alpha as 2
        tasks = mixed_task_builder.taskGeneration(tasks, hardTasks, softTasks, hardTaskPercentage, 2)

        sortedTasks = sorted(tasks, key=lambda item: item['period'])

        #######################################################
        # SCAIR-RM (normal mode)
        ######################################################

        if rad.scair_dm(sortedTasks) == False:
            print "normal mode FAIL"
            numfail += 1

        #######################################################
        # safe mode
        ######################################################

        elif TDA.hardTDAtest(tasks) != 0:
            print "safe mode FAIL"
            numfail += 1

        #######################################################
        # transient phase I
        ######################################################

        elif rad.transientIAnalysis(tasks) == 0:
            print "transient phase I FAIL"
            numfail += 1

        #######################################################
        # transient phase II
        ######################################################

        elif rad.transientIIAnalysis(tasks) == False:
            print "transient phase II FAIL"
            numfail += 1


    acceptanceRatio = 1 - (numfail / totalRuns)
    resultstring = resultstring + repr(acceptanceRatio) + ','

    print "acceptanceRatio:", acceptanceRatio
    # y[u] = acceptanceRatio

with open('schedtest' + '_tasks_' + repr(numOfTasks) + '_' + 'hard_perc' + repr(hardTaskPercentage) + '_' + '.txt', 'a') as f:
    f.write(resultstring)