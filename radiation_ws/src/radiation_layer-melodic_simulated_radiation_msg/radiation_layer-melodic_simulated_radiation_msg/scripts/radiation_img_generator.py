#!/usr/bin/env python 
import sys
import os
import cv2
import rospy
import time
import numpy as np
from sensor_msgs import point_cloud2
from nav_msgs.msg import OccupancyGrid
import tf
import tf2_ros
from radiation_layer.srv import RadImageGenerator
import struct
import matplotlib.pyplot as plt
import pathlib


class GenRadPC(object):

    def __init__(self):
        rospy.init_node('GenRadImg')
        s = rospy.Service('generate_radiation_image', RadImageGenerator, self.run)
        self._radiation_map = None
        self._map = None

    def run(self,req):
        img_sub =  rospy.Subscriber(req.map_topic, OccupancyGrid, self.map_callback)
        radiation_sub =  rospy.Subscriber(req.radiation_map_topic, OccupancyGrid, self.radiation_callback)

        #z_scale = rospy.get_param(req.scale,1.0)
        #z_offset = rospy.get_param(req.offset,0.0)


        while(self._radiation_map == None)|(self._map == None):
            print "waiting"
            time.sleep(1)


        min_v = min(self._radiation_map.data)
        max_v = max(self._radiation_map.data)

        
        img = np.asarray(np.reshape(self._map.data,(self._map.info.height,self._map.info.width)),dtype=np.uint8)
        recoloured_img = np.zeros((img.shape[1],img.shape[0],1),dtype=np.uint8)
        for i in range(0,len(img)):
            for j in range(0,len(img[i])):
                if img[i][j] == 0:
                    colour = 205
                elif img[i][j] == 255:
                    colour = 255
                elif img[i][j] == 100:
                    colour = 0
                recoloured_img[i,j] = colour
        recoloured_img = cv2.cvtColor(recoloured_img,cv2.COLOR_GRAY2RGB)


    
        rad_img = np.asarray(np.reshape(self._radiation_map.data,(self._radiation_map.info.height,self._radiation_map.info.width)),dtype=np.uint8)
        ret,mask1 = cv2.threshold(rad_img,1,255,cv2.THRESH_BINARY)
        ret,mask2 = cv2.threshold(rad_img,254,255,cv2.THRESH_BINARY_INV)
        scaled_rad_img = ((rad_img*255.0)/max_v)
        coloured_rad_img = cv2.applyColorMap(np.asarray(scaled_rad_img,dtype = np.uint8), cv2.COLORMAP_JET)
        inter = cv2.bitwise_or(coloured_rad_img, coloured_rad_img, mask = mask1)
        output = cv2.bitwise_or(inter, inter, mask = mask2)
        
        output_img = np.zeros((img.shape[1],img.shape[0],3),dtype=np.uint8)

        alpha = 0.7

        for i in range(0,len(output_img)):
            for j in range(0,len(output_img[i])):
                real_i = (i* self._map.info.resolution) + self._map.info.origin.position.x
                real_j = (j* self._map.info.resolution) + self._map.info.origin.position.y
                rad_i = int((real_i - self._radiation_map.info.origin.position.x)/self._radiation_map.info.resolution)
                rad_j = int((real_j - self._radiation_map.info.origin.position.y)/self._radiation_map.info.resolution)
                if (output[rad_i,rad_j,0] == 0) & (output[rad_i,rad_j,1] == 0)&(output[rad_i,rad_j,2] == 0):
                    output_img[i][j] = recoloured_img[i][j]
                else:
                    output_img[i][j] =  (recoloured_img[i][j]*alpha) + (output[rad_i,rad_j]*(1.0-alpha))
                
        """

        cv2.imshow('recoloured_img',recoloured_img)
        cv2.imshow('img',img)
        cv2.imshow('output',output)
        cv2.imshow('inter',inter)
        cv2.imshow('rad_img',rad_img)
        cv2.imshow('coloured_rad_img',coloured_rad_img)
        cv2.imshow('mask1',mask1)
        cv2.imshow('mask2',mask2)

        cv2.imshow('output_img',output_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        """

        minx = self._map.info.origin.position.x
        miny = self._map.info.origin.position.y
        maxx = self._map.info.origin.position.x +(self._map.info.width * self._map.info.resolution)
        maxy = self._map.info.origin.position.y +(self._map.info.height * self._map.info.resolution)
        print minx,maxx,miny,maxy
        
        plt.imshow(cv2.cvtColor(output_img, cv2.COLOR_BGR2RGB),interpolation='none', extent=[minx,maxx,miny,maxy])
        cbar = plt.colorbar()
        plt.clim(1,max_v)

        plt.savefig(req.radiation_img_relative_save_locations,dpi=300)

                
                
        """
                
                if rad < thresh:
                    r = 0
                    g =  float(float(thresh-rad)/thresh)*255
                else:
                    r = float( float(rad-thresh)/ float(max_v-thresh))*255
                    if r > 255:
                        r = 255
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
        pc.header.frame_id = "rad_cloud"
        pc.header.stamp = rospy.Time.now()
        """


    def map_callback(self,msg):
        self._map = msg

    def radiation_callback(self,msg):    
        self._radiation_map = msg   

if __name__ == "__main__":
    x = GenRadPC()
    rospy.spin()