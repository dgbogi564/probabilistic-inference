from datetime import datetime
import itertools
import pygame
from pygame.locals import *
import random
import sys
import numpy

BLACK = (0, 0, 0)  # BORDERS
GRAY = (100, 100, 100)  # BLOCKED
GOLD = (255, 215, 0)  # HIGHWAY
GREEN = (0, 100, 0)  # ROUGH TERRAIN
WHITE = (255, 255, 255)  # NORMAL


class Grid:
    normal, highway, rough_terrain, blocked = 'N', 'H', 'R', 'B'
    up, down, left, right = 'U', 'D', 'L', 'R'

    def __init__(self, filepath, width, height, cell_size):
        self.window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.cell_size = cell_size
        self.circle_radius = 10
        self.border_size = 2
        self.line_width = 5
        self.grid = self.import_grid(filepath)

    def draw_grid(self):



    @classmethod
    def import_grid(cls, filepath):
        # TODO
        grid = None
        return grid

    @classmethod
    def generate_grid(cls, rows, columns):
        grid = [[''] * columns] * rows
        for row in range(rows):
            for column in range(columns):
                num = random.uniform(0, 1)
                if 0 <= num <= 0.5:
                    grid[row][column] = Grid.normal
                elif 0.5 < num <= 0.7:
                    grid[row][column] = Grid.highway
                elif 0.7 < num <= 0.9:
                    grid[row][column] = Grid.rough_terrain
                else:
                    grid[row][column] = Grid.blocked
        return grid

    @classmethod
    def generate_ground_truth_paths(cls, grid):
        # TODO we don't know much about map format besides that it is 100 by 50?
        row, column = -1, -1
        rows, columns = len(grid), len(grid[0])
        coordinates = [(r, c) for r in range(rows) for c in range(columns)]

        # check if unblocked cells exist
        if not any(terrain in row for terrain in [Grid.normal, Grid.highway, Grid.rough_terrain] for row in grid):
            raise Exception("No unblocked cells exist")

        # get random unblocked cell
        while row == -1:
            r, c = random.choice(coordinates)
            if grid[r][c] != Grid.blocked:
                starting_row = row = r
                starting_column = column = c

        # generate actions, ground truth states, and sensor readings
        actions = ''
        ground_truth_states = ''
        sensor_readings = ''
        for x in range(100):
            # actions
            action = random.choice([Grid.up, Grid.down, Grid.left, Grid.right])
            actions += action

            # ground truth states
            num = random.uniform(0, 1)
            if 0 <= num < 0.9:
                match action:
                    case Grid.up:
                        if row > 0 and grid[row - 1][column] != Grid.blocked:
                            row -= 1
                    case Grid.down:
                        if row < rows - 1 and grid[row + 1][column] != Grid.blocked:
                            row += 1
                    case Grid.left:
                        if column > 0 and grid[row][column - 1] != Grid.blocked:
                            column -= 1
                    case Grid.right:
                        if column < columns - 1 and grid[row][column + 1] != Grid.blocked:
                            column += 1
            ground_truth_states += f'{row} {column}\n'

            # sensor readings
            num = random.uniform(0, 1)
            if 0 <= num < 0.9:
                sensor_reading = grid[row][column]
            else:
                sensor_reading = random.choice(
                    [x for x in [Grid.normal, Grid.highway, Grid.rough_terrain] if x != grid[row][column]])
            sensor_readings += sensor_reading

        # write everything to a file
        with open(f'ground_truth_path_{datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}.txt', "w") as file:
            # write coordinates of initial cell
            file.write(f'{starting_row} {starting_column}\n')
            # write ground truth states
            file.write(ground_truth_states)
            # write actions
            file.write(actions + '\n')
            # write sensor readings
            file.write(sensor_readings + '\n')


def test():
    Grid.generate_ground_truth_paths(Grid.generate_grid(100, 50))

def bad_test():
    Grid.generate_ground_truth_paths([[Grid.blocked] * 100] * 50)


if __name__ == '__main__':
    test()
