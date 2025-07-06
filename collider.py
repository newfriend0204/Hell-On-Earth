import pygame

class Collider:
    def __init__(self, shape, center, size, bullet_passable=False):
        self.shape = shape
        self.center = center
        self.size = size
        self.bullet_passable = bullet_passable

    def check_collision_circle(self, circle_center, circle_radius):
        if self.shape == "circle":
            dx = circle_center[0] - self.center[0]
            dy = circle_center[1] - self.center[1]
            dist_sq = dx * dx + dy * dy
            r_sum = circle_radius + self.size
            return dist_sq <= r_sum * r_sum

        elif self.shape == "ellipse":
            cx, cy = self.center
            rx, ry = self.size
            dx = circle_center[0] - cx
            dy = circle_center[1] - cy
            value = (dx * dx) / (rx * rx) + (dy * dy) / (ry * ry)
            return value <= 1.0

        elif self.shape == "rectangle":
            rect_x = self.center[0] - self.size[0] / 2
            rect_y = self.center[1] - self.size[1] / 2
            rect_w = self.size[0]
            rect_h = self.size[1]
            cx, cy = circle_center

            # Clamp circle center to rectangle bounds
            closest_x = max(rect_x, min(cx, rect_x + rect_w))
            closest_y = max(rect_y, min(cy, rect_y + rect_h))

            dx = cx - closest_x
            dy = cy - closest_y

            return (dx * dx + dy * dy) <= (circle_radius * circle_radius)

        return False

    def draw(self, screen, world_offset_x, world_offset_y, obstacle_world_pos):
        cx, cy = self.center
        world_cx = obstacle_world_pos[0] + cx
        world_cy = obstacle_world_pos[1] + cy
        screen_x = world_cx - world_offset_x
        screen_y = world_cy - world_offset_y
