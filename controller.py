import socket
import threading
import math
import time


class Controller:
    def __init__(self, ip : str, port : int, id : int) -> None:
        self.exit_flag = False
        self.ip = ip
        self.port = port
        self.id = id
        # lock
        self.lock = threading.Lock()
        self.v1 = 0 # 左前
        self.v2 = 0 # 右前
        self.v3 = 0 # 左后
        self.v4 = 0 # 右后
        self.x = 0
        self.y = 0
        self.theta = 0
        self.target_x = 0
        self.target_y = 0
        self.speed = 70 # 小车的速度
    def set_position(self, x : int, y : int, theta : float) -> None:
        with self.lock:
            self.x = x
            self.y = y
            self.theta = theta
    def set_speed(self, v1 : int, v2 : int, v3 : int, v4 : int) -> None:
        with self.lock:
            self.v1 = v1
            self.v2 = v2
            self.v3 = v3
            self.v4 = v4
    def set_target(self, x : int, y : int) -> None:
        with self.lock:
            self.target_x = x
            self.target_y = y
            alpha = math.atan2(y - self.y, x - self.x)
        beta = self.theta - alpha

        cosValue = math.cos(beta)
        sinValue = math.sin(beta)
        speed1 = self.speed * cosValue - self.speed * sinValue; # 左前
        speed2 = self.speed * cosValue + self.speed * sinValue; # 右前
        speed3 = self.speed * cosValue + self.speed * sinValue; # 左后
        speed4 = self.speed * cosValue - self.speed * sinValue; # 右后
        # 距离小于150速度置零
        if math.sqrt((x - self.x) * (x - self.x) + (y - self.y) * (y - self.y)) < 150:
            speed1 = 0
            speed2 = 0
            speed3 = 0
            speed4 = 0
        self.set_speed(int(speed1), int(speed2), int(speed3), int(speed4))
    def stop(self) -> None:
        self.set_speed(0, 0, 0, 0)
        self.exit_flag = True
    def start(self) -> None:
        with self.lock:
            if self.exit_flag:
                return
            self.exit_flag = False
        # start the update thread
        t = threading.Thread(target=self.update)
        t.start()
        
    def update(self) -> None:
        while True:
            with self.lock:
                if self.exit_flag:
                    break
                v1 = self.v1
                v2 = self.v2
                v3 = self.v3
                v4 = self.v4
            # send the speed to the robot
            cmd = f"<{v1},{v2},{v3},{v4}>"
            # cmd = f"<{-v1},{-v2},{-v3},{-v4}>"
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(cmd.encode(), (self.ip, self.port))
            time.sleep(0.02) # 50Hz update rate
        # stop the robot when the loop ends
        cmd = "<0,0,0,0>"
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(cmd.encode(), (self.ip, self.port))


if __name__ == '__main__':
    controller = Controller("192.168.1.225", 12345, 25)
    controller.start()
    while True:
        # get the speed from the user with "v1,v2,v3,v4" format
        try:
            v1, v2, v3, v4 = map(int, input().split(","))
            controller.set_speed(v1, v2, v3, v4)
        except KeyboardInterrupt:
            # If it's a keyboard interrupt, safely exit the controller
            controller.stop()
            print("Safely exited")
            break
        except Exception as e:
            print("Error:", e)
            continue