from camera import Camera
from map import Maze
from controller import Controller
import time
import math
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # 初始化相机和控制器
    camera = Camera(0)
    camera.start()
    
    controller_25 = Controller("192.168.137.124", 12345, 25) # DDH的车
    # controller_22 = Controller("192.168.137.135", 12345, 22) # LK的车
    controller_24 = Controller("192.168.137.227", 12345, 24) # LHZ的车
    controller_35 = Controller("192.168.137.56", 12345, 35) # JQH的车
    controllers = [controller_25, controller_24, controller_35]
    for controller in controllers:
        controller.start()
    # 等待初始化
    time.sleep(2)
    
    #创建一个以controller_id为邻居的无向切换拓扑图
    #25->24/35
    controller_25.add_neighbor(controller_24)
    controller_25.add_neighbor(controller_35)
    #24->35/25
    controller_24.add_neighbor(controller_35)
    controller_24.add_neighbor(controller_25)
    #35->25/24
    controller_35.add_neighbor(controller_25)
    controller_35.add_neighbor(controller_24)

    # 创建一个新的图形和子图
    fig, ax = plt.subplots()
    
    #创建计时参数
    start_time = time.time()
    
    neighbor_num = 0
    
    # 开始循环
    while True:
        # 获取小车的位置
        cars = camera.get_cars()

        # 清除子图
        ax.clear()
        
        #获得当前时间
        current_time = time.time()
        #计算时间差
        time_diff = current_time - start_time
        #如果时间差大于2.5s，重新规划路径
        if time_diff > 2.5:
            neighbor_num = (neighbor_num + 1) % 2   

        for car in cars:
            controller = None
            for c in controllers:
                if c.id == car["id"]:
                    controller = c
                    break
            if controller is not None:
                # 寻找目标位置
                car_x = car["x"]
                car_y = car["y"]
                x = 0
                y = 0
                nerghbors = controller.get_neighbors()
                for other_car in cars:
                    if other_car["id"] == nerghbors[neighbor_num].id:
                        x = other_car["x"] - car_x
                        y = other_car["y"] - car_y
                # 设置目标位置
                target_x = car_x + x
                target_y = car_y + y
                controller.set_position(car_x, car_y, car["theta"])
                controller.set_target(target_x, target_y)
                # 绘制小车的位置和目标方向
                ax.plot(car_x, car_y, 'bo')  # 小车的位置
                ax.plot([car_x, target_x], [car_y, target_y], 'r-')  # 小车的目标方向

        # 更新图形
        plt.pause(0.05)