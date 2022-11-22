from datetime import datetime
import itertools
import pygame
from pygame.locals import *
import random
import sys
import numpy


# TODO input grid format?

class Grid:
    BLACK = (0, 0, 0)  # BORDERS
    GRAY = (100, 100, 100)  # BLOCKED
    GOLD = (255, 215, 0)  # HIGHWAY
    GREEN = (0, 100, 0)  # HARD TO TRAVERSE
    WHITE = (255, 255, 255)  # NORMAL

    NORMAL, HIGHWAY, HARD_TO_TRAVERSE, BLOCKED = 'N', 'H', 'T', 'B'
    UP, DOWN, LEFT, RIGHT = 'U', 'D', 'L', 'R'

    @classmethod
    def import_grid(cls, filepath):
        grid = None
        with open(filepath, "r") as file:
            rows, columns = map(int, file.readline().split(' '))
            grid = [[''] * columns] * rows
            for line in file:
                r, c, t = line.split()
                row, column, terrain = int(r), int(c), t
                grid[row][column] = terrain
        return grid

    @classmethod
    def generate_grid(cls, rows, columns):
        grid = [[''] * columns] * rows
        for row in range(rows):
            for column in range(columns):
                num = random.uniform(0, 1)
                if 0 <= num <= 0.5:
                    grid[row][column] = Grid.NORMAL
                elif 0.5 < num <= 0.7:
                    grid[row][column] = Grid.HIGHWAY
                elif 0.7 < num <= 0.9:
                    grid[row][column] = Grid.HARD_TO_TRAVERSE
                else:
                    grid[row][column] = Grid.BLOCKED
        return grid

    @classmethod
    def save_grid(cls, grid):
        rows, columns = len(grid), len(grid[0])
        filepath = f'grid_{datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}.txt'
        with open(filepath, "w") as file:
            file.write(f'{rows} {columns}\n')
            for row in range(rows):
                for column in range(columns):
                    file.write(f'{row} {column} {grid[row][column]}\n')
        return filepath

    @classmethod
    def draw_grid(cls, grid):
        # TODO
        width, height = 1000, 1000
        window = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        cell_size = 150
        circle_radius = 10
        border_size = 2
        font_size = 35
        line_width = 5

    @classmethod
    def generate_ground_truth_paths(cls, grid, probabilities):
        row, column = -1, -1
        starting_row, starting_column = -1, -1
        rows, columns = len(grid), len(grid[0])
        coordinates = [(r, c) for r in range(rows) for c in range(columns)]

        # check if unblocked cells exist
        if not any(terrain in row for terrain in [Grid.NORMAL, Grid.HIGHWAY, Grid.HARD_TO_TRAVERSE] for row in grid):
            raise Exception("No unblocked cells exist")

        # get random unblocked cell
        while row == -1:
            r, c = random.choice(coordinates)
            if grid[r][c] != Grid.BLOCKED:
                starting_row = row = r
                starting_column = column = c

        # generate actions, ground truth states, and sensor readings
        actions = []  # actions = ''
        ground_truth_states = []  # ground_truth_states = ''
        sensor_readings = []  # sensor_readings = ''
        for x in range(100):
            # actions
            action = random.choice([Grid.UP, Grid.DOWN, Grid.LEFT, Grid.RIGHT])
            actions.append(action)  # actions += action

            # ground truth states
            num = random.uniform(0, 1)
            if 0 <= num < 0.9:
                match action:
                    case Grid.UP:
                        if row > 0 and grid[row - 1][column] != Grid.BLOCKED:
                            row -= 1
                    case Grid.DOWN:
                        if row < rows - 1 and grid[row + 1][column] != Grid.BLOCKED:
                            row += 1
                    case Grid.LEFT:
                        if column > 0 and grid[row][column - 1] != Grid.BLOCKED:
                            column -= 1
                    case Grid.RIGHT:
                        if column < columns - 1 and grid[row][column + 1] != Grid.BLOCKED:
                            column += 1
            ground_truth_states.append(f'{row} {column}')  # ground_truth_states += f'{row} {column}\n'

            # sensor readings
            num = random.uniform(0, 1)
            if 0 <= num < 0.9:
                sensor_reading = grid[row][column]
            else:
                sensor_reading = random.choice(
                    [x for x in [Grid.NORMAL, Grid.HIGHWAY, Grid.HARD_TO_TRAVERSE] if x != grid[row][column]])
            sensor_readings.append(sensor_reading)  # sensor_readings += sensor_reading

        # write everything to a file
        filepath = f'ground_truth_path_{datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}.txt'
        with open(filepath, "w") as file:
            # write coordinates of initial cell
            file.write(f'{starting_row} {starting_column}\n')
            # write ground truth states
            file.write('\n'.join(ground_truth_states) + '\n')
            # write actions
            file.write(''.join(actions) + '\n')
            # write sensor readings
            file.write(''.join(sensor_readings) + '\n')

        return filepath

    @classmethod
    def calculate_probabilities(cls, grid, ground_truth_paths):
        # TODO



def test():
    grid = None
    try:
        grid = Grid.generate_grid(3, 4)
        print('[PASSED] Generate grid\n')
    except Exception as e:
        print('[FAILED] Generate grid:\n' + e.__str__() + '\n\n')
        exit(1)

    grid_filepath = None
    if grid is not None:
        try:
            grid_filepath = Grid.save_grid(grid)
            print('[PASSED] Save grid\n')
        except Exception as e:
            print('[FAILED] Save grid:\n' + e.__str__() + '\n\n')

        try:
            Grid.generate_ground_truth_paths(grid)
            print("[PASSED] Generate ground truth paths of randomly generated grid\n")
        except Exception as e:
            print("[FAILED] Generate ground truth paths of randomly generated grid:\n" + e.__str__() + '\n\n')

    try:
        Grid.generate_ground_truth_paths([[Grid.BLOCKED] * 100] * 50)
        print("[FAILED] Generate ground truth paths of blocked grid\n")
    except Exception as e:
        if e.__str__() == "No unblocked cells exist":
            print("[PASSED] Generate ground truth paths of blocked grid\n")

    if grid_filepath is not None:
        try:
            imported_grid = Grid.import_grid(grid_filepath)
            if imported_grid == grid:
                print('[PASSED] Import grid\n')
            else:
                raise Exception('Grid mismatch')
        except Exception as e:
            print('[FAILED] Import grid:\n' + e.__str__() + '\n\n')


if __name__ == '__main__':
    test()
