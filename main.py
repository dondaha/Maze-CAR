from camera import Camera
from map import Maze
from controller import Controller
import time
import math


if __name__ == '__main__':
    # 初始化相机和控制器
    camera = Camera(0)
    camera.start()
    
    controller_25 = Controller("192.168.4.225", 12345, 25) # DDH的车
    controller_22 = Controller("192.168.4.200", 12345, 22) # LK的车
    controller_24 = Controller("192.168.4.224", 12345, 24) # LHZ的车
    controller_35 = Controller("192.168.4.235", 12345, 35) # JQH的车
    controllers = [controller_25, controller_22, controller_24, controller_35]
    for controller in controllers:
        controller.start()
    # 等待初始化
    time.sleep(2)
    while True:
        # 获取小车的位置
        cars = camera.get_cars()
        for car in cars:
            # 求出所有其他车的平均位置
            x = 0
            y = 0
            count = 0
            for other_car in cars:
                if other_car["id"] != car["id"]:
                    x += other_car["x"]
                    y += other_car["y"]
                    count += 1
            if count == 0:
                continue
            x /= count
            y /= count
            # 设置目标位置
            controller = None
            for c in controllers:
                if c.id == car["id"]:
                    controller = c
                    break
            if controller is not None:
                controller.set_target(x, y)
        time.sleep(0.05)
