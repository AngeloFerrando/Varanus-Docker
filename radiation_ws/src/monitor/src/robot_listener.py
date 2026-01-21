#!/usr/bin/env python
# Copyright 2017 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import geometry_msgs.msg
import rospy
import tf2_ros
import math
import tf2_geometry_msgs  # import support for transforming geometry_msgs stamped msgs
import numpy as np
from std_msgs.msg import *
from nist_gear.msg import *

transOld = None
frame = 'torso_base'

def callbackClock(data):
    global transOld
    # Ensure that the transform is available.
    try:
        transTime = rospy.Time()
        trans = tfBuffer.lookup_transform('world', frame, transTime, rospy.Duration(0.0))
    except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as e:
        print(e)
        return

    # Transform the pose from the specified frame to the world frame.
    local_pose = geometry_msgs.msg.PoseStamped()
    local_pose.header.frame_id = frame
    local_pose.pose.position.x = 0.15
    local_pose.pose.position.y = 0.15

    if transOld is not None:
        delta_time = (trans.header.stamp - transOld.header.stamp).to_sec()
        if delta_time != 0:
            p1 = np.array([transOld.transform.translation.x, transOld.transform.translation.y, transOld.transform.translation.z])
            p2 = np.array([trans.transform.translation.x, trans.transform.translation.y, trans.transform.translation.z])
            squared_dist = np.sum((p1-p2)**2, axis=0)
            dist = np.sqrt(squared_dist) # [m]
            print(str(dist / delta_time) + ' [m/s]') # [m/s]
            p = geometry_msgs.msg.Pose()
            p.position.x = trans.transform.translation.x
            p.position.y = trans.transform.translation.y
            p.position.z = trans.transform.translation.z
            tp = TimedPose()
            tp.time = data.data
            tp.value = p
            pub_position.publish(tp)
            ts = TimedFloat()
            ts.time = data.data
            ts.value = (dist / delta_time)
            pub_speed.publish(ts)
    transOld = trans
    transOldTime = transTime

if __name__ == '__main__':
    global pub_speed, pub_position, tfBuffer, listener
    rospy.init_node('tf2_example')

    pub_speed = rospy.Publisher(name = '/monitor/robot/speed', data_class = TimedFloat, latch = True, queue_size = 1000)
    pub_position = rospy.Publisher(name = '/monitor/robot/pose', data_class = TimedPose, latch = True, queue_size = 1000)
    rospy.Subscriber('stream_clock', Int64, callbackClock)

    tfBuffer = tf2_ros.Buffer()
    listener = tf2_ros.TransformListener(tfBuffer)
    rospy.spin()
