'''
Author: Kuan-Hsun Chen
'''

from __future__ import division
import random
import math
import numpy
import sort_task_set

def taskGeneration(tasks, hardTasks, softTasks, hardTaskPercentage, alpha):
    numberOfHardTasks = (hardTaskPercentage / 100 * len(tasks))
    print numberOfHardTasks
    allTasks=[]
    # we first pick up certain number of task as hard task
    for i in range(int(numberOfHardTasks)):
        pos=random.randint(0, len(tasks)-1)
        task=tasks[pos]
        task['firstSub']=task['execution']*0.4 #c_{i,1}
        task['secondSub']=task['execution']*0.4 #c_{i,2}
        task['pPart']=task['execution']*0.1 #p_i
        task['qPart']=task['execution']*0.1 #q_i
        # suppose C_{i,2} = c_{i,2}+qi or c_{i,2}+c_{i,s}
        # different possible suspension lengths
        task['suspTime'] = random.uniform(0.01 * (task['period'] - task['execution']), 0.1 * (task['period'] - task['execution']))  # S^N_i # short suspension
        # task['suspTime'] = random.uniform(0.1 * (task['period'] - task['execution']),
        #                                   0.6 * (task['period'] - task['execution']))  # S^N_i # medium suspension
        # task['suspTime'] = random.uniform(0.6 * (task['period'] - task['execution']),
        #                                   1 * (task['period'] - task['execution']))  # S^N_i # long suspension
        # task['suspTime'] = random.uniform(0.01 * (task['period'] - task['execution']), 1 * (task['period'] - task['execution']))  # S^N_i # mixed suspension

        # task['suspTime']=task['execution']*0.2 #S^N_i
        task['local']=task['suspTime']*alpha #c_{i,s} = S^N_i * alpha
        task['response']=task['suspTime'] #t_{r,i}
        task['mode']=0 # 0 normal suspension / 1 is abnormal / 2 is mode-change legacy
        task['type']='hard'
        hardTasks.append(task)
        allTasks.append(task)
        del tasks[pos]
    # for the rest tasks in taskset, we assign them as soft tasks
    for task in tasks:
        task['firstSub']=task['execution']*0.4 #c_{i,1}
        task['secondSub']=task['execution']*0.4 #c_{i,2}
        task['pPart']=task['execution']*0.1 #p_i
        task['qPart']=task['execution']*0.1 #q_i
        # suppose C_{i,2} = c_{i,2}+qi or c_{i,2}+c_{i,s}
        # different possible suspension lengths
        task['suspTime'] = random.uniform(0.01 * (task['period'] - task['execution']),
                                          0.1 * (task['period'] - task['execution']))  # S^N_i # short suspension
        # task['suspTime'] = random.uniform(0.1 * (task['period'] - task['execution']),
        #                                   0.6 * (task['period'] - task['execution']))  # S^N_i # medium suspension
        # task['suspTime'] = random.uniform(0.6 * (task['period'] - task['execution']),
        #                                   1 * (task['period'] - task['execution']))  # S^N_i # long suspension
        # task['suspTime'] = random.uniform(0.01 * (task['period'] - task['execution']), 0.5 * (task['period'] - task['execution']))  # S^N_i # custom suspension
        # task['suspTime']=task['execution']*0.2 #S^N_i
        task['local']=task['suspTime']*alpha #c_{i,s} = S^N_i * alpha
        task['response']=task['suspTime'] #t_{r,i}
        task['mode']=0 # mode 0 normal suspension / 1 is abnormal / 2 is mode-change legacy
        task['type']='soft'
        softTasks.append(task)
        allTasks.append(task)
    allTasks=hardTasks+softTasks
    hardTasks=sort_task_set.sort(hardTasks, 'period')
    softTasks=sort_task_set.sort(softTasks, 'period')
    return sort_task_set.sort(allTasks, 'period')
