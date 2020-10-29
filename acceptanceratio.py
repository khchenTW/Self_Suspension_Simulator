""" The interface of deploying experiments.

:filename experiments.py
:Author: Lea Schoenberger (lea.schoenberger@tu-dortmunde), Kuan-Hsun Chen (kuan-hsun.chen@tu-dortmund.de)
:Date: 09.10.19

"""


from __future__ import division
from simulator import MissRateSimulator
import sys
import numpy as np
import time
import decimal
import TDA # this is enhanced from ECRTS'18
import task_generator
import mixed_task_builder
import schedtest_paper

import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import rcParams

rcParams.update({'font.size': 15})
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Tahoma']

rcParams['ps.useafm'] = True
rcParams['pdf.use14corefonts'] = True
rcParams['text.usetex'] = True

marker = ['o','v','^','s','p','d','o', 'v','+','*','D','x','+','p',]
colors = ['r','g','b','k','m','c','c','m','k','b','r','g','y','m','b']
line = [':',':',':','-','-','-','-','-','-']
line = [':',':',':','-','-','-.','-.','-.','-.','-','-','-','-','-','-']
line = ['-','-','-.',':',':',':','-.','-.','-.','-','-','-','-','-','-']
line = ['-','-','-','--','--','--','-.','-.','-.','-','-','-','-','-','-']

# Setting for Fig4:
# faultRate = [10**-2]
# faultRate = np.arange(0.1,5.1,0.1)
#faultRate = [0.1, 0.5, 1]
# faultRate = [0.01] # 1%
# faultRate = [0.005] # 0.5%
faultRate = [0.001] # 0.1%
# faultRate = [0.0005] # 0.05%
# faultRate = [0.0001] # 0.01%
# utilization = [30]
utilization = np.arange(1,101,1)
# utilization = np.arange(1,21,1)
hardTaskRate = [20]
# jobnum = 17
jobnum = 50
distribution = 1 # 0 is uniform, 1 is possion random process
# setsDiscarded = 0
discardedOverviewService = []
discardedOverviewReturn = []


# task generation
def taskGeneWithTDA(uti, numOfTasks, hardTaskPercentage):
    cont = 0
    while (1):
        # use UUnifast to generate a normal task set without further properties.
        tasks = task_generator.taskGeneration_p(numOfTasks, uti)
        # use mixed_task_builder to put some add-on in the set
        hardTasks = []
        softTasks = []
        # here I set alpha as 2
        tasks = mixed_task_builder.taskGeneration(tasks, hardTasks, softTasks, hardTaskPercentage, 2) # removed by Lea


        print tasks

        #checking for task models

        # first of all, all the execution time should not be 0.
        for task in tasks:
            if task['execution'] <= 0:
                print task['execution']
                cont = 1 #just regenerate without testing

        if cont == 1:
            print "There is a task having no execution time"
            continue

        if TDA.TDAtest( tasks ) == 0 and TDA.hardTDAtest( tasks ) == 0:
            print "TDA pass for all tasks"
            print "HARD TDA pass for HARD tasks"
            break
        else:
            # the TDA with the normal case cannot pass
            pass
    return tasks

# task generation with schedulability test from the paper (Theorems 10 and 13)
def taskGenerationWithSchedtest(uti, numOfTasks, hardTaskPercentage):
    setsDiscardedService = 0
    setsDiscardedReturn = 0
    global discardedOverviewReturn
    global discardedOverviewService
    cont = 0
    for run in range(100):
        # use UUnifast to generate a normal task set without further properties.
        tasks = task_generator.taskGeneration_p(numOfTasks, uti)
        # use mixed_task_builder to put some add-on in the set
        hardTasks = []
        softTasks = []
        # here I set alpha as 2
        tasks = mixed_task_builder.taskGeneration(tasks, hardTasks, softTasks, hardTaskPercentage, 2)
        tasks = sorted(tasks, key=lambda item: item['period'])

        print tasks

        #checking for task models

        # first of all, all the execution time should not be 0.
        for task in tasks:
            if task['execution'] <= 0:
                print task['execution']
                cont = 1 #just regenerate without testing

        if cont == 1:
            print "There is a task having no execution time"
            # continue

        if schedtest_paper.schedtest_ServiceOnly(tasks) != 0:
            setsDiscardedService = setsDiscardedService + 1
        if schedtest_paper.schedtest_ReturnOnly(tasks) != 0:
            setsDiscardedReturn = setsDiscardedReturn + 1

            # break
        # else:
        #     # the schedulability test is not passed
        #     setsDiscarded = setsDiscarded + 1
        #     print "schedulability test NOT passed"
        #     # pass
    discardedOverviewService.append(setsDiscardedService)
    discardedOverviewReturn.append(setsDiscardedReturn)
    discarded_service_file = 'DISCARDED_SERVICE.txt'
    discarded_return_file = 'DISCARDED_RETURN.txt'
    with open(discarded_service_file, "a") as resultfile:
        resultfile.write(str(setsDiscardedService) + ',\n')
    with open(discarded_return_file, "a") as resultfile:
        resultfile.write(str(setsDiscardedReturn) + ',\n')
    return tasks


def taskSetInput(n, uti, hr, tasksets_amount, filename):
    # tasksets = [taskGeneWithTDA(uti, n, hr) for x in range(tasksets_amount)]
    tasksets = [taskGenerationWithSchedtest(uti, n, hr) for x in range(tasksets_amount)]
    np.save(filename, tasksets)
    return filename

# experiement wrapper
def experiments_sim(n, fr, uti, hr, inputfile, simmode, distribution, threshold = 0):
    Outputs = True
    filePrefix = 'sim'
    folder = 'figures/'

    SimRateList = []

    # List for recording runtime
    runtimeSIM = []

    tasksets = np.load(inputfile+'.npy')
    tasksets_amount = len(tasksets)

    # try if there are outputs already for the given configurations
    try:
        filename = 'outputs' + str(faultRate) + '/sim' + str(n) + '_' + str(uti) + '_' + str(
            tasksets_amount) + '_' + str(hr) + '_Sim'
        SIM = np.load(filename + '.npy')
        filename = 'outputs' + str(faultRate) + '/simt' + str(n) + '_' + str(uti) + '_' + str(
            tasksets_amount) + '_' + str(hr) + '_Sim'
        runtimeSIM = np.load(filename + '.npy')
    except IOError:
        Outputs = False

    if Outputs is False:
        runtimeSIM = []
        for idx, tasks in enumerate(
                tasksets):  # for each task set (e.g. if we create 50), we do the same experiment now, i.e., first x times one uti step, then next one
            # i.e. file output will have the first x lines results of one uti step, next x lines results of next uti step

            print "Running simulator"
            # simmode 1 is the original design without soft-task retrying
            # simmode 2 is the design with soft-task retrying
            # simmode 3 is the design with soft-task retrying and a threshold
            simulator = MissRateSimulator(n, tasks, simmode, threshold)

            # report the ratio over safe/all for the whole system

            t1 = time.clock()
            # start to dispatch the events, usage: (terminate condition, fault rate or lambda, unidistribution or poisson random process)
            simulator.dispatcher(jobnum, fr, distribution)
            diff = time.clock() - t1
            print ("--- Simulation %s seconds ---" % diff)
            runtimeSIM.append(diff)
            tmp = simulator.systemSafeRate()
            # resultperuti = [tmp, simulator.safetime, simulator.systemlateness]
            print ("--- Total time is %s ---" % simulator.totaltime)
            print ("--- Total safetime is %s ---" % simulator.safetime)
            print ("--- Safe over All Ratio is %s ---" % tmp)
            SimRateList.append(tmp)

            # resultfilename = 'result_hardperc_' + str(hr) + 'faultprob_' + str(fr) + 'simode_' + str(simmode) + 'th_' + str(threshold) + 'distribution' + distribution +'.txt'
            # resultfilename = 'campus_o2_' + 'result_hardperc_' + str(hr) + 'faultprob_' + str(fr) + 'simode_' + str(
            #     simmode) + 'th_' + str(threshold) + 'distribution' + distribution + '.txt'

            resultfilename_saferatio = 'RATIO__result_hardperc_' + str(hr) + 'faultprob_' + str(fr) + 'simode_' + str(
                simmode) + 'th_' + str(threshold) + 'distribution' + str(distribution) + '.txt'
            resultfilename_lateness = 'LATENESS__result_hardperc_' + str(hr) + 'faultprob_' + str(fr) + 'simode_' + str(
                simmode) + 'th_' + str(threshold) + 'distribution' + str(distribution) + '.txt'

            # for each uti step, new line with results
            # with open(resultfilename, "a") as resultfile:
            #     resultfile.write(str(resultperuti) + ',\n')
            with open(resultfilename_lateness, "a") as resultfile:
                resultfile.write(str(simulator.systemlateness) + ',\n')
            with open(resultfilename_saferatio, "a") as resultfile:
                resultfile.write(str(tmp) + ',\n')

        # filename = 'outputs/sim'+str(n)+'_'+str(uti)+'_'+str(power[por])+'_'+str(tasksets_amount)+'_Sim'
        #np.save(filename, SimRateList)
        # SIM = np.load(filename+'.npy')
        #filename = 'outputs/simt'+str(n)+'_'+str(uti)+'_'+str(power[por])+'_'+str(tasksets_amount)+'_Sim'
        #np.save(filename, runtimeSIM)

    print "Result for Safe Rate under fault rate: "+str(fr)+"_uti-"+str(uti)
    print "Ratio for Safe:"
    print SimRateList

    print ("SIM Avg %s seconds" %(reduce(lambda y, z: y + z, runtimeSIM)/len(runtimeSIM)))
    print "Simulation runtime:"
    print runtimeSIM
    print "========================="

    #The following code is for drawing figures.

    #pp = PdfPages(folder + "task" + repr(n) + "-" + filePrefix + '.pdf')

    #ind = np.arange(len(EMR))
    ##prune for leq 20 sets
    #print "Num of SIM:",len(SIM)
    #print "Num of CON:",len(CON)
    #print "Num of EMR:",len(EMR)
    #if len(EMR) > 20:
        #SIM = SIM[:20]
        #EMR = EMR[:20]
        #CON = CON[:20]
        #ind = np.arange(20) # the x locations for the groups

    #width = 0.15
    #title = 'Task Cardinality: '+ repr(n) + ', $U^N_{SUM}$: '+repr(uti)+'\%' + ', $P_i^A$: '+repr(fr)
    #plt.title(title, fontsize=20)
    #plt.grid(True)
    #plt.ylabel('Expected Miss Rate', fontsize=20)
    #plt.yscale("log")
    #plt.ylim([10**-5, 10**0])
    #pltlabels = []
    #for idt, tt in enumerate(EMR):
        #pltlabels.append('S'+str(idt))
    #plt.xticks(ind + width /2, pltlabels)
    #plt.tick_params(axis='both', which='major',labelsize=18)
    #print ind
    #try:
        #rects1 = plt.bar(ind-0.1, SIM, width, edgecolor='black')
        #rects2 = plt.bar(ind+0.1, CON, width, edgecolor='black')
        #rects3 = plt.bar(ind+0.3, EMR, width, edgecolor='black')
        #plt.legend((rects1[0], rects2[0], rects3[0]),('SIM', 'CON', 'Chernoff'), ncol=3, loc=9, bbox_to_anchor=(0.5, 1), prop={'size':20})
    #except ValueError:
        #print "Value ERROR!!!!!!!!!!"
    #figure = plt.gcf()
    #figure.set_size_inches([14.5,6])

    ##plt.show()
    #pp.savefig()
    #plt.clf()
    #pp.close()

def main():
    args = sys.argv
    if len(args) < 5:
        print "Usage: python experiments.py [mode] [number of tasks] [tasksets_amount] [uniform/poisson] [threshold]"
        return -1
    # this is used to choose the types of experiments.
    mode = int(args[1])
    n = int(args[2])
    # this is used to generate the number of sets you want to test / load the cooresponding input file.
    tasksets_amount = int(args[3])
    # this is used to decide the distribution
    distribution = int(args[4])
    # this is used to set threshold of retries for soft-tasks.
    if len(args) > 5:
        threshold = int(args[5])

    global discardedOverviewService
    global discardedOverviewReturn
    for hr in hardTaskRate:
        for fr in faultRate:
            if fr > 1:
                print "The fault rate range is [0,1]"
                return -1
            for uti in utilization:
                filename = 'inputs/'+str(n)+'_'+str(uti)+'_'+str(tasksets_amount)+'_'+str(hr)
                if mode == 0:
                    fileInput=taskSetInput(n, uti, hr, tasksets_amount, filename)
                    print "Generate Task sets:"
                    print np.load(fileInput+'.npy')
                    print 'discarded sets per utilization level (service protocol): ' + str(discardedOverviewService)
                    print 'discarded sets per utilization level (return protocol): ' + str(discardedOverviewReturn)
                    # np.load(fileInput + '.npy')
                elif mode == 1:
                    # used to get sim results
                    # print 'probability: ' + str(fr) + ' hard: ' + str(hr)
                    experiments_sim(n, fr, uti, hr, filename, mode, distribution)
                elif mode == 2:
                    # used to get sim results
                    # print 'probability: ' + str(fr) + ' hard: ' + str(hr)
                    experiments_sim(n, fr, uti, hr, filename, mode, distribution)
                elif mode == 3:
                    # used to get sim results
                    # print 'probability: ' + str(fr) + ' hard: ' + str(hr)
                    experiments_sim(n, fr, uti, hr, filename, mode, distribution, threshold)

                else:
                    raise NotImplementedError("Error: you use an experimental mode without implementation")

if __name__=="__main__":
    main()
