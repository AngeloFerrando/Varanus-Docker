#!/usr/bin/env python 
import sys
import os
import rospy
import time
import numpy as np
from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud,PointCloud2,PointField
from nav_msgs.msg import OccupancyGrid
import geometry_msgs.msg
import tf
import tf2_ros
from radiation_layer.srv import RadPointCloudGenerator
import struct


class GenRadPC(object):

    def __init__(self):
        rospy.init_node('GenRadPC')
        s = rospy.Service('generate_radiation_point_cloud', RadPointCloudGenerator, self.run)
        self._radiation_map = None
        self._height_map = None

    def run(self,req):
        print "service called"
        height_sub =  rospy.Subscriber(req.height_map_topic, OccupancyGrid, self.height_callback)
        radiation_sub =  rospy.Subscriber(req.radiation_map_topic, OccupancyGrid, self.radiation_callback)

        z_scale = rospy.get_param(req.scale,1.0)
        z_offset = rospy.get_param(req.offset,0.0)


        while(self._radiation_map == None)|(self._radiation_map == None):
            time.sleep(1)

        if (self._radiation_map.info.width == self._height_map.info.width) & (self._radiation_map.info.height == self._height_map.info.height):
            points = []
            min_v = 0
            thresh = 100
            max_v = 255
            #max_v = max(self._radiation_map.data)
            for i in range(0,len(self._radiation_map.data)):
                col_idx = i%self._radiation_map.info.width
                row_idx = np.floor(i/self._radiation_map.info.width)
                x_pos = float(col_idx*self._radiation_map.info.resolution)
                y_pos = float(row_idx*self._radiation_map.info.resolution)
                z_pos = float(self._height_map.data[i]/z_scale) +z_offset
                rad = np.uint8(self._radiation_map.data[i])
                if (rad == 255):
                    pass
                else:
                    
                    #val = float(rad/(max_v-0.0)*510.0)-255.0
                   
                    if rad < thresh:
                        r =  float(float(rad/2.0)/thresh)*255
                        g =  float(float(thresh-(rad/2.0))/thresh)*255
                    else:
                        r = (float( float(rad-thresh)/ float(max_v-thresh))*122) +123
                        g = 255- ((float( float(rad-thresh)/ float(max_v-thresh))*122) +123)
                       
                    if r > 255:
                        r = 255
                    if r < 0:
                        r = 0
                    if g > 255:
                        g =255
                    if g < 0:
                        g = 0


                    a = 255
                    b = 0
                    rgb = struct.unpack('I', struct.pack('BBBB', b, g, r, a))[0]
                    points.append([x_pos, y_pos, z_pos, rgb])

            fields = [PointField('x', 0, PointField.FLOAT32, 1),
                        PointField('y', 4, PointField.FLOAT32, 1),
                        PointField('z', 8, PointField.FLOAT32, 1),
                        # PointField('rgb', 12, PointField.UINT32, 1),
                        PointField('rgba', 12, PointField.UINT32, 1),
                        ] 
            pc = point_cloud2.create_cloud(self._radiation_map.header, fields, points)
            #pc.header.frame_id = "rad_cloud"
            pc.header.frame_id = "rad_cloud"
            pc.header.stamp = rospy.Time.now()


            broadcaster = tf2_ros.StaticTransformBroadcaster()
            static_transformStamped = geometry_msgs.msg.TransformStamped()

            static_transformStamped.header.stamp = pc.header.stamp 
            static_transformStamped.header.frame_id = "map"
            static_transformStamped.child_frame_id = "rad_cloud"

            static_transformStamped.transform.translation.x = self._radiation_map.info.origin.position.x 
            static_transformStamped.transform.translation.y = self._radiation_map.info.origin.position.y 
            static_transformStamped.transform.translation.z = self._radiation_map.info.origin.position.z 
            static_transformStamped.transform.rotation.x = self._radiation_map.info.origin.orientation.x
            static_transformStamped.transform.rotation.y = self._radiation_map.info.origin.orientation.y
            static_transformStamped.transform.rotation.z = self._radiation_map.info.origin.orientation.z
            static_transformStamped.transform.rotation.w = 1.0

            broadcaster.sendTransform(static_transformStamped)      

            pub = rospy.Publisher(req.radiation_pointcloud_topic, PointCloud2, queue_size=2)
            pub.publish(pc)




        else:
            print("MISSMATCHED MAP SIZES")


    def height_callback(self,msg):
        self._height_map = msg

    def radiation_callback(self,msg):    
        self._radiation_map = msg   

if __name__ == "__main__":
    x = GenRadPC()
    rospy.spin()