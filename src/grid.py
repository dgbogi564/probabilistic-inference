import sys
from datetime import datetime
import pygame
from pygame.locals import *
import random


# TODO input grid format?

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
                grid[row-1][column-1] = terrain
        return grid

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
    def save_grid(cls, grid):
        rows, columns = len(grid), len(grid[0])
        filepath = f'grid_{datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")}.txt'
        with open(filepath, "w") as file:
            file.write(f'{rows} {columns}\n')
            for row in range(rows):
                for column in range(columns):
                    file.write(f'{row+1} {column+1} {grid[row][column]}\n')
        return filepath

    @classmethod
    def draw_grid(cls, grid):
        # TODO need to label probabilities
        base_cell_size = 150
        base_border_size = 2
        base_font_size = 35
        base_line_width = 5
        base_circle_radius = 10
        width, height = 1000, 1000
        rows, columns = len(grid), len(grid[0])

        pygame.init()

        window = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        canvas = pygame.Surface((base_cell_size * (columns + 1), base_cell_size * (rows + 1)))
        canvas.fill(Grid.RED)  # TODO canvas.fill(Grid.WHITE)
        canvas_rect = canvas.get_rect()

        def draw(zoom):
            nonlocal canvas
            nonlocal canvas_rect

            border_size = max(1, round(base_border_size * zoom))
            offset = border_size // 2
            cell_size = max(1, round(base_cell_size * zoom))
            font_size = max(1, round(base_font_size * zoom))
            line_width = max(1, round(base_line_width * zoom))
            circle_radius = max(1, round(base_circle_radius * zoom))

            canvas = pygame.Surface((cell_size * (columns + 1), cell_size * (rows + 1)))
            canvas.fill(Grid.RED)
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
                    # TODO REPLACE WITH PROBABILITIES
                    probability_label = pygame.font.SysFont('calibri', font_size).render(str('#.###'), True, Grid.BLACK)
                    probability_label_rect = probability_label.get_rect(center=(left + cell_size//2, top + cell_size//2))
                    canvas.blit(probability_label, probability_label_rect)

            # draw grid labels
            for column in range(1, columns + 2):
                x_label = pygame.font.SysFont('calibri', font_size).render(str(column), True, Grid.BLACK)
                x_label_rect = x_label.get_rect(center=(border_rect.left + (column - 1) * (cell_size - offset),
                                                        border_rect.top - 4 * circle_radius))
                canvas.blit(x_label, x_label_rect)
            for row in range(1, rows + 2):
                y_label = pygame.font.SysFont('calibri', font_size).render(str(row), True, Grid.BLACK)
                y_label_rect = y_label.get_rect(center=(border_rect.left - 4 * circle_radius,
                                                        border_rect.top + (row - 1) * (cell_size - offset)))
                canvas.blit(y_label, y_label_rect)

        zoom = 1
        position = [width // 2, height // 2]
        draw(zoom)
        moving = False
        while True:
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
                    draw(zoom)

            window.fill(Grid.WHITE)

            # Set canvas and image
            window.blit(canvas, canvas_rect)

            # Construct image border
            pygame.draw.rect(window, Grid.WHITE, canvas_rect, 2)

            # Update screen
            pygame.display.update()

    @classmethod
    def generate_ground_truth_paths(cls, grid):
        # TODO more research into probabilities?
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
        actions = []
        ground_truth_states = []
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
            ground_truth_states.append(f'{row} {column}')

            # sensor readings
            num = random.uniform(0, 1)
            if 0 <= num < 0.9:
                sensor_reading = grid[row][column]
            else:
                sensor_reading = random.choice(
                    [x for x in [Grid.NORMAL, Grid.HIGHWAY, Grid.HARD_TO_TRAVERSE] if x != grid[row][column]])
            sensor_readings.append(sensor_reading)

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
        pass


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

    print("[INFO] Drawing grid...")
    Grid.draw_grid(grid)
    pass


if __name__ == '__main__':
    test()