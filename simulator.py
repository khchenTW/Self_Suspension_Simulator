""" The main body of the event-driven simulator.

:filename simulator.py
:Author: Kuan-Hsun Chen (kuan-hsun.chen@tu-dortmund.de)
:Date: 09.10.19

"""

from __future__ import division
import random
import math
import numpy as np
import operator
import sys

# for simulator initialization
class MissRateSimulator:
    def __init__( self, n, tasks, simmode, threshold = 0 ):
        self.statusTable = [[0 for x in range(6)] for y in range(n)] # 6th for accumulated lateness of all instances of one task
        self.sysmode = 0 # 0:normal and 1:safe
        self.normaltime = 0 # the normaltime over the simulation
        # @Lea, I define the variables I want to use here
        self.safetime = 0 # the safetime over the simulation
        self.totaltime = 0 # the total time over the simulation
        self.eventList = []
        self.tasks = tasks
        self.lowestHardIdx = -1
        self.lowestSoftIdx = -1
        self.stampSIM = []
        self.h = -1
        self.n = n
        self.simmode = simmode # 0: no soft-task retrying, 1: retrying, and 2: retrying with a threshold
        self.retryThreshold = threshold
        self.retryCount = 0
        self.initState()
        self.fr = 0.0
        self.distribution = 0
        self.systemlateness = 0 # avg system lateness

    class eventClass( object ):
        # This is the class of events
        def __init__( self, case, delta, idx ):
            self.eventType = case
            self.delta = delta
            self.idx = idx

        def case(self):
            if self.eventType == 0:
                return "release" #the first subtask
            elif self.eventType == 1:
                return "suspension" #the second subtask
            else:
                return "deadline" #check the deadline event

        def updateDelta( self, elapsedTime ):
            self.delta = self.delta - elapsedTime
            if self.delta < 0:
                print "There is a event delta less than 0: "+self.case()+str(self.idx)
                print elapsedTime
                print self.delta + elapsedTime
    """
    The status table for the simulator
    per col with 4 rows:
    workload
    # of release
    # of misses
    # of deadlines = this should be less than release
    processed
    """
    def tableReport( self ):
        print self.tasks
        for i, e in enumerate(self.eventList):
            print "event "+str(i)+" from task "+str(e.idx)
            print e.case()
            print e.delta

        print
        systemlateness = 0
        bestcaselateness = 0
        for x in range(self.n):
            # add the average lateness of the task to the total system lateness
            if self.statusTable[x][2] > 0:
                # divide accumulated lateness by # deadline misses
                systemlateness += (self.statusTable[x][5]/self.statusTable[x][2])
                # compute what we call best-case lateness
                # if self.tasks[x]['type'] == 'soft':
                    # bestcaselateness += self.tasks[x]['secondSub']+self.tasks[x]['local']
            print "task"+str(x)+": "
            for y in range(6):
                print self.statusTable[x][y]
        print
        print "avg. system lateness: " + str(systemlateness) + " seconds"
        self.systemlateness = systemlateness
        # print "best-case system lateness: " + str(bestcaselateness) + " seconds"

    def findTheHighestWithWorkload( self ):
        # Assume that the fixed priority is given in the task set.
        # if there is no workload in the table, returns -1
        hidx = -1
        for i in range(self.n):
            if self.statusTable[i][0] != 0:
                hidx = i
                break
            else:
                pass
        if hidx == -1:
            if self.sysmode == 1:
                # print "System is idle so back to normal "+str(self.totaltime)
                self.sysmode = 0
        return hidx

    def stopHardOffloading( self ):
        # this function is called by the mode change in the suspension event of higher priority task
        # Those lower priority hard tasks with workload should stop the pre-processing and the following offload by changing the task mode
        for idx in range(self.n):
            if self.tasks[idx]['mode'] == 0 and self.statusTable[ idx ][ 0 ] > 0 and self.tasks[idx]['type'] == 'hard':
                # the skip part
                if self.statusTable[ idx ][4] <= self.tasks[idx]['firstSub']:
                    # print "Skip the pPart"
                    self.statusTable[ idx ][0] = 0 #force it skip pPart


    def stopAllOffloading( self ):
        # this function is called by the mode change from the suspension event of higher priority task
        # those lower priority tasks with workload should stop the pre-processing and the following offload by changing the task mode
        # The following procedure handles case 2 that some tasks not yet reach t_{s,k} but have workload from the release
        for idx in range(self.n):
            if self.tasks[idx]['mode'] == 0 and self.statusTable[ idx ][ 0 ] > 0:
                # the skip part
                if self.statusTable[ idx ][4] <= self.tasks[idx]['firstSub']:
                    # print "Skip the pPart"
                    self.statusTable[ idx ][0] = 0 #force it skip pPart

            # Tasks which have no workload but waiting for suspention event in the list (case 3) is with task mode 0,
            # in which the secondSub will be released accordingly. The next instance will be released without offloading
            # due to the fact that system mode was set to safe mode already by the mode change.
            # case 4 is covered directly

    def faultDistribution(self, idx):
        value = False
        if self.distribution == 0:
            # uniform distribution
            value = True if random.random() < self.fr else False
        else:
            # poisson distribution
            pf = 1 - np.exp(-self.fr * self.tasks[idx]['response'])
            # pf = 1 - np.exp(-fr)
            # print pf
            pn = 1 - pf
            value = np.random.choice([False, True], 1, p=[pn, pf])[0]
        return value

    def suspension( self, idx, distribution=0 ):
        # this is the suspension event that is not happened between any of two events
        # print "Suspension event add workload"
        # print "suspension got response"+str(idx)
        return self.workloadDetermine(idx, 1)


    def workloadDetermine( self, idx, typ = 0):
        # first check the task mode
        if self.fr == 0.0:
            # always in normal mode
            self.statusTable[ idx ][ 0 ] += self.tasks[idx]['secondSub']+self.tasks[idx]['qPart']
        else:
            # this condition decide if a server response is received until t_{r,k}.
            if self.faultDistribution( idx ):
                # this is about transient Phase I
                # got a fault, mode changes, sys.mode is abnormal
                if self.simmode == 1:
                    # The cautious Protocol
                    self.statusTable[ idx ][ 0 ] += self.tasks[idx]['secondSub']+self.tasks[idx]['local']
                    self.stopAllOffloading()
                    self.tasks[idx]['mode'] = -1 # the release of the local execution is done

                elif self.simmode == 2:
                    # The Striving Protocol: just retry for soft-tasks
                    if self.tasks[idx]['type'] == 'hard':
                        # re-execute the hard task
                        self.statusTable[ idx ][ 0 ] += self.tasks[idx]['secondSub']+self.tasks[idx]['local']
                        self.tasks[idx]['mode'] = -1 # the release of the local execution is done
                    else:
                        # abort the soft task
                        self.statusTable[ idx ][ 0 ] += 0
                    #the case that soft-task retry
                    if self.sysmode == 0:
                        self.stopHardOffloading()
                self.sysmode = 1
                # print "System is changed to Safe mode due to a fault at: "+str(self.totaltime)

            else:
                # no fault, so system mode won't change
                if self.sysmode == 0:
                    self.statusTable[ idx ][ 0 ] += self.tasks[idx]['secondSub']+self.tasks[idx]['qPart']

                else:
                    # anyway already get the response, just continue the post-processed execution.
                    self.statusTable[ idx ][ 0 ] += self.tasks[idx]['secondSub']+self.tasks[idx]['qPart']

                    # transient phase II should be considered here:
                    if self.tasks[idx]['type'] != 'soft':
                        if self.tasks[idx]['mode'] != 2:
                            # since now a soft-task gets a response, start the transient phase II back to the normal mode
                            # Option IIa: check the workload of the lowesthardtask, implying that all hard tasks have finished.
                            # abort all released soft tasks.
                            if self.workload( self.lowestHardIdx ) == 0:
                                # print "System is changed back to Normal mode"
                                for idxR in range(self.n):
                                    if self.tasks[ idxR ][ 'type' ] == 'soft':
                                        self.statusTable[ idxR ][ 0 ] = 0
                                self.sysmode = 0
                                # print "The lowestHardIdx has no workload, so sys.mode is changed back to normal "+str(self.totaltime)
                        else:
                            # as the soft task was aborted already
                            pass
        return 0

    def release( self, idx ):


        # create release event to the event list
        # periodic setup
        self.eventList.append(self.eventClass(0, self.tasks[idx]['period'], idx))


        # add the workload to the table corresponding entry according to the system mode

        if self.sysmode == 0:
            # system normal mode
            self.statusTable[ idx ][ 0 ] += self.tasks[idx]['firstSub']+self.tasks[idx]['pPart']
            self.tasks[idx]['mode'] = 0
        else:
            # system safe mode: case 1 is covered here.

            if self.simmode == 1:
                self.statusTable[ idx ][ 0 ] += self.tasks[idx]['firstSub']
                self.tasks[idx]['mode'] = 1
            elif self.simmode == 2:
                if self.tasks[idx]['type'] == 'soft':
                    # return protocol:
                    if self.statusTable[ idx ][ 0 ] > 0 : # meaning that it misses its deadline
                        # don't release more workload, so no deadline event, and mark it
                        self.tasks[idx]['mode'] = 2
                    else:
                        self.statusTable[ idx ][ 0 ] += self.tasks[idx]['firstSub']+self.tasks[idx]['pPart']
                        self.tasks[idx]['mode'] = 1
                else:
                    self.statusTable[ idx ][ 0 ] += self.tasks[idx]['firstSub']
                    self.tasks[idx]['mode'] = 1

        if self.tasks[idx]['mode'] != 2:
            # create deadline event to the event list
            self.eventList.append(self.eventClass(2, self.tasks[idx]['deadline'], idx))

        # init the process tracking
        self.statusTable[ idx ][4] = 0

        # sort the eventList
        self.eventList = sorted(self.eventList, key=operator.attrgetter('delta'))

        # decide the highest priority task in the system
        self.h = self.findTheHighestWithWorkload()
        if self.h == -1:
            for i in range(self.n):
                print "task:", i
                print self.tasks[i]['firstSub']+self.tasks[i]['pPart']
                print self.tasks[i]['firstSub']
                print self.statusTable[i][0]

            print "BUG: after release, there must be at least one task with workload."
            # @Lea: this is only for catching the exception
            self.safetime = 0
            self.normaltime = 1
            return -1

        self.statusTable[ idx ][ 1 ]+=1
        self.tableReport()
        return 0

    def deadline( self, idx ):
        # check if the targeted task in the table has workload.
        # print "Table in task"+str(idx)+" deadline event with h"+str(self.h)
        if self.workload( idx ) != 0:
            # print "task"+str(idx)+" misses deadline"
            self.statusTable[ idx ][ 2 ] += 1
            self.tableReport()
        self.statusTable[ idx ][ 3 ]+=1
        # print

        # check if it is the time to change system mode back to normal.
        if self.sysmode == 1:
            # print self.workload( self.lowestHardIdx )
            if idx == self.lowestHardIdx and self.workload( idx ) == 0:
                # print "System is changed back to Normal mode"
                # This is the deadline event of the lowest priority hard task, and it has no workload.
                for idxR in range(self.n):
                    if self.tasks[ idxR ][ 'type' ] == 'soft':
                        self.statusTable[ idxR ][ 0 ] = 0
                self.sysmode = 0
                # print "System is changed back to normal "+str(self.totaltime)
        return 0


    def event_to_dispatch( self, event, fr, distribution ):
        # take out the delta from the event
        self.elapsedTime( event )

        # execute the corresponding event functions
        switcher = {
            0: self.release,
            1: self.suspension,
            2: self.deadline,
        }
        func = switcher.get( event.eventType, lambda: "ERROR" )
        # execute the event
        if func == self.suspension:
            # the second parameter is for changing the distribution of fault rate
            exception = func( event.idx, distribution )
        else:
            exception = func( event.idx )
        if exception != 0:
            print "There is an error from Event "+str(event.idx)
        return exception


    def elapsedTime( self, event ):
        currentDelta = event.delta
        # record the system status along with the events
        # @Lea
        tmpDelta = currentDelta
        # update the workloads in the table
        # print "now execute:"+str(self.h)
        while (tmpDelta):
            # find the next highest priority task with workload
            self.h = self.findTheHighestWithWorkload()
            if self.h == -1:
                # processor Idle
                tmpDelta = 0
                # print "Processor is idle so system mode change back / keep in normal"
                self.sysmode = 0
            elif tmpDelta >= self.statusTable[ self.h ][ 0 ]:
                # the distance from the current event to the next is more than the current highest priority workload:
                if self.h == self.lowestHardIdx and self.sysmode == 1:
                    # print "the lowestHardTask is finished at: "+str(self.totaltime) + " so sys.mode change back to normal "
                    # print self.workload( self.lowestHardIdx )
                    self.sysmode = 0
                tmpDelta = tmpDelta - self.statusTable[ self.h ][ 0 ]
                # to record the processed time
                self.statusTable[ self.h ][ 4 ] += self.statusTable[ self.h ][ 0 ]
                #finish the execution of the highest priority task
                self.statusTable[ self.h ][ 0 ] = 0

                if self.tasks[self.h]['mode'] >= 0:
                    # this task finishes its first workload
                    # after S^N_k, there should be a response event if system is normal
                    if self.sysmode == 0:
                        if tmpDelta >= self.tasks[self.h]['response']:
                            # print "response inside the delta: "+str(self.h)
                            # the response happens before the next event,
                            # based on the sysmode, the workload can be added accordingly
                            self.workloadDetermine(self.h)
                            self.tasks[self.h]['mode'] = -1
                        else:
                            # the response happens after the next event
                            # be aware of that this suspension may experience sysmode ==1
                            self.eventList.append(self.eventClass(1, self.tasks[self.h]['response']-tmpDelta+currentDelta, self.h))
                            self.tasks[self.h]['mode'] = -1
                            # sort
                            self.eventList = sorted(self.eventList, key=operator.attrgetter('delta'))
                    elif self.sysmode == 1:
                        if self.simmode == 1:
                            # no matter which type of tasks, all execute locally
                            self.statusTable[ self.h ][ 0 ] += self.tasks[self.h]['secondSub']+self.tasks[self.h]['local']
                            self.tasks[self.h]['mode'] = -1
                        else:
                            if self.tasks[self.h]['type'] == 'hard':
                                # the system is in abnormal mode, so there is no suspension but local execution.
                                self.statusTable[ self.h ][ 0 ] += self.tasks[self.h]['secondSub']+self.tasks[self.h]['local']
                                self.tasks[self.h]['mode'] = -1
                            else:
                                # soft tasks are offloaded irregardless if it doesn't miss it's deadline yet
                                if self.tasks[self.h]['mode'] == 2:
                                    self.tasks[self.h]['mode'] = -1
                                    pass
                                else:
                                    if tmpDelta >= self.tasks[self.h]['response']:
                                        # the response happens before the next event,
                                        # based on the sysmode, the workload can be added accordingly
                                        self.workloadDetermine(self.h)
                                        self.tasks[self.h]['mode'] = -1
                                    else:
                                        # the response happens after the next event
                                        self.eventList.append(self.eventClass(1, self.tasks[self.h]['response']-tmpDelta+currentDelta, self.h))
                                        self.tasks[self.h]['mode'] = -1
                                        # sort
                                        self.eventList = sorted(self.eventList, key=operator.attrgetter('delta'))
                else:
                    # this is the case that the second release after the post-processed is done
                    pass

                # @Lea, this is the measurement
                if self.sysmode == 1:
                    self.safetime+=self.statusTable[self.h][0]


            elif tmpDelta < self.statusTable[self.h][0]:
                # the distance from the current event to the next is less than the current highest priority workload.
                # the current highest priority one spends the time completely
                self.statusTable[ self.h ][ 0 ] -= tmpDelta
                self.statusTable[ self.h ][ 4 ] += tmpDelta
                # add remaining workload of the current task (which misses the deadline) to accumulate the lateness
                if event.case() == 'deadline':
                    self.statusTable[ self.h ][ 5 ] += self.statusTable[ self.h ][ 0 ]
                tmpDelta = 0

        # update the deltas of remaining events in the event list.
        if len(self.eventList) == 0:
            print "BUG: there is no event in the list to be updated."
        for e in self.eventList:
            e.updateDelta( currentDelta )
        # print
        self.totaltime += currentDelta

    def getNextEvent(self):
        # get the next event from the event list
        event = self.eventList.pop(0)
        # print "Get Event: "+event.case() + " from " + str(event.idx)
        return event

    def systemSafeRate( self ):
        # @Lea, here is the way I calculate the ratio
        # return the safe rate of the system
        # print "Return the system safe rate:" + str(self.safetime/(self.safetime+self.normaltime))
        if self.totaltime == 0:
            return 0
        return self.safetime/(self.totaltime)

    def releasedJobs( self, idx ):
        # return the number of released jobs of idx task in the table
        # print "Released jobs of " + str(idx) + " is " + str(statusTable[ idx ][ 1 ])
        return self.statusTable[ idx ][ 1 ]

    def numDeadlines( self, idx ):
        # return the number of past deadlines of idx task in the table
        # print "Deadlines of " + str(idx) + " is " + str(statusTable[ idx ][ 1 ])
        return self.statusTable[ idx ][ 3 ]

    def releasedMisses( self, idx ):
        # return the number of misses of idx task in the table
        return self.statusTable[ idx ][ 2 ]

    def workload( self, idx ):
        # return the remaining workload of idx task in the table
        return self.statusTable[ idx ][ 0 ]

    def initState( self ):
        # init
        for idx, task in enumerate(self.tasks):
            if task['type'] == 'hard':
                # to the end of the list, this idx must be the lowest priority task among hard tasks.
                self.lowestHardIdx = idx
            elif task['type'] == 'soft':
                self.lowestSoftIdx = idx
        # print "The lowest priority hard task: "+str(self.lowestHardIdx)
        # print


        #print self.tasks
        self.eventList = []

        # task release together at 0 without delta / release from the lowest priority task
        # for using periodic task model, the event queue should be sorted again
        tmp=range(len(self.tasks))
        tmp = tmp[::-1]
        for idx in tmp:
            self.statusTable[ idx ][ 0 ] = 0
            self.statusTable[ idx ][ 3 ] = self.statusTable[ idx ][ 1 ]
            self.eventList.append(self.eventClass(0,0,idx))
        self.eventList = sorted(self.eventList, key=operator.attrgetter('delta'))
        self.tableReport()
        #print

    def dispatcher(self, targetedNumber, fr, distribution):
        self.fr = fr
        self.distribution = distribution
        # Stop when the number of released jobs in the lowest priority task is equal to the targeted number.
        # print self.tasks
        while( targetedNumber != self.numDeadlines( self.n - 1 )):
            if len(self.eventList) == 0:
                print "BUG: there is no event in the dispatcher"
                break
            else:
                e = self.getNextEvent()
                exp = self.event_to_dispatch(e, fr, distribution )
                if exp == -1:
                    break
        # print "Stop at task "+str(e.idx)
        self.tableReport()




