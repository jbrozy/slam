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
        self.x = 20
        self.y = 20
        self.screen = screen
        self.heading = 0
        self.sensor_range = 2
        self.map = []  # Liste für erkannte Hindernisse
        self.exploration_state = 'exploring'  # Exploration mode

    def move(self, speed):
        # Update position based on current heading and speed
        self.x += speed * math.cos(self.heading)
        self.y += speed * math.sin(self.heading)

    def sense_obstacles(self):
        """Sense obstacles in a 30-degree field of view (FOV)."""
        # Angle range: 30 degrees FOV centered around the robot's heading
        fov_angle = math.radians(60)  # Convert 30 degrees to radians
        start_angle = self.heading - fov_angle / 2  # Start angle (heading - 15 degrees)
        end_angle = self.heading + fov_angle / 2    # End angle (heading + 15 degrees)
        
        # Number of rays to cast within the FOV (e.g., 10 rays within the 30 degrees)
        num_rays = 10
        angle_step = fov_angle / num_rays  # Step between each ray
        
        # Cast rays at each angle in the FOV
        for i in range(num_rays):
            # Calculate the angle of the current ray
            ray_angle = start_angle + i * angle_step
            
            # Calculate the end point of the ray
            target_x = self.x + self.sensor_range * math.cos(ray_angle)
            target_y = self.y + self.sensor_range * math.sin(ray_angle)
            
            # Detect obstacle along this ray
            self.detect_obstacle(target_x, target_y)


    def rotate(self, angle):
        self.heading += angle
        self.heading %= 2 * math.pi

    def draw(self):
        color = (255, 255, 255)  # Weißer Roboter
        pygame.draw.circle(self.screen, color, (int(self.x), int(self.y)), 10)
        end_x = self.x + 20 * math.cos(self.heading)
        end_y = self.y + 20 * math.sin(self.heading)
        # Richtungslinie
        pygame.draw.line(self.screen, color, (self.x, self.y), (end_x, end_y), 2)

    def detect_obstacle(self, target_x, target_y):
        x = self.x
        y = self.y

        dx = abs(target_x - x)
        dy = abs(target_y - y)
        sx = 1 if target_x > x else -1
        sy = 1 if target_y > y else -1

        err = dx - dy

        while True:
            r_x, r_y = int(round(x)), int(round(y))

            # Check if we are outside of the valid range (in the range [0, 799] for x, and [0, 599] for y)
            if r_x < 0 or r_y < 0 or r_x >= 800 or r_y >= 600:
                return False  # Outside screen bounds

            pixel_color = self.screen.get_at((r_x, r_y))
            # Debugging: print the pixel color

            # Check if the pixel color is close to white (tolerance of 10)
            if pixel_color == (255, 255, 255, 255):
                self.map.append((r_x, r_y))
                return True  # White pixel found

            if x == target_x and y == target_y:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx * self.sensor_range
            if e2 < dx:
                err += dx
                y += sy * self.sensor_range

        return False  # No white pixel detected

    def is_white(self, pixel_color):
        # Tolerance for color comparison (adjust if needed)
        tolerance = 10
        r, g, b, a = pixel_color

        # Debugging: print the RGB values
        # print(f"Checking color: R={r}, G={g}, B={b}, A={a}")

        # Ensure that we only check the RGB components and disregard the alpha channel
        return (abs(r - 255) <= tolerance and abs(g - 255) <= tolerance and abs(b - 255) <= tolerance)
    def draw_map(self):
        """Zeichne alle erkannten Hindernisse."""
        for x, y in self.map:
            pygame.draw.circle(self.screen, (255, 0, 0), (int(x), int(y)), 2)  # Rote Hindernisse
    def avoid_obstacles(self):
        """Simple logic to avoid obstacles based on detected positions."""
        # Check for obstacles near the front
        if len(self.map) > 0:
            for (obstacle_x, obstacle_y) in self.map:
                distance = math.dist((self.x, self.y), (obstacle_x, obstacle_y))
                if distance < SENSOR_THRESHOLD:
                    # If obstacle is close, turn
                    self.rotate(math.pi / 2)  # Turn 90 degrees to avoid
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
        neighbors = []
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # oben, rechts, unten, links

        for dr, dc in directions:
            new_row = cell.row + dr
            new_col = cell.col + dc

            if (0 <= new_row < self.rows and 0 <= new_col < self.cols and 
                not self.grid[new_row][new_col].visited):
                neighbors.append(self.grid[new_row][new_col])

        return neighbors

    def remove_walls(self, current: Cell, next_cell: Cell):
        dx = next_cell.col - current.col
        dy = next_cell.row - current.row

        if dx == 1:  # rechts
            current.walls["right"] = False
            next_cell.walls["left"] = False
        elif dx == -1:  # links
            current.walls["left"] = False
            next_cell.walls["right"] = False
        elif dy == 1:  # unten
            current.walls["bottom"] = False
            next_cell.walls["top"] = False
        elif dy == -1:  # oben
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
        colors = [(0, 255, 0), (255, 165, 0), (0, 0, 255)]  # grün, orange, blau
        available_cells = [(i, j) for i in range(self.rows) for j in range(self.cols)]
        random_cells = random.sample(available_cells, 3)

        for (row, col), color in zip(random_cells, colors):
            self.grid[row][col].color = color

    def draw_cell(self, cell: Cell):
        x = cell.col * self.cell_size
        y = cell.row * self.cell_size

        if cell.color:
            pygame.draw.rect(self.screen, cell.color,
                             (x + 1, y + 1, self.cell_size - 1, self.cell_size - 1))

        if cell.walls["top"]:
            pygame.draw.line(self.screen, (255, 255, 255),
                             (x, y), (x + self.cell_size, y), 2)
        if cell.walls["right"]:
            pygame.draw.line(self.screen, (255, 255, 255),
                             (x + self.cell_size, y), (x + self.cell_size, y + self.cell_size), 2)
        if cell.walls["bottom"]:
            pygame.draw.line(self.screen, (255, 255, 255),
                             (x, y + self.cell_size), (x + self.cell_size, y + self.cell_size), 2)
        if cell.walls["left"]:
            pygame.draw.line(self.screen, (255, 255, 255),
                             (x, y), (x, y + self.cell_size), 2)

    def run(self):
        while self.running:
            t = pygame.time.get_ticks()
            dt = (t - self.last_tick) / 1000.0
            self.last_tick = t

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.robot.rotate(-ROTATE_SPEED * dt)  # Rotate left
            if keys[pygame.K_RIGHT]:
                self.robot.rotate(ROTATE_SPEED * dt)  # Rotate right
            if keys[pygame.K_UP]:
                self.robot.move(ROBOT_SPEED)  # Move forward
            if keys[pygame.K_DOWN]:
                self.robot.move(-ROBOT_SPEED)  # Move backward
            if keys[pygame.K_0]:
                print(self.robot.map)

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
