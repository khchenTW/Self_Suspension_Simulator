""" sorting functions for tasks and events

:filename sort_task_set.py
:Author: Kuan-Hsun Chen (kuan-hsun.chen@tu-dortmund.de)
:Date: 03.09.19

"""


from __future__ import division
import random
import math
import numpy
import sys, getopt

def sort(tasks, criteria):
    return sorted(tasks, key=lambda item:item[criteria])

def sortEvent(tasks, criteria):
    return sorted(tasks, key=lambda item:item.criteria)
