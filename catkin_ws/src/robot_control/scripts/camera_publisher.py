#!/usr/bin/env python3
# coding: utf-8
# @Time    : 2025/1/26 21:04
# @Author  : HeLong
# @FileName: camera_publisher.py
# @Software: PyCharm
# @Blog    : https://helong.online/

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

# 初始化ROS节点
rospy.init_node('camera_publisher', anonymous=True)

# 创建Publisher
pub = rospy.Publisher('/camera/image_raw', Image, queue_size=10)

# 初始化摄像头
cap = cv2.VideoCapture(0)

# 创建CvBridge对象
bridge = CvBridge()

def publish_image():
    while not rospy.is_shutdown():
        ret, frame = cap.read()
        if ret:
            # 将OpenCV图像转换为ROS消息
            try:
                msg = bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            except Exception as e:
                rospy.logerr("CV Bridge Error: {0}".format(e))
                continue
            # 发布图像消息
            pub.publish(msg)
        else:
            rospy.logerr("Failed to capture image")
            break

if __name__ == '__main__':
    publish_image()