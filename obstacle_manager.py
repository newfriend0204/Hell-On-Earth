import pygame
import random
from entities import Obstacle
from collider import Collider

class ObstacleManager:
    def __init__(self, obstacle_images, obstacle_masks, map_width, map_height,
                 min_scale=1.3, max_scale=2.0, num_obstacles_range=(1, 1)):
        self.obstacle_images = obstacle_images
        self.obstacle_masks = obstacle_masks
        self.map_width = map_width
        self.map_height = map_height
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.num_obstacles_range = num_obstacles_range

        self.placed_obstacles = []
        self.generate_obstacles()

    def generate_obstacles(self):
        # Map1 고정 배치 사용
        self.generate_obstacles_map1()

    def generate_obstacles_map1(self):
        self.placed_obstacles = []

        # -----------------------------
        # ① 중앙에 큰 연못
        # -----------------------------

        pond_filename = "Pond1.png"   # 네 asset 이름에 맞춰 변경해도 좋음
        orig_image = self.obstacle_images[pond_filename]

        scale_factor = 0.7
        new_width = int(orig_image.get_width() * scale_factor)
        new_height = int(orig_image.get_height() * scale_factor)

        scaled_image = pygame.transform.scale(orig_image, (new_width, new_height))

        pond_x = (self.map_width - new_width) // 2
        pond_y = (self.map_height - new_height) // 2

        colliders = self._create_colliders_for_image(
            pond_filename, new_width, new_height
        )

        pond_obstacle = Obstacle(scaled_image, pond_x, pond_y, colliders)
        self.placed_obstacles.append(pond_obstacle)

        # -----------------------------
        # ② 가장자리에 돌 6개
        # -----------------------------

        rock_filename = "Rock1.png"
        orig_image = self.obstacle_images[rock_filename]

        scale_factor = 1.5
        new_width = int(orig_image.get_width() * scale_factor)
        new_height = int(orig_image.get_height() * scale_factor)

        scaled_image = pygame.transform.scale(orig_image, (new_width, new_height))

        positions = [
            (50, 50),
            (self.map_width - new_width - 50, 50),
            (50, self.map_height - new_height - 50),
            (self.map_width - new_width - 50, self.map_height - new_height - 50),
            (self.map_width // 2 - new_width // 2, self.map_height - new_height - 50),
        ]

        for pos in positions:
            colliders = self._create_colliders_for_image(
                rock_filename, new_width, new_height
            )
            rock_obstacle = Obstacle(scaled_image, pos[0], pos[1], colliders)
            self.placed_obstacles.append(rock_obstacle)

    def _check_overlap(self, new_obstacle):
        for obs in self.placed_obstacles:
            for c1 in obs.colliders:
                for c2 in new_obstacle.colliders:
                    center1 = (obs.world_x + c1.center[0], obs.world_y + c1.center[1])
                    center2 = (new_obstacle.world_x + c2.center[0], new_obstacle.world_y + c2.center[1])
                    if c1.check_collision_circle(center2, c2.size if c2.shape == "circle" else max(c2.size)):
                        return True
        return False

    def _create_colliders_for_image(self, filename, w, h):
        colliders = []

        if "Pond1" in filename:
            rx = w * 0.3
            ry = h * 0.35
            colliders.append(
                Collider(
                    shape="ellipse",
                    center=(w / 2, h / 2),
                    size=(rx, ry),
                    bullet_passable=True
                )
            )
        elif "Pond2" in filename:
            rx = w * 0.45
            ry = h * 0.3
            colliders.append(
                Collider(
                    shape="ellipse",
                    center=(w / 2, h / 2),
                    size=(rx, ry),
                    bullet_passable=True
                )
            )
        elif "Rock1" in filename:
            rx = w * 0.5
            ry = h * 0.5
            colliders.append(
                Collider(
                    shape="ellipse",
                    center=(w / 2, h / 2),
                    size=(rx, ry),
                    bullet_passable=False
                )
            )
        elif "Rock2" in filename or "Rock3" in filename:
            rx = w * 0.4
            ry = h * 0.25
            colliders.append(
                Collider(
                    shape="ellipse",
                    center=(w / 2, h / 2),
                    size=(rx, ry),
                    bullet_passable=False
                )
            )
        else:
            r = min(w, h) * 0.4
            colliders.append(
                Collider(
                    shape="circle",
                    center=(w / 2, h / 2),
                    size=r
                )
            )

        return colliders

    def draw(self, screen, world_offset_x, world_offset_y):
        for obs in self.placed_obstacles:
            obs.draw(screen, world_offset_x, world_offset_y)
            for c in obs.colliders:
                c.draw(screen, world_offset_x, world_offset_y, (obs.world_x, obs.world_y))

    def check_collision_circle(self, circle_center_world, circle_radius):
        for obs in self.placed_obstacles:
            for collider in obs.colliders:
                collider_world_center = (
                    obs.world_x + collider.center[0],
                    obs.world_y + collider.center[1]
                )
                if collider.check_collision_circle(circle_center_world, circle_radius):
                    return True
        return False
