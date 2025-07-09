import pygame
import math

class Collider:
    def __init__(self, shape, center, size, bullet_passable=False):
        self.shape = shape
        self.center = center
        self.size = size
        self.bullet_passable = bullet_passable

    def check_collision_circle(self, circle_center, circle_radius, obstacle_world_pos):
        cx, cy = obstacle_world_pos
        center_world_x = cx + self.center[0]
        center_world_y = cy + self.center[1]

        if self.shape == "circle":
            dx = circle_center[0] - center_world_x
            dy = circle_center[1] - center_world_y
            dist_sq = dx * dx + dy * dy
            r_sum = circle_radius + self.size
            return dist_sq <= r_sum * r_sum

        elif self.shape == "ellipse":
            rx, ry = self.size
            dx = circle_center[0] - center_world_x
            dy = circle_center[1] - center_world_y
            value = (dx * dx) / (rx * rx) + (dy * dy) / (ry * ry)
            return value <= 1.0

        elif self.shape == "rectangle":
            w, h = self.size
            rect_left = center_world_x - w / 2
            rect_top = center_world_y - h / 2

            closest_x = max(rect_left, min(circle_center[0], rect_left + w))
            closest_y = max(rect_top, min(circle_center[1], rect_top + h))

            dx = circle_center[0] - closest_x
            dy = circle_center[1] - closest_y
            return (dx * dx + dy * dy) <= (circle_radius * circle_radius)

        return False

    def draw(self, screen, offset_x, offset_y, obstacle_pos):
        color = (255, 0, 0)  # 빨간색 선

        # collider 중심 world좌표 계산w 
        cx, cy = obstacle_pos
        center_x = int(cx + self.center[0] - offset_x)
        center_y = int(cy + self.center[1] - offset_y)

        if self.shape == "ellipse":
            rx, ry = self.size
            rect = pygame.Rect(
                center_x - rx,
                center_y - ry,
                rx * 2,
                ry * 2
            )
            pygame.draw.ellipse(screen, color, rect, 2)

        elif self.shape == "circle":
            radius = int(self.size)
            pygame.draw.circle(screen, color, (center_x, center_y), radius, 2)

        elif self.shape == "rectangle":
            w, h = self.size
            rect = pygame.Rect(
                center_x - w // 2,
                center_y - h // 2,
                w,
                h
            )
            pygame.draw.rect(screen, color, rect, 2)
    
    def get_world_center(self, obstacle_world_pos):
        return (
            obstacle_world_pos[0] + self.center[0],
            obstacle_world_pos[1] + self.center[1]
        )
    
    def compute_penetration_circle(self, circle_center, circle_radius, obstacle_world_pos):
        cx, cy = obstacle_world_pos
        center_world_x = cx + self.center[0]
        center_world_y = cy + self.center[1]

        dx = circle_center[0] - center_world_x
        dy = circle_center[1] - center_world_y

        if self.shape == "circle":
            dist_sq = dx * dx + dy * dy
            r_sum = circle_radius + self.size
            if dist_sq < r_sum * r_sum:
                dist = math.sqrt(dist_sq) if dist_sq > 0 else 0.0001
                penetration = r_sum - dist
                return (
                    (dx / dist) * penetration,
                    (dy / dist) * penetration
                )
            else:
                return None

        elif self.shape == "ellipse":
            rx, ry = self.size
            value = (dx ** 2) / ((rx + circle_radius) ** 2) + \
                    (dy ** 2) / ((ry + circle_radius) ** 2)

            if value < 1.0:
                norm = math.sqrt(dx * dx + dy * dy)
                if norm == 0:
                    # 동일 좌표일 때 적당히 튕겨냄
                    return (1.0, 0.0)
                overlap_ratio = 1.0 - value
                penetration = overlap_ratio * (rx + ry) * 0.5 * 0.5
                if penetration < 0.5:
                    penetration = 0.5
                return (
                    (dx / norm) * penetration,
                    (dy / norm) * penetration
                )
            else:
                return None

        elif self.shape == "rectangle":
            w, h = self.size
            rect_left = center_world_x - w / 2
            rect_top = center_world_y - h / 2

            closest_x = max(rect_left, min(circle_center[0], rect_left + w))
            closest_y = max(rect_top, min(circle_center[1], rect_top + h))

            dx_rect = circle_center[0] - closest_x
            dy_rect = circle_center[1] - closest_y

            dist_sq = dx_rect ** 2 + dy_rect ** 2
            if dist_sq < circle_radius ** 2:
                dist = math.sqrt(dist_sq) if dist_sq > 0 else 0.0001
                penetration = circle_radius - dist
                if penetration < 0.5:
                    penetration = 0.5
                return (
                    (dx_rect / dist) * penetration,
                    (dy_rect / dist) * penetration
                )
            else:
                return None
        if penetration < 0.5:
            penetration = 0.5

        return None