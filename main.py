from camera import Camera
from map import Maze
from controller import Controller
import time
import math


if __name__ == '__main__':
    # 初始化相机和控制器
    camera = Camera(0)
    camera.end = (6,1)
    camera.start()
    
    controller = Controller("192.168.4.1", 12345)
    controller.start()
    first_flag = False

    maze = None
    path = None

    while True:
        if not camera.maze_init:
            # 只有在初始化完毕后，小车才能开始运动（包含了起点终点初始化）
            time.sleep(0.5)
            continue
        with camera.car_lock:
            if len(camera.cars) != 0:
                car = camera.cars[0]
            else:
                continue
        if not first_flag:
            # 第一次运行时，获取迷宫并求解路径
            maze = camera.get_maze()
            path = maze.solve_path()
            first_flag = True
            print(path)
        target_x, target_y = tuple(i*100+50 for i in path.get_target()) # 将格点转化成像素坐标
        car_x, car_y = car["x"], car["y"]
        print(f"Car: ({car_x}, {car_y}), Target: ({target_x}, {target_y}), speed1: {controller.v1}, speed2: {controller.v2}, speed3: {controller.v3}, speed4: {controller.v4}")
        if math.sqrt((car_x - target_x)**2 + (car_y - target_y)**2) < 20: # 判断是否抵达格点的距离阈值
            target_x, target_y = tuple(i*100+50 for i in path.get_next_target())
        if path.arrived(): # 判断是否到达终点
            controller.stop()
            camera.stop()
            exit() # 结束程序
        controller.set_position(car["x"], car["y"], car["theta"]) # 控制器更新小车位置
        controller.set_target(target_x, target_y) # 控制器更新目标位置
        time.sleep(0.05)