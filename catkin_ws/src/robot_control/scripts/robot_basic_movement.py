# -*- coding: utf-8 -*-
# @Time    : 2025/1/19 10:45
# @Author  : HeLong
# @FileName: robot_basic_movement.py
# @Software: PyCharm
# @Blog    ：https://blog.duolaa.asia/

import rospy
from gpiozero import Robot, Motor
from time import sleep
import math

# 初始化ROS节点
rospy.init_node('robot_basic_movement', anonymous=True)

# 创建机器人对象
robot = Robot(left=Motor(forward=22, backward=27, enable=18), right=Motor(forward=25, backward=24, enable=23))

class BasicRobotMovement:
    def __init__(self, speed=0.3, turn_speed=0.3, wheelbase=0.12, track_width=0.11):
        """
        初始化函数
        :param speed: 前进后退速度，默认0.5
        :param turn_speed: 转弯速度，默认0.3
        :param wheelbase: 前后轮距离，默认0.12米
        :param track_width: 左前到右前的距离，默认0.11米
        """
        self.speed = speed
        self.turn_speed = turn_speed
        self.wheelbase = wheelbase
        self.track_width = track_width

    def move_forward(self, duration):
        """
        前进
        :param duration: 持续时间（秒）
        """
        robot.forward(self.speed)
        sleep(duration)
        robot.stop()

    def move_backward(self, duration):
        """
        后退
        :param duration: 持续时间（秒）
        """
        robot.backward(self.speed)
        sleep(duration)
        robot.stop()

    def turn_left(self, angle):
        anglea = 2*angle
        """
        左转
        :param angle: 转角（度）
        """
        radians = math.radians(anglea)  # 将角度转换为弧度
        # 左轮逆时针，右轮顺时针
        robot.left_motor.value = self.turn_speed
        robot.right_motor.value = -self.turn_speed
        # 计算转弯所需时间
        duration = (radians * (self.track_width)) / self.turn_speed
        sleep(duration)
        robot.stop()

    def turn_right(self, angle):
        anglea = 2*angle
        """
        右转
        :param angle: 转角（度）
        """
        radians = math.radians(anglea)  # 将角度转换为弧度
        # 右轮逆时针，左轮顺时针
        robot.right_motor.value = self.turn_speed
        robot.left_motor.value = -self.turn_speed
        # 计算转弯所需时间
        duration = (radians * (self.track_width)) / self.turn_speed
        sleep(duration)
        robot.stop()

# 示例用法
if __name__ == '__main__':
    try:
        robot_movement = BasicRobotMovement()
        robot_movement.move_forward(2)  # 前进2秒
        robot_movement.turn_left(90)    # 左转90度
        robot_movement.move_backward(2) # 后退2秒
        robot_movement.turn_right(45)   # 右转45度
    except rospy.ROSInterruptException:
        pass