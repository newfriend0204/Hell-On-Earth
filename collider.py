import math
import pygame

class Collider:
    def __init__(self, shape, center, size):
        self.shape = shape  # "circle" or "ellipse"
        self.center = center
        self.size = size

    def check_collision_circle(self, circle_center, circle_radius):
        if self.shape == "circle":
            dx = circle_center[0] - self.center[0]
            dy = circle_center[1] - self.center[1]
            dist_sq = dx*dx + dy*dy
            r_sum = circle_radius + self.size
            return dist_sq <= r_sum * r_sum

        elif self.shape == "ellipse":
            cx, cy = self.center
            rx, ry = self.size
            dx = circle_center[0] - cx
            dy = circle_center[1] - cy
            value = (dx*dx) / (rx*rx) + (dy*dy) / (ry*ry)
            return value <= 1.0

        return False

    def draw(self, screen, world_offset_x, world_offset_y, obstacle_world_pos):
        cx, cy = self.center
        world_cx = obstacle_world_pos[0] + cx
        world_cy = obstacle_world_pos[1] + cy
        screen_x = world_cx - world_offset_x
        screen_y = world_cy - world_offset_y

        if self.shape == "circle":
            pygame.draw.circle(
                screen,
                (255, 0, 0),
                (int(screen_x), int(screen_y)),
                int(self.size),
                2
            )
        elif self.shape == "ellipse":
            rx, ry = self.size
            rect = pygame.Rect(
                screen_x - rx,
                screen_y - ry,
                rx * 2,
                ry * 2
            )
            pygame.draw.ellipse(
                screen,
                (255, 0, 0),
                rect,
                2
            )
