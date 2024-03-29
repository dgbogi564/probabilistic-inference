import math

import numpy
import pygame
import random
import sys
import os
from datetime import datetime
from pygame.locals import *


class Grid:
    BLACK = (0, 0, 0)  # BORDERS
    GRAY = (100, 100, 100)  # BLOCKED
    GOLD = (255, 215, 0)  # HIGHWAY
    GREEN = (0, 100, 0)  # HARD TO TRAVERSE
    WHITE = (255, 255, 255)  # NORMAL
    RED = (255, 0, 0)  # DEBUG BACKGROUND

    NORMAL, HIGHWAY, HARD_TO_TRAVERSE, BLOCKED = 'N', 'H', 'T', 'B'
    UP, DOWN, LEFT, RIGHT = 'U', 'D', 'L', 'R'

    @classmethod
    def import_grid(cls, filepath):
        grid = None
        with open(filepath, "r") as file:
            rows, columns = map(int, file.readline().split(' '))
            grid = [['' for c in range(columns)] for r in range(rows)]
            for line in file:
                r, c, t = line.split()
                row, column, terrain = int(r), int(c), t
                grid[row - 1][column - 1] = terrain
        return grid

    @classmethod
    def save_grid(cls, grid, filepath):
        rows, columns = len(grid), len(grid[0])
        with open(filepath, "w") as file:
            file.write(f'{rows} {columns}\n')
            for row in range(rows):
                for column in range(columns):
                    file.write(f'{row + 1} {column + 1} {grid[row][column]}\n')
        return filepath

    @classmethod
    def generate_grid(cls, rows, columns):
        grid = [['' for c in range(columns)] for r in range(rows)]
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
                pass
        return grid

    @classmethod
    def draw_grid(cls, grid, actions, sensor_readings, experiment_filepath=None):
        base_cell_size = 150
        base_border_size = 2
        base_font_size = 15
        base_line_width = 5
        base_circle_radius = 10
        width, height = 1000, 1000
        rows, columns = len(grid), len(grid[0])

        pygame.init()

        canvas = pygame.Surface((base_cell_size * (columns + 1), base_cell_size * (rows + 1)))
        canvas.fill(Grid.WHITE)
        canvas_rect = canvas.get_rect()

        def draw():
            nonlocal canvas
            nonlocal canvas_rect
            nonlocal probabilities
            nonlocal step
            nonlocal zoom

            border_size = max(1, round(base_border_size * zoom))
            offset = border_size // 2
            cell_size = max(1, round(base_cell_size * zoom))
            font_size = max(1, round(base_font_size * zoom))
            line_width = max(1, round(base_line_width * zoom))
            circle_radius = max(1, round(base_circle_radius * zoom))

            canvas = pygame.Surface((cell_size * (columns + 1), cell_size * (rows + 1)))
            canvas.fill(Grid.WHITE)
            canvas_rect = canvas.get_rect()

            # Create border with the same size as the grid, centered in image.
            border_rect = pygame.Rect(0, 0, columns * cell_size - (border_size * (columns - 1)),
                                      rows * cell_size - (border_size * (rows - 1)))
            border_rect.center = (canvas.get_width() // 2, canvas.get_height() // 2)

            # Create cells
            for row in range(rows):
                for column in range(columns):
                    # get position of cell
                    left = border_rect.left + column * (cell_size - border_size)
                    right = left + cell_size - border_size
                    top = border_rect.top + row * (cell_size - border_size)
                    bottom = top + cell_size - border_size

                    # get color of cell
                    color = None
                    match grid[row][column]:
                        case Grid.HIGHWAY:
                            color = Grid.GOLD
                        case Grid.HARD_TO_TRAVERSE:
                            color = Grid.GREEN
                        case Grid.BLOCKED:
                            color = Grid.GRAY
                        case Grid.NORMAL:
                            color = Grid.WHITE

                    # draw cell color
                    pygame.draw.rect(canvas, color, (left, top, cell_size, cell_size))

                    # draw cell borders
                    pygame.draw.rect(canvas, Grid.BLACK, pygame.Rect(left, top, cell_size, cell_size), border_size)

                    # draw cell probabilities
                    probability_label = pygame.font.SysFont('calibri', font_size).render(
                        "{:.7f}".format(probabilities[row][column] * 100) + "%", True, Grid.BLACK)
                    probability_label_rect = probability_label.get_rect(
                        center=(left + cell_size // 2, top + cell_size // 2))
                    canvas.blit(probability_label, probability_label_rect)

            # draw grid labels
            for column in range(1, columns + 2):
                x_label = pygame.font.SysFont('calibri', font_size).render(str(column), True, Grid.BLACK)
                x_label_rect = x_label.get_rect(center=(border_rect.left - column + (column - 1) * (cell_size - offset),
                                                        border_rect.top - 4 * circle_radius))
                canvas.blit(x_label, x_label_rect)
            for row in range(1, rows + 2):
                y_label = pygame.font.SysFont('calibri', font_size).render(str(row), True, Grid.BLACK)
                y_label_rect = y_label.get_rect(center=(border_rect.left - 4 * circle_radius,
                                                        border_rect.top - row + (row - 1) * (cell_size - offset)))
                canvas.blit(y_label, y_label_rect)

            # draw step label
            step_label = pygame.font.SysFont('calibri', font_size).render(f'Step: {step}', True, Grid.BLACK)
            step_label_rect = step_label.get_rect(left=font_size / 2, top=font_size / 2)
            canvas.blit(step_label, step_label_rect)

        zoom = 1
        step = 0
        probabilities = Grid.calculate_next_probabilities(grid, actions, sensor_readings, step, step)
        position = [width // 2, height // 2]
        draw()
        moving = False

        if experiment_filepath:
            base = os.path.splitext(experiment_filepath)[0]

            step = 10
            probabilities = Grid.calculate_next_probabilities(grid, actions, sensor_readings, 0, step, probabilities)
            draw()
            pygame.image.save(canvas, base + f'_heatmap_step_{step}.png')

            step = 50
            probabilities = Grid.calculate_next_probabilities(grid, actions, sensor_readings, 10, step, probabilities)
            draw()
            pygame.image.save(canvas, base + f'_heatmap_step_{step}.png')

            step = 100
            probabilities = Grid.calculate_next_probabilities(grid, actions, sensor_readings, 50, step, probabilities)
            draw()
            pygame.image.save(canvas, base + f'_heatmap_step_{step}.png')

            pygame.quit()
            return

        window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        while True:
            dirty = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Set moving true while mouse button is held
                elif event.type == MOUSEBUTTONDOWN:
                    if canvas_rect.collidepoint(event.pos):
                        moving = True

                # Set moving false when mouse button is released
                elif event.type == MOUSEBUTTONUP:
                    moving = False

                # Click and drag image
                elif event.type == MOUSEMOTION and moving:
                    pos = list(event.rel)
                    canvas_rect.move_ip(pos)

                # Zoom
                elif event.type == MOUSEWHEEL:
                    if event.y > 0.1:
                        zoom += 0.1
                    elif zoom > 0.2:
                        zoom -= 0.1

                    position[0] = round(canvas_rect.left * zoom)
                    position[1] = round(canvas_rect.right * zoom)
                    dirty = True

                # Change Step
                elif event.type == KEYDOWN and event.key == pygame.K_RIGHT and step < len(actions):
                    probabilities = Grid.calculate_next_probabilities(grid, actions, sensor_readings, step, step + 1, probabilities)
                    step += 1
                    dirty = True

            if dirty:
                draw()

            window.fill(Grid.WHITE)

            # Set canvas and image
            window.blit(canvas, canvas_rect)

            # Construct image border
            pygame.draw.rect(window, Grid.WHITE, canvas_rect, 2)

            # Update screen
            pygame.display.update()

    @classmethod
    def import_experiment(cls, filepath, num_actions):
        ground_truth_states, actions, sensor_readings = [], [], []
        with open(filepath, "r") as file:
            lines = file.readlines()

        for x in range(min(num_actions + 1, len(lines) - 2)):
            ground_truth_states.append(lines[x].strip())

        action_states = lines[-2].strip()
        for x in range(min(num_actions, len(action_states))):
            actions.append(action_states[x])

        sensor_reading_states = lines[-1].strip()
        for x in range(min(num_actions, len(sensor_reading_states))):
            sensor_readings.append(sensor_reading_states[x])

        return ground_truth_states, actions, sensor_readings

    @classmethod
    def save_experiment(cls, ground_truth_states, actions, sensor_readings, filepath):
        with open(filepath, "w") as file:
            # write ground truth states
            file.write('\n'.join(ground_truth_states) + '\n')

            # write actions
            file.write(''.join(actions) + '\n')

            # write sensor readings
            file.write(''.join(sensor_readings) + '\n')
        return filepath

    @classmethod
    def generate_experiment(cls, grid):
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
                row = r
                column = c

        # generate actions, ground truth states, and sensor readings
        actions = []
        ground_truth_states = [f'{row} {column}']  # append starting row and column
        sensor_readings = []
        for x in range(100):
            # actions
            action = random.choice([Grid.UP, Grid.DOWN, Grid.LEFT, Grid.RIGHT])
            actions.append(action)

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
            ground_truth_states.append(f'{row + 1} {column + 1}')

            # sensor readings
            num = random.uniform(0, 1)
            if 0 <= num < 0.9:
                sensor_reading = grid[row][column]
            else:
                sensor_reading = random.choice(
                    [x for x in [Grid.NORMAL, Grid.HIGHWAY, Grid.HARD_TO_TRAVERSE] if x != grid[row][column]])
            sensor_readings.append(sensor_reading)

        return ground_truth_states, actions, sensor_readings

    @classmethod
    def calculate_next_probabilities(cls, grid, actions, sensor_readings, start_step=0, end_step=0, probabilities=None):
        rows, columns = len(grid), len(grid[0])

        if not probabilities:
            num_unblocked_cells = rows * columns - sum(r.count('B') for r in grid)
            probabilities = [[1 / num_unblocked_cells if grid[r][c] != 'B' else 0 for c in range(columns)] for r in
                             range(rows)]

        # len(actions) == len(sensor_readings)
        for i in range(start_step, end_step):

            # use previous probabilities for current step
            prev_probabilities = [r[:] for r in probabilities]

            # actions
            for row in range(rows):
                for column in range(columns):
                    if grid[row][column] == Grid.BLOCKED:
                        continue
                    probabilities[row][column] = 0
                    match actions[i]:
                        # Failed to move to next cell from current cell (fails)
                        # Stays at current cell, but didn't fail (blocked or at border)
                        # Move to current cell from previous cell (success)
                        case Grid.UP:
                            # Failed to move to next cell from current cell (fails)
                            if row > 0 and grid[row - 1][column] != Grid.BLOCKED:
                                probabilities[row][column] += 0.1 * prev_probabilities[row][column]
                            # Stays at current cell, but didn't fail (blocked or at border)
                            else:
                                probabilities[row][column] += prev_probabilities[row][column]

                            # Move to current cell from previous cell (success)
                            if row < rows - 1 and grid[row + 1][column] != Grid.BLOCKED:
                                probabilities[row][column] += 0.9 * prev_probabilities[row + 1][column]

                        case Grid.DOWN:
                            # Failed to move to next cell from current cell (fails)
                            if row < rows - 1 and grid[row + 1][column] != Grid.BLOCKED:
                                probabilities[row][column] += 0.1 * prev_probabilities[row][column]

                            # Move to current cell from previous cell (success)
                            if row > 0 and grid[row - 1][column] != Grid.BLOCKED:
                                probabilities[row][column] += 0.9 * prev_probabilities[row - 1][column]

                        case Grid.LEFT:
                            # Failed to move to next cell from current cell (fails)
                            if column > 0 and grid[row][column - 1] != Grid.BLOCKED:
                                probabilities[row][column] += 0.1 * prev_probabilities[row][column]
                            else:
                                probabilities[row][column] += prev_probabilities[row][column]
                            # Move to current cell from previous cell (success)
                            if column < columns - 1 and grid[row][column + 1] != Grid.BLOCKED:
                                probabilities[row][column] += 0.9 * prev_probabilities[row][column + 1]

                        case Grid.RIGHT:
                            # Failed to move to next cell from current cell (fails)
                            if column < columns - 1 and grid[row][column + 1] != Grid.BLOCKED:
                                probabilities[row][column] += 0.1 * prev_probabilities[row][column]
                            else:
                                probabilities[row][column] += prev_probabilities[row][column]
                            # Move to current cell from previous cell (success)
                            if column > 0 and grid[row][column - 1] != Grid.BLOCKED:
                                probabilities[row][column] += 0.9 * prev_probabilities[row][column - 1]

            # sensor readings
            for row in range(rows):
                for column in range(columns):
                    if grid[row][column] != 'B' and grid[row][column] == sensor_readings[i]:
                        probabilities[row][column] *= 0.9
                    else:
                        probabilities[row][column] *= 0.05

            # normalization
            sum_probabilities = sum(sum(r) for r in probabilities)
            for row in range(rows):
                for column in range(columns):
                    probabilities[row][column] /= sum_probabilities

        return probabilities


def test():
    grid = None
    probabilities = None
    grid_filepath = None
    ground_truth_states, actions, sensor_readings = None, None, None
    experiment_filepath = None

    try:
        grid = Grid.generate_grid(3, 4)
        print('[PASSED] Generate grid\n\n')
    except Exception as e:
        print('[FAILED] Generate grid:\n' + e.__str__() + '\n\n')
        exit(1)

    if grid is not None:
        try:
            grid_filepath = Grid.save_grid(grid, '../test/grid_test.txt')
            print('[PASSED] Save grid\n\n')
        except Exception as e:
            print('[FAILED] Save grid:\n' + e.__str__() + '\n\n')

        try:
            ground_truth_states, actions, sensor_readings = Grid.generate_experiment(grid)
            print("[PASSED] Generate experiment for randomly generated grid\n\n")
        except Exception as e:
            print("[FAILED] Generate experiment for randomly generated grid:\n" + e.__str__() + '\n\n')

        try:
            experiment_filepath = Grid.save_experiment(ground_truth_states, actions, sensor_readings,
                                                       '../test/grid_experiment_test.txt')
            print("[PASSED] Save experiment\n\n")
        except Exception as e:
            print("[FAILED] Save experiment:\n" + e.__str__() + '\n\n')

        if actions is not None and sensor_readings is not None:
            try:
                Grid.calculate_next_probabilities(grid, actions, sensor_readings, 0, len(actions))
                print("[PASSED] Calculate probabilities\n\n")
            except Exception as e:
                print("[Failed] Calculate probabilities:\n" + e.__str__() + '\n\n')

    try:
        Grid.generate_experiment([[Grid.BLOCKED] * 100] * 50)
        print("[FAILED] Generate experiment of blocked grid\n\n")
    except Exception as e:
        if e.__str__() == "No unblocked cells exist":
            print("[PASSED] Generate experiments of blocked grid\n\n")

    if grid_filepath is not None:
        try:
            imported_grid = Grid.import_grid(grid_filepath)
            if imported_grid == grid:
                print('[PASSED] Import grid\n\n')
            else:
                raise Exception('Grid mismatch')
        except Exception as e:
            print('[FAILED] Import grid:\n' + e.__str__() + '\n\n')

    if experiment_filepath is not None:
        try:
            imported_ground_truth_states, imported_actions, imported_sensor_readings \
                = Grid.import_experiment(experiment_filepath, 100)
            if imported_ground_truth_states == ground_truth_states \
                    and imported_actions == actions \
                    and imported_sensor_readings == sensor_readings:
                print('[PASSED] Import experiment\n\n')
            else:
                raise Exception('Experiment mismatch')
        except Exception as e:
            print('[FAILED] Import experiment:\n' + e.__str__() + '\n\n')

    grid = Grid.import_grid('../out/grid_0.txt')  # Grid.import_grid('part_a_grid.txt')
    ground_truth_states, actions, sensor_readings = Grid.import_experiment('../out/grid_0_experiment_0.txt',
                                                                           100)  # Grid.import_experiment('part_a_experiment.txt', 4)
    if grid is not None and actions is not None and sensor_readings is not None:
        print("[INFO] Drawing grid...")
        Grid.draw_grid(grid, actions, sensor_readings)


def generate_10_maps_and_100_experiments():
    if not os.path.exists('../out'):
        os.makedirs('../out')

    for x in range(10):
        grid = Grid.generate_grid(100, 50)
        Grid.save_grid(grid, f'../out/grid_{x}.txt')
        for y in range(10):
            ground_truth_states, actions, sensor_readings = Grid.generate_experiment(grid)
            Grid.save_experiment(ground_truth_states, actions, sensor_readings, f'../out/grid_{x}_experiment_{y}.txt')


def generate_error_rate_of_100_experiments():
    def find_maximum(probabilities):
        r = 0
        c = 0
        highest_value = 0
        for row in range(len(probabilities)):
            for column in range(len(probabilities[0])):
                if probabilities[row][column] > highest_value:
                    highest_value = probabilities[row][column]
                    r = row
                    c = column
        return r, c

    def get_ground_truth_location(ground_truth):
        row, column = ground_truth.split()
        return int(row) - 1, int(column) - 1

    def calculate_average_experiment_error_and_probability(grid, filepath, num_actions):
        ground_truth_states, actions, sensor_readings = Grid.import_experiment(filepath, num_actions)
        probabilities = Grid.calculate_next_probabilities(grid, actions, sensor_readings, 0, 4)
        error_distance = []
        ground_truth_path_probability = []
        for step in range(4, len(ground_truth_states) - 1):
            probabilities = Grid.calculate_next_probabilities(grid, actions, sensor_readings, step, step + 1,
                                                              probabilities)
            pr, pc = find_maximum(probabilities)
            gr, gc = get_ground_truth_location(ground_truth_states[step])
            error_distance.append(math.sqrt((pr - gr) ** 2 + (pc - gc) ** 2))
            ground_truth_path_probability.append(probabilities[gr][gc])
        return numpy.mean(error_distance), numpy.mean(ground_truth_path_probability)

    with open('../out/error_rate.csv', "w") as file:
        file.write("grid,experiment,average_distance_error, average_ground_truth_path_probability\n")
        for x in range(10):
            grid = Grid.import_grid(f'../out/grid_{x}.txt')
            for y in range(10):
                average_distance_error, average_ground_truth_path_probability = \
                    calculate_average_experiment_error_and_probability(grid, f'../out/grid_{x}_experiment_{y}.txt', 100)
                file.write(f'{x},{y},{average_distance_error},{average_ground_truth_path_probability}\n')


def get_heatmap():
    for x in range(10):
        grid = Grid.import_grid(f'../out/grid_{x}.txt')
        for y in range(10):
            filepath = f'../out/grid_{x}_experiment_{y}.txt'
            ground_truth_states, actions, sensor_readings = Grid.import_experiment(filepath, 100)
            Grid.draw_grid(grid, actions, sensor_readings, experiment_filepath=filepath)


if __name__ == '__main__':
    # generate_10_maps_and_100_experiments()
    # test()
    # generate_error_rate_of_100_experiments()
    get_heatmap()
