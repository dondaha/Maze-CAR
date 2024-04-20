from camera import Camera
from map import Maze
from controller import Controller

if __name__ == '__main__':
    camera = Camera()
    maze = camera.get_maze()
    controller = Controller()