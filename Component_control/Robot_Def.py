# -*- coding: utf-8 -*-
# @Time    : 2025/1/17 19:01
# @Author  : HeLong
# @FileName: Robot_Def.py
# @Software: PyCharm
# @Blog    ：https://blog.duolaa.asia/

from gpiozero import Robot, Motor
from gpiozero import LED
from time import sleep

def robot():
    robot = Robot(left=Motor(forward=22, backward=27, enable=18), right=Motor(forward=25, backward=24, enable=23))
    return robot
