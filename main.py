from camera import Camera
from map import Maze
from controller import Controller
import time
import math


if __name__ == '__main__':
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
            maze = camera.get_maze()
            path = maze.solve_path()
            first_flag = True
            print(path)
        target_x, target_y = tuple(i*100+50 for i in path.get_target())
        car_x, car_y = car["x"], car["y"]
        print(f"Car: ({car_x}, {car_y}), Target: ({target_x}, {target_y}), speed1: {controller.v1}, speed2: {controller.v2}, speed3: {controller.v3}, speed4: {controller.v4}")
        if math.sqrt((car_x - target_x)**2 + (car_y - target_y)**2) < 10:
            target_x, target_y = tuple(i*100+50 for i in path.get_next_target())
        if path.arrived():
            controller.stop()
            camera.stop()
            exit()
        controller.set_position(car["x"], car["y"], car["theta"])
        controller.set_target(target_x, target_y)
        time.sleep(0.05)