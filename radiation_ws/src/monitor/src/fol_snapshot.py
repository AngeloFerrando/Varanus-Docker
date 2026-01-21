#!/usr/bin/env python
import roslib
import rospy
from sortedcontainers import SortedDict
from threading import *
import numpy as np
from gazebo_msgs.msg import *
from std_msgs.msg import *
from geometry_msgs.msg import *

ws_lock = Lock()
dict_msgs = SortedDict()

def callback(data, args):
    ws_lock.acquire()
    if data.time not in dict_msgs:
        dict_msgs[data.time] = set()
    
    dict_msgs[data.time].add((args, data.value))
    conditional_publish()
    ws_lock.release()

attempts = 0
def conditional_publish():
    global attempts
    if len(dict_msgs.peekitem(0)[1]) == 4:
        snapshot = Snapshot()
        snapshot.time = dict_msgs.peekitem(0)[0]
        for i in range(4):
            e = dict_msgs.peekitem(0)[1].pop()
            if e[0] == 'hs1':
                snapshot.human_operator_speed = e[1]
            elif e[0] == 'hp1':
                human_pose = e[1]
            elif e[0] == 'rs':
                snapshot.robot_speed = e[1]
            else:
                robot_pose = e[1]
        pub.publish(snapshot)
        dict_msgs.popitem(0)
        attempts = 0
    elif attempts > 4:
        attempts = 0
        dict_msgs.popitem(0)
    else:
        attempts += 1

if __name__ == '__main__':
    global pub
    rospy.init_node('snapshot')

    pub = rospy.Publisher(name = '/snapshot', data_class = Snapshot, latch = True, queue_size = 1000)

    rospy.Subscriber('/monitor/human_operator_1/speed', TimedFloat, callback, ('hs1'))
    # rospy.Subscriber('/monitor/human_operator_2/speed', TimedFloat, callback, ('hs2'))
    # rospy.Subscriber('/monitor/human_operator_1/pose', TimedPose, callback, ('hp1'))
    # rospy.Subscriber('/monitor/human_operator_2/pose', TimedPose, callback, ('hp2'))
    # rospy.Subscriber('/monitor/robot/speed', TimedFloat, callback, ('rs'))
    # rospy.Subscriber('/monitor/robot/pose', TimedPose, callback, ('rp'))
    rospy.spin()
