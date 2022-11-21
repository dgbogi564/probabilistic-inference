from datetime import datetime
import pygame
from pygame.locals import *
import random
import sys
import numpy

BLACK = (0, 0, 0)           # BORDERS
GRAY = (100, 100, 100)      # BLOCKED
GOLD = (255, 215, 0)        # HIGHWAY
GREEN = (0, 100, 0)         # ROUGH TERRAIN
WHITE = (255, 255, 255)     # NORMAL

class Grid:

    normal, highway, rough_terrain, blocked = 'N', 'H', 'R', 'B'
    up, down, left, right = 'U', 'D', 'L', 'R'

    def __init__(self, filepath, width, height, cell_size):
        self.window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.cell_size = cell_size
        self.circle_radius = 10
        self.border_size = 2
        self.line_width = 5

        with open(filepath, "r") as path:


    @classmethod
    def generate_ground_truth_paths(cls, grid_map):
        # TODO we don't know much about map format besides that it is 100 by 50
        # function was created on the assumption that we create our own map

        rows = 100
        columns = 50
        grid = [[''] * columns] * rows

        # In case grid does not contain an unblocked cell
        row = -1
        column = -1
        while row is not -1:

            # populate grid
            for r in range(rows):
                for c in range(columns):
                    num = random.uniform(0, 1)

                    if 0 <= num <= 0.5:
                        grid[r][c] = Grid.normal
                    elif 0.5 < num <= 0.7:
                        grid[r][c] = Grid.highway
                    elif 0.7 < num <= 0.9:
                        grid[r][c] = Grid.rough_terrain
                    else:
                        grid[r][c] = Grid.blocked

            # get first unblocked cell
            for r in range(rows):
                for c in range(columns):
                    if grid[row][column] != Grid.blocked:
                        row = r
                        column = c
                        break

        starting_coordinates = f'{row} {column}'

        # generate sequence and sensor readings
        actions = []
        ground_truth_states = []
        sensor_readings = []
        for x in range(100):

            # generate actions and ground truth states
            action = random.choice([Grid.up, Grid.down, Grid.left, Grid.right])
            actions.append(action)
            num = random.uniform(0, 1)
            if 0 <= num < 0.9:
                match action:
                    case Grid.up:
                        if row > 0 and grid[row-1][column] is not Grid.blocked:
                            row = row-1
                    case Grid.down:
                        if row < rows-1 and grid[row+1][column] is not Grid.blocked:
                            row = row+1
                    case Grid.left:
                        if column > 0 and grid[row][column-1] is not Grid.blocked:
                            column = column-1
                    case Grid.right:
                        if column < column-1 and grid[row][column+1] is not Grid.blocked:
                            column = column+1
            ground_truth_states.append(f'{row} {column}')

            # generate sensor readings
            num = random.uniform(0, 1)
            if 0 <= num < 0.9:
                sensor_reading = grid[row][column]
            else:
                sensor_reading = random.choice(
                    [x for x in [Grid.normal, Grid.highway, Grid.rough_terrain] if x != grid[row][column]])
            sensor_readings.append(sensor_reading)

        # write everything to a file
        with open(datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") + ".txt", "w") as file:

            # write coordinates of initial point
            file.write(starting_coordinates + '\n')

            # write ground truth states
            for x in range(100):
                file.write(ground_truth_states[x])
                file.write('\n')

            # write actions
            for x in range(100):
                file.write(actions[x])
            file.write('\n')

            # write sensor readings
            for x in range(100):
                file.write(sensor_readings[x])
            file.write('\n')
