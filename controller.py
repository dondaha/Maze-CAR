import socket
import threading


class Controller:
    def __init__(self, ip : str, port : int) -> None:
        exit_flag = False
        self.v1 = 0 # left front wheel
        self.v2 = 0 # left back wheel
        self.v3 = 0 # right front wheel
        self.v4 = 0 # right back wheel
    def set_speed(self, v1 : int, v2 : int, v3 : int, v4 : int) -> None:
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4
    def update(self) -> None:
        pass