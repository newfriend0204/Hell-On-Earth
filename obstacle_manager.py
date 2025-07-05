import pygame
import random
from entities import Obstacle
from collider import Collider

class ObstacleManager:
    def __init__(self, obstacle_images, obstacle_masks, map_width, map_height,
                 min_scale=1.3, max_scale=2.0, num_obstacles_range=(5, 8)):
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
        num_obstacles = random.randint(*self.num_obstacles_range)
        attempt_limit = 500

        for _ in range(num_obstacles):
            attempts = 0
            while attempts < attempt_limit:
                filename = random.choice(list(self.obstacle_images.keys()))
                orig_image = self.obstacle_images[filename]

                scale_factor = random.uniform(self.min_scale, self.max_scale)

                orig_width = orig_image.get_width()
                orig_height = orig_image.get_height()

                new_width = int(orig_width * scale_factor)
                new_height = int(orig_height * scale_factor)

                scaled_image = pygame.transform.scale(orig_image, (new_width, new_height))

                rand_x = random.randint(0, self.map_width - new_width)
                rand_y = random.randint(0, self.map_height - new_height)

                colliders = self._create_colliders_for_image(
                    filename, new_width, new_height
                )

                obstacle = Obstacle(scaled_image, rand_x, rand_y, colliders)

                if not self._check_overlap(obstacle):
                    self.placed_obstacles.append(obstacle)
                    break
                else:
                    attempts += 1

            if attempts >= attempt_limit:
                print("Could not place obstacle after many attempts!")

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
            rx = w * 0.4
            ry = h * 0.25
            colliders.append(
                Collider(
                    shape="ellipse",
                    center=(w / 2, h / 2),
                    size=(rx, ry)
                )
            )
        elif "Pond2" in filename:
            rx = w * 0.45
            ry = h * 0.3
            colliders.append(
                Collider(
                    shape="ellipse",
                    center=(w / 2, h / 2),
                    size=(rx, ry)
                )
            )
        elif "Rock1" in filename:
            r = min(w, h) * 0.4
            colliders.append(
                Collider(
                    shape="circle",
                    center=(w / 2, h / 2),
                    size=r
                )
            )
        elif "Rock2" in filename or "Rock3" in filename:
            r = min(w, h) * 0.35
            colliders.append(
                Collider(
                    shape="circle",
                    center=(w / 2, h / 2),
                    size=r
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
