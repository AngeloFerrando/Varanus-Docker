#!/usr/bin/env python
import roslib
import rospy
import math
from gazebo_msgs.msg import *
from std_msgs.msg import *
from geometry_msgs.msg import *
import numpy as np
from nist_gear.msg import *
from threading import *

ws_lock = Lock()

last_pose = [None, None]
last_time = [None, None]
current_speed = [0.0, 0.0]
current_pose = [Pose(), Pose()]

def callback(data):
    global last_pose, last_time, current_pose, current_speed
    now = rospy.get_rostime()
    j = 0
    speed = [0, 0]
    for i in [data.name.index('person_1_ariac'), data.name.index('person_2_ariac')]:
        if last_pose[j] and last_time[j]:
            diff_time = (now - last_time[j]).to_sec() # [s]
            if diff_time > 0.1:
                p1 = np.array([last_pose[j].position.x, last_pose[j].position.y, last_pose[j].position.z])
                p2 = np.array([data.pose[i].position.x, data.pose[i].position.y, data.pose[i].position.z])
                squared_dist = np.sum((p1-p2)**2, axis=0)
                dist = np.sqrt(squared_dist) # [m]
                speed[j] = dist / diff_time # [m/s]

                ws_lock.acquire()
                current_pose[j] = data.pose[i]
                current_speed[j] = speed[j]
                ws_lock.release()

                last_time[j] = now
                last_pose[j] = data.pose[i]
        else:
            last_pose[j] = data.pose[i]
            last_time[j] = now
        j += 1

def callbackClock(data):
    ws_lock.acquire()
    print(data)
    for i in [0,1]:
        tp = TimedPose()
        tp.time = data.data
        tp.value = current_pose[i]
        ts = TimedFloat()
        ts.time = data.data
        ts.value = current_speed[i]
        print(ts)
        pub_position[i].publish(tp)
        pub_speed[i].publish(ts)
    ws_lock.release()

if __name__ == '__main__':
    global pub_speed, pub_position
    rospy.init_node('modelstate_listener')
    pub_speed = []
    pub_speed.append(rospy.Publisher(name = '/monitor/human_operator_1/speed', data_class = TimedFloat, latch = True, queue_size = 1000))
    pub_speed.append(rospy.Publisher(name = '/monitor/human_operator_2/speed', data_class = TimedFloat, latch = True, queue_size = 1000))
    pub_position = []
    pub_position.append(rospy.Publisher(name = '/monitor/human_operator_1/pose', data_class = TimedPose, latch = True, queue_size = 1000))
    pub_position.append(rospy.Publisher(name = '/monitor/human_operator_2/pose', data_class = TimedPose, latch = True, queue_size = 1000))
    rospy.Subscriber('/gazebo/model_states', gazebo_msgs.msg.ModelStates, callback)
    rospy.Subscriber('stream_clock', Int64, callbackClock)
    rospy.spin()
