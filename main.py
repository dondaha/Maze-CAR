from camera import Camera
from map import Maze
from controller import Controller
import time
import math


if __name__ == '__main__':
    # 初始化相机和控制器
    camera = Camera(0)
    camera.start()
    
    controller1 = Controller("192.168.4.225", 12345) # DDH的车
    controller2 = Controller("192.168.4.200", 12345) # LK的车
    controller3 = Controller("192.168.4.224", 12345) # LHZ的车
    controller4 = Controller("192.168.4.235", 12345) # JQH的车
    controller1.start()
    controller2.start()
    controller3.start()
    controller4.start()

