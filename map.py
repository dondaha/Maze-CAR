from collections import deque
import numpy as np
import time


class Directions:
    """
    Class to represent directions in a maze.
    """
    NORTH = 'North'
    SOUTH = 'South'
    EAST = 'East'
    WEST = 'West'
    STOP = 'Stop'

    LEFT = {NORTH: WEST,
            SOUTH: EAST,
            EAST: NORTH,
            WEST: SOUTH,
            STOP: STOP}

    RIGHT = dict([(y, x) for x, y in LEFT.items()])

    REVERSE = {NORTH: SOUTH,
               SOUTH: NORTH,
               EAST: WEST,
               WEST: EAST,
               STOP: STOP}


class Path:
    """
    Class to represent a path in a maze.
    """
    def __init__(self, path: list, start_point: tuple, end_point: tuple):
        """
        Initialize a Path object.

        Args:
            path (list): List of moves representing the path.
        """
        self.path = path
        self.path_points = [start_point]
        for p in self.path:
            if p == Directions.NORTH:
                self.path_points.append((self.path_points[-1][0], self.path_points[-1][1] - 1))
            elif p == Directions.SOUTH:
                self.path_points.append((self.path_points[-1][0], self.path_points[-1][1] + 1))
            elif p == Directions.EAST:
                self.path_points.append((self.path_points[-1][0] + 1, self.path_points[-1][1]))
            elif p == Directions.WEST:
                self.path_points.append((self.path_points[-1][0] - 1, self.path_points[-1][1]))
            # 对于STOP，不添加新的点
        self.index = 0
    def get_target(self):
        """
        Get the target position in the path.

        Returns:
            tuple: The target position in the path.
        """
        if self.index < len(self.path_points):
            return self.path_points[self.index]
        else:
            return self.path_points[-1]
    def get_next_target(self):
        """
        Get the next target position in the path.

        Returns:
            tuple: The next target position in the path.
        """
        if self.index < len(self.path_points):
            point = self.path_points[self.index]
            self.index += 1
            return point
        else:
            return self.path_points[-1]

    def get_next_move(self):
        """
        Get the next move in the path.

        Returns:
            str: The next move in the path.
        """
        if self.index < len(self.path):
            move = self.path[self.index]
            self.index += 1
            return move
        else:
            return Directions.STOP

    def has_next_move(self):
        """
        Check if there is a next move in the path.

        Returns:
            bool: True if there is a next move, False otherwise.
        """
        return self.index < len(self.path)
    
    def arrived(self):
        return self.index == len(self.path_points)

    def __str__(self) -> str:
        """
        Convert the path to a string representation.

        Returns:
            str: The string representation of the path.
        """
        result = ''
        for move in self.path:
            if move == Directions.NORTH:
                result += '↑'
            elif move == Directions.SOUTH:
                result += '↓'
            elif move == Directions.EAST:
                result += '→'
            elif move == Directions.WEST:
                result += '←'
            else:
                result += '<STOP>'
        return result


def example_path():
    """
    Returns a sequence of moves that solves tinyMaze. For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.

    Returns:
        list: List of moves representing the example path.
    """
    s = Directions.SOUTH
    e = Directions.EAST

    return [e, e, s, s, s, e, e, e, e, e, e]


class Maze:
    """
    Class to represent a maze.
    """
    def __init__(self, width: int, height: int):
        """
        Initialize a Maze object.

        Args:
            width (int): Width of the maze.
            height (int): Height of the maze.
        """
        self.width = width
        self.height = height
        self.maze = [[0 for x in range(width)] for y in range(height)]
        self.start = (0, 0)
        self.end = (9 - 1, 4 - 1)
    def set_start_end(self, start: tuple, end: tuple):
        """
        Set the start and end positions of the maze.

        Args:
            start (tuple): Start position of the maze. (x, y)
            end (tuple): End position of the maze. (x, y)
        """
        self.start = start
        self.end = end
    def set_point(self, x: int, y: int, value: int):
        """
        Set the value of a point in the maze.

        Args:
            x (int): X-coordinate of the point.
            y (int): Y-coordinate of the point.
            value (int): Value to set at the point.
        """
        self.maze[y][x] = value

    def set_point_from_text(self, text: str):
        """
        Set the values of points in the maze from a text representation.

        Args:
            text (str): Text representation of the maze.
        """
        lines = text.split('\n')
        for y, line in enumerate(lines):
            for x, point in enumerate(line):
                self.maze[y][x] = 1 if point == '#' else 0

    def set_point_from_np_array(self, array):
        """
        Set the values of points in the maze from a numpy array.

        Args:
            array (np.array): Numpy array representation of the maze.
            [[0 0 0 1 0 0 0 0 0]
            [0 1 0 1 0 1 0 1 0]
            [0 1 0 1 0 1 1 1 0]
            [0 1 0 0 0 0 0 0 0]
            [0 1 0 1 1 0 1 1 0]
            [0 0 0 0 1 0 0 0 0]]
        """
        self.maze = array.tolist()
        self.width = len(array[0])
        self.height = len(array)

    def get_point(self, x: int, y: int):
        """
        Get the value of a point in the maze.

        Args:
            x (int): X-coordinate of the point.
            y (int): Y-coordinate of the point.

        Returns:
            int: The value of the point.
        """
        return self.maze[y][x]

    def solve_path(self):
        """
        Solve the maze and return the path.

        Returns:
            Path: The path object representing the solution path.
        """
        start = self.start
        end = self.end
        path = self.bfs(start, end)
        return Path(path, start, end)


    def bfs(self, start, end):
        """
        Breadth-first search algorithm to find a path in the maze.

        Args:
            start: Starting position in the maze.
            end: End position in the maze.

        Returns:
            list: List of moves representing the path.
        """
        visited = set()  # Set to keep track of visited nodes
        queue = deque([(start, [])])  # Queue to keep track of paths

        while queue:
            current, path = queue.popleft()

            if current == end:
                return path + [Directions.STOP]

            if current not in visited:
                visited.add(current)

                for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
                    next_position = self.get_next_position(current, direction)

                    if self.is_valid_move(next_position) and next_position not in visited:
                        new_path = list(path)
                        new_path.append(direction)
                        queue.append((next_position, new_path))

        return []  # If no path is found

    def get_next_position(self, current, direction):
        """
        Get the next position in the maze given the current position and direction.

        Args:
            current: Current position in the maze.
            direction: Direction to move in.

        Returns:
            tuple: The next position in the maze.
        """
        x, y = current
        if direction == Directions.NORTH:
            return (x, y - 1)
        elif direction == Directions.SOUTH:
            return (x, y + 1)
        elif direction == Directions.EAST:
            return (x + 1, y)
        elif direction == Directions.WEST:
            return (x - 1, y)

    def is_valid_move(self, position):
        """
        Check if a move to the given position is valid.

        Args:
            position: Position to move to.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        x, y = position
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.get_point(x, y) == 0

    def __str__(self) -> str:
        """
        Convert the maze to a string representation.

        Returns:
            str: The string representation of the maze.
        """
        result = ''
        for row in self.maze:
            for point in row:
                result += "#" if point == 1 else " "
            result += '\n'
        return result


if __name__ == '__main__':
    maze = Maze(9, 6)
    map = ""
    map += "    #    \n"
    map += " ## ## # \n"
    map += "       # \n"
    map += " ### # # \n"
    map += " # # # # \n"
    map += "     #   "
    maze.set_start_end((1, 1), (5, 0))
    maze.set_point_from_text(map)
    start_time = time.time()
    solution = maze.solve_path()
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.6f} seconds")
    print(maze)
    print(solution)