import cv2
import json
import numpy as np
import cv2.aruco as aruco
from pathlib import Path
from map import Maze

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]

cam = 1
imagesize = (900, 600)

class Camera:
    def __init__(self) -> None:
        exit_flag = False
        pass
    def get_maze(self) -> Maze:
        pass
    def update(self) -> None:
        pass
