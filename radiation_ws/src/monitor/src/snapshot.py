#!/usr/bin/env python
import roslib
import rospy
from sortedcontainers import SortedDict
from threading import *
from nist_gear.msg import *
import numpy as np
from gazebo_msgs.msg import *
from std_msgs.msg import *
from geometry_msgs.msg import *

ws_lock = Lock()
dict_msgs_1 = SortedDict()
dict_msgs_2 = SortedDict()

def callback(data, args):
    ws_lock.acquire()
    if data.time not in dict_msgs_1:
        dict_msgs_1[data.time] = set()
    if data.time not in dict_msgs_2:
        dict_msgs_2[data.time] = set()
    if args in ['hs1','hp1','rs','rp']:
        dict_msgs_1[data.time].add((args, data.value))
        conditional_publish1()
    if args in ['hs2','hp2','rs','rp']:
        dict_msgs_2[data.time].add((args, data.value))
        conditional_publish2()
    ws_lock.release()

attempts1 = 0
def conditional_publish1():
    global attempts1
    if len(dict_msgs_1.peekitem(0)[1]) == 4:
        snapshot = Snapshot()
        snapshot.time = dict_msgs_1.peekitem(0)[0]
        for i in range(4):
            e = dict_msgs_1.peekitem(0)[1].pop()
            if e[0] == 'hs1':
                snapshot.human_operator_speed = e[1]
            elif e[0] == 'hp1':
                human_pose = e[1]
            elif e[0] == 'rs':
                snapshot.robot_speed = e[1]
            else:
                robot_pose = e[1]
        p1 = np.array([human_pose.position.x, human_pose.position.y, human_pose.position.z])
        p2 = np.array([robot_pose.position.x, robot_pose.position.y, robot_pose.position.z])
        squared_dist = np.sum((p1-p2)**2, axis=0)
        snapshot.distance_robot_human_operator = np.sqrt(squared_dist)
        print(snapshot)
        pub1.publish(snapshot)
        dict_msgs_1.popitem(0)
        attempts1 = 0
    elif attempts1 > 4:
        attempts1 = 0
        dict_msgs_1.popitem(0)
    else:
        attempts1 += 1

attempts2 = 0
def conditional_publish2():
    global attempts2
    if len(dict_msgs_2.peekitem(0)[1]) == 4:
        snapshot = Snapshot()
        snapshot.time = dict_msgs_2.peekitem(0)[0]
        for i in range(4):
            e = dict_msgs_2.peekitem(0)[1].pop()
            if e[0] == 'hs2':
                snapshot.human_operator_speed = e[1]
            elif e[0] == 'hp2':
                human_pose = e[1]
            elif e[0] == 'rs':
                snapshot.robot_speed = e[1]
            else:
                robot_pose = e[1]
        p1 = np.array([human_pose.position.x, human_pose.position.y, human_pose.position.z])
        p2 = np.array([robot_pose.position.x, robot_pose.position.y, robot_pose.position.z])
        squared_dist = np.sum((p1-p2)**2, axis=0)
        snapshot.distance_robot_human_operator = np.sqrt(squared_dist)
        print(snapshot)
        pub2.publish(snapshot)
        dict_msgs_2.popitem(0)
        attempts2 = 0
    elif attempts2 > 4:
        attempts2 = 0
        dict_msgs_2.popitem(0)
    else:
        attempts2 += 1

if __name__ == '__main__':
    global pub1, pub2
    rospy.init_node('snapshot')

    pub1 = rospy.Publisher(name = '/snapshot_1', data_class = Snapshot, latch = True, queue_size = 1000)
    pub2 = rospy.Publisher(name = '/snapshot', data_class = Snapshot, latch = True, queue_size = 1000)

    rospy.Subscriber('/monitor/human_operator_1/speed', TimedFloat, callback, ('hs1'))
    rospy.Subscriber('/monitor/human_operator_2/speed', TimedFloat, callback, ('hs2'))
    rospy.Subscriber('/monitor/human_operator_1/pose', TimedPose, callback, ('hp1'))
    rospy.Subscriber('/monitor/human_operator_2/pose', TimedPose, callback, ('hp2'))
    rospy.Subscriber('/monitor/robot/speed', TimedFloat, callback, ('rs'))
    rospy.Subscriber('/monitor/robot/pose', TimedPose, callback, ('rp'))
    rospy.spin()
