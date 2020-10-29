import math
import rad

def getFirstSegmentResponseTime(task, hpTasks):
    # compute response time of the first computation segment with SCAIR
    responsetime = rad.scair_dm_responsetimefirstsegment(task, hpTasks)
    return responsetime

def getCsharp(task):
    # C^\sharp
    wcet = task['firstSub'] + task['local'] + task['secondSub']
    return wcet

def getCflat(task):
    # C^\flat
    wcet = task['firstSub'] + task['secondSub'] + task['pPart']+ task['qPart']
    return wcet

def getWorkloadFunction1(task, delta):
    # Equation (1)
    cSharp = getCsharp(task)
    workload = task['pPart'] + (math.ceil((delta/task['period']))*cSharp)
    return workload

def getWorkloadFunction2(task, delta, hptasks):
    # Equation (2)
    cSharp = getCsharp(task)
    firstResponseTime = getFirstSegmentResponseTime(task, hptasks)
    workload = task['local'] + task['secondSub'] + (math.ceil((delta - (task['period'] - (firstResponseTime + task['suspTime'])))/task['period']) * cSharp)
    return workload

def getWorkloadReturnNon(task, delta):
    # last part of equation (7)
    cFlat = getCflat(task)
    workload = (math.ceil(delta/task['period'])+1) * cFlat
    return workload

def theoremService(task, hptasks):
    # Theorem 10
    wcet = getCsharp(task) + task['pPart']
    responsetimeUB = wcet
    deadline = task['deadline']

    while True:
        interference = 0
        for interfTask in hptasks:
            workloadByFunction1 = getWorkloadFunction1(interfTask, responsetimeUB)
            workloadByFunction2 = getWorkloadFunction2(interfTask, responsetimeUB, hptasks)
            interference = interference + max(workloadByFunction1,workloadByFunction2)

        if interference + wcet > deadline: # unschedulable if 0 is returned
            return 0
        elif interference + wcet < responsetimeUB:
            responsetimeUB = interference + wcet
        else:
            return responsetimeUB


def theoremReturn(task, hptasks):
    # Theorem 13
    wcet = getCsharp(task) + task['pPart']
    responsetimeUB = wcet
    deadline = task['deadline']

    while True:
        interference = 0
        for interfTask in hptasks:
            if interfTask['type'] == 'hard':
                workloadByFunction1 = getWorkloadFunction1(interfTask, responsetimeUB)
                workloadByFunction2 = getWorkloadFunction2(interfTask, responsetimeUB, hptasks)
                interference = interference + max(workloadByFunction1,workloadByFunction2)
            else:
                interference = interference + getWorkloadReturnNon(interfTask, responsetimeUB)

        if interference + wcet > deadline: # unschedulable if 0 is returned
            return 0
        elif interference + wcet < responsetimeUB:
            responsetimeUB = interference + wcet
        else:
            return responsetimeUB


def schedtest(tasks):
    # assume that tasks are sorted in such a way that tasks[0] has the shortest period, i.e., is the highest-priority task
    print "testing feasibility under normal behavior"
    resultNormal = rad.scair_dm(tasks)
    if not resultNormal:
        return 1

    for i in range(len(tasks)):
        resultService = 0
        resultReturn = 0
        hptasks = []
        if i != 0:
            hptasks = tasks[0:i] # first index included, last index not included (range)

        print "testing feasibility under the service protocol"
        resultService = theoremService(tasks[i],hptasks)
        if resultService == 0:
            return 1
        print "testing feasibility under the return protocol"
        resultReturn = theoremReturn(tasks[i], hptasks)
        if resultReturn == 0:
            return 1
    return 0

def schedtest_ServiceOnly(tasks):
    # assume that tasks are sorted in such a way that tasks[0] has the shortest period, i.e., is the highest-priority task
    print "testing feasibility under normal behavior"
    resultNormal = rad.scair_dm(tasks)
    if not resultNormal:
        return 1

    for i in range(len(tasks)):
        resultService = 0
        resultReturn = 0
        hptasks = []
        if i != 0:
            hptasks = tasks[0:i] # first index included, last index not included (range)

        print "testing feasibility under the service protocol"
        resultService = theoremService(tasks[i],hptasks)
        if resultService == 0:
            return 1
        # print "testing feasibility under the return protocol"
        # resultReturn = theoremReturn(tasks[i], hptasks)
        # if resultReturn == 0:
        #     return 1
    return 0

def schedtest_ReturnOnly(tasks):
    print "testing feasibility under normal behavior"
    resultNormal = rad.scair_dm(tasks)
    if not resultNormal:
        return 1

    # assume that tasks are sorted in such a way that tasks[0] has the shortest period, i.e., is the highest-priority task
    for i in range(len(tasks)):
        resultService = 0
        resultReturn = 0
        hptasks = []
        if i != 0:
            hptasks = tasks[0:i] # first index included, last index not included (range)

        # print "testing feasibility under the service protocol"
        # resultService = theoremService(tasks[i],hptasks)
        # if resultService == 0:
        #     return 1
        print "testing feasibility under the return protocol"
        resultReturn = theoremReturn(tasks[i], hptasks)
        if resultReturn == 0:
            return 1
    return 0




