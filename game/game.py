import math
import random
from enum import Enum
from typing import List, Set, Tuple

import numpy as np
import pygame

ROTATE_SPEED = 1
ROBOT_SPEED = 1
SENSOR_THRESHOLD = 5

class Robot:
    def __init__(self, screen):
        self.pos = np.array([20.0, 20.0])  # Position vector [x, y]
        self.screen = screen
        self.heading = 0
        self.sensor_range = 2
        self.map = []  # List of obstacle coordinates as numpy arrays
        self.exploration_state = 'exploring'

    def move(self, speed):
        # Calculate direction vector from heading
        direction = np.array([math.cos(self.heading), math.sin(self.heading)])
        self.pos += speed * direction

    def sense_obstacles(self):
        """Sense obstacles in a 30-degree field of view (FOV)."""
        fov_angle = math.radians(60)
        start_angle = self.heading - fov_angle / 2
        end_angle = self.heading + fov_angle / 2
        num_rays = 10
        # Cast rays using numpy arrays for directions
        angles = np.linspace(start_angle, end_angle, num_rays)
        directions = np.column_stack((np.cos(angles), np.sin(angles)))
        for direction in directions:
            target_pos = self.pos + self.sensor_range * direction
            self.detect_obstacle(target_pos)

    def rotate(self, angle):
        self.heading = (self.heading + angle) % (2 * math.pi)

    def draw(self):
        color = (255, 255, 255)
        pos_int = self.pos.astype(int)
        pygame.draw.circle(self.screen, color, pos_int, 10)
        # Calculate end point for heading indicator
        direction = np.array([math.cos(self.heading), math.sin(self.heading)])
        end_pos = self.pos + 20 * direction
        end_pos_int = end_pos.astype(int)
        pygame.draw.line(self.screen, color, pos_int, end_pos_int, 2)

    def detect_obstacle(self, target_pos):
        current_pos = self.pos.copy()
        target_pos = np.array(target_pos)
        # Calculate direction and distance
        delta = np.abs(target_pos - current_pos)
        step = np.sign(target_pos - current_pos)
        # Bresenham's line algorithm with numpy
        err = delta[0] - delta[1]
        while True:
            pos_int = np.round(current_pos).astype(int)
            # Check bounds
            if not (0 <= pos_int[0] < 800 and 0 <= pos_int[1] < 600):
                return False

            # Get pixel color at current position
            pixel_color = self.screen.get_at(pos_int)
            # Check for white pixels (walls)
            if pixel_color == (255, 255, 255, 255):
                self.map.append(pos_int)
                return True

            if np.array_equal(current_pos, target_pos):
                break

            e2 = 2 * err
            if e2 > -delta[1]:
                err -= delta[1]
                current_pos[0] += step[0] * self.sensor_range
            if e2 < delta[0]:
                err += delta[0]
                current_pos[1] += step[1] * self.sensor_range

        return False

    def draw_map(self):
        """Draw detected obstacles."""
        for obstacle_pos in self.map:
            pygame.draw.circle(self.screen, (255, 0, 0), obstacle_pos, 2)

    def avoid_obstacles(self):
        """Obstacle avoidance using numpy operations."""
        if self.map:
            obstacles = np.array(self.map)
            # Calculate distances to all obstacles using numpy
            distances = np.linalg.norm(obstacles - self.pos, axis=1)
            if np.any(distances < SENSOR_THRESHOLD):
                self.rotate(math.pi / 2)
                return


class Cell:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.walls = {"top": True, "right": True, "bottom": True, "left": True}
        self.visited = False
        self.color = None


class Game:
    def __init__(self, width=800, height=600, cell_size=40):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Slam")
        self.clock = pygame.time.Clock()
        self.last_tick = 0
        self.running = True
        self.robot = Robot(self.screen)
        self.cell_size = cell_size
        self.cols = width // cell_size
        self.rows = height // cell_size
        self.grid = self.create_grid()
        self.current = self.grid[0][0]
        self.stack: List[Cell] = []
        self.generate_maze()
        self.place_colored_cells()

    def create_grid(self) -> List[List[Cell]]:
        return [[Cell(i, j) for j in range(self.cols)] for i in range(self.rows)]

    def get_neighbors(self, cell: Cell) -> List[Cell]:
        # Create direction vectors using numpy
        directions = np.array([[0, -1], [1, 0], [0, 1], [-1, 0]])
        neighbors = []
        cell_pos = np.array([cell.row, cell.col])

        for direction in directions:
            new_pos = cell_pos + direction
            if (0 <= new_pos[0] < self.rows and 
                0 <= new_pos[1] < self.cols and 
                not self.grid[new_pos[0]][new_pos[1]].visited):
                neighbors.append(self.grid[new_pos[0]][new_pos[1]])

        return neighbors

    def remove_walls(self, current: Cell, next_cell: Cell):
        # Calculate cell difference using numpy
        diff = np.array([next_cell.col - current.col, 
                        next_cell.row - current.row])
        
        if diff[0] == 1:  # right
            current.walls["right"] = False
            next_cell.walls["left"] = False
        elif diff[0] == -1:  # left
            current.walls["left"] = False
            next_cell.walls["right"] = False
        elif diff[1] == 1:  # down
            current.walls["bottom"] = False
            next_cell.walls["top"] = False
        elif diff[1] == -1:  # up
            current.walls["top"] = False
            next_cell.walls["bottom"] = False

    def generate_maze(self):
        self.current.visited = True
        self.stack.append(self.current)

        while self.stack:
            current = self.stack[-1]
            neighbors = self.get_neighbors(current)

            if neighbors:
                next_cell = random.choice(neighbors)
                next_cell.visited = True
                self.remove_walls(current, next_cell)
                self.current = next_cell
                self.stack.append(next_cell)
            else:
                self.stack.pop()

    def place_colored_cells(self):
        colors = np.array([(0, 255, 0), (255, 165, 0), (0, 0, 255)])
        available_cells = np.array([(i, j)
                                  for i in range(self.rows)
                                  for j in range(self.cols)])
        random_indices = np.random.choice(len(available_cells),
                                        size=3,
                                        replace=False)
        random_cells = available_cells[random_indices]

        for (row, col), color in zip(random_cells, colors):
            self.grid[row][col].color = tuple(color)

    def draw_cell(self, cell: Cell):
        pos = np.array([cell.col * self.cell_size,
                       cell.row * self.cell_size])

        if cell.color:
            pygame.draw.rect(self.screen, cell.color,
                           (*pos + 1, self.cell_size - 1, self.cell_size - 1))

        if cell.walls["top"]:
            pygame.draw.line(self.screen, (255, 255, 255),
                           pos, pos + [self.cell_size, 0], 2)
        if cell.walls["right"]:
            pygame.draw.line(self.screen, (255, 255, 255),
                           pos + [self.cell_size, 0],
                           pos + [self.cell_size, self.cell_size], 2)
        if cell.walls["bottom"]:
            pygame.draw.line(self.screen, (255, 255, 255),
                           pos + [0, self.cell_size],
                           pos + [self.cell_size, self.cell_size], 2)
        if cell.walls["left"]:
            pygame.draw.line(self.screen, (255, 255, 255),
                           pos, pos + [0, self.cell_size], 2)

    def run(self):
        while self.running:
            t = pygame.time.get_ticks()
            dt = (t - self.last_tick) / 1000.0
            self.last_tick = t

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.robot.rotate(-ROTATE_SPEED * dt)
            if keys[pygame.K_RIGHT]:
                self.robot.rotate(ROTATE_SPEED * dt)
            if keys[pygame.K_UP]:
                self.robot.move(ROBOT_SPEED)
            if keys[pygame.K_DOWN]:
                self.robot.move(-ROBOT_SPEED)
            if keys[pygame.K_0]:
                print(np.array(self.robot.map))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill((0, 0, 0))
            for row in self.grid:
                for cell in row:
                    self.draw_cell(cell)
            self.robot.sense_obstacles()
            self.robot.draw_map()
            self.robot.draw()
            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()

