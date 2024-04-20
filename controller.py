import socket
import threading
import time


class Controller:
    def __init__(self, ip : str, port : int) -> None:
        self.exit_flag = False
        self.ip = ip
        self.port = port
        # lock
        self.lock = threading.Lock()
        self.v1 = 0 # left front wheel
        self.v2 = 0 # left back wheel
        self.v3 = 0 # right front wheel
        self.v4 = 0 # right back wheel
    def set_speed(self, v1 : int, v2 : int, v3 : int, v4 : int) -> None:
        with self.lock:
            self.v1 = v1
            self.v2 = v2
            self.v3 = v3
            self.v4 = v4
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
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(cmd.encode(), (self.ip, self.port))
            time.sleep(0.02) # 50Hz update rate
        # stop the robot when the loop ends
        cmd = "<0,0,0,0>"
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(cmd.encode(), (self.ip, self.port))


if __name__ == '__main__':
    controller = Controller("192.168.4.1", 12345)
    controller.start()
    while True:
        # get the speed from the user with "v1,v1,v3,v4" format
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