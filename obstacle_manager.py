import pygame
import random
from entities import Obstacle
from collider import Collider
import os

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

    def generate_obstacles_from_map(self, map_definition):
        self.placed_obstacles = []

        for obs_def in map_definition["obstacles"]:
            filename = obs_def["filename"]
            x = obs_def["x"]
            y = obs_def["y"]
            scale = obs_def["scale"]

            orig_image = self.obstacle_images[filename]
            new_width = int(orig_image.get_width() * scale)
            new_height = int(orig_image.get_height() * scale)
            scaled_image = pygame.transform.smoothscale(orig_image, (new_width, new_height))

            # ✅ 중심 좌표를 좌상단 좌표로 변환
            x -= new_width // 2
            y -= new_height // 2

            colliders = self._create_colliders_for_image(filename, new_width, new_height)

            if "Tree1" in filename or "Tree2" in filename:
                # cover collider (트리 전체 크기 기준)
                cover_collider = Collider(
                    shape="ellipse",
                    center=(new_width / 2, new_height / 2),
                    size=(new_width / 2, new_height / 2)
                )

                trunk_image = self.obstacle_images.get("TreeStump.png")

                if trunk_image:
                    trunk_scale = 0.35
                    trunk_width = int(new_width * trunk_scale)
                    trunk_height = int(new_height * trunk_scale)

                    trunk_image = pygame.transform.smoothscale(trunk_image, (trunk_width, trunk_height))

                obstacle = Obstacle(
                    scaled_image,
                    x,
                    y,
                    colliders,
                    image_filename=filename,
                    is_covering=True,
                    cover_collider=cover_collider,
                    trunk_image=trunk_image
                )
            else:
                obstacle = Obstacle(
                    scaled_image,
                    x,
                    y,
                    colliders,
                    image_filename=filename
                )

            self.placed_obstacles.append(obstacle)


    def _create_colliders_for_image(self, filename, w, h):
        colliders = []

        if "Pond1" in filename:
            rx = w * 0.27
            ry = h * 0.25
            colliders.append(
                Collider(
                    shape="ellipse",
                    center=(w / 2, h / 2),
                    size=(rx, ry),
                    bullet_passable=True
                )
            )
        elif "Pond2" in filename:
            rx = w * 0.27
            ry = h * 0.25
            colliders.append(
                Collider(
                    shape="ellipse",
                    center=(w / 2, h / 2),
                    size=(rx, ry),
                    bullet_passable=True
                )
            )
        elif "Rock1" in filename:
            rx = w * 0.27
            ry = h * 0.3
            colliders.append(
                Collider(
                    shape="ellipse",
                    center=(w / 2, h / 2),
                    size=(rx, ry),
                    bullet_passable=False
                )
            )
        elif "Rock2" in filename:
            rx = w * 0.43
            ry = h * 0.4
            colliders.append(
                Collider(
                    shape="ellipse",
                    center=(w / 2, h / 2),
                    size=(rx, ry),
                    bullet_passable=False
                )
            )
        elif "Rock3" in filename:
            rx = w * 0.45
            ry = h * 0.35
            colliders.append(
                Collider(
                    shape="ellipse",
                    center=(w / 2, h / 2),
                    size=(rx, ry),
                    bullet_passable=False
                )
            )
        elif "Tree1" in filename or "Tree2" in filename:
            radius = 0.15
            colliders.append(
                Collider(
                    shape="ellipse",
                    center=(w / 2, h / 2),
                    size=(w * radius, h * radius),
                    bullet_passable=False
                )
            )
        elif "FallenLog1" in filename:
            width = w * 0.3
            height = h * 0.7
            colliders.append(
                Collider(
                    shape="rectangle",
                    center=(w / 2, h / 2),
                    size=(width, height),
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
    
    def draw_non_trees(self, screen, world_offset_x, world_offset_y):
        for obs in self.placed_obstacles:
            if not obs.is_covering:
                obs.draw(screen, world_offset_x, world_offset_y)

    def draw_trees(self, screen, world_offset_x, world_offset_y, player_center, enemies):
        for obs in self.placed_obstacles:
            if obs.is_covering:
                obs.draw(screen, world_offset_x, world_offset_y, player_center, enemies)

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
                if collider.check_collision_circle(circle_center_world, circle_radius, (obs.world_x, obs.world_y)):
                    return True
        return False