import pygame
from entities import Obstacle
from collider import Collider
from config import PLAYER_VIEW_SCALE

class ObstacleManager:
    def __init__(self, obstacle_images, obstacle_masks, map_width, map_height,
                 min_scale=1.3, max_scale=2.0, num_obstacles_range=(1, 1)):
        # 장애물 관리 클래스 초기화
        self.obstacle_images = obstacle_images
        self.obstacle_masks = obstacle_masks
        self.map_width = map_width
        self.map_height = map_height
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.num_obstacles_range = num_obstacles_range
        self.placed_obstacles = []
        self.static_obstacles = []
        self.dynamic_obstacles = []
        self.combat_obstacles = []

    def generate_obstacles_from_map(self, map_definition):
        # 맵 정의에 따라 장애물 생성
        self.placed_obstacles = []

        for obs_def in map_definition["obstacles"]:
            filename = obs_def["filename"]
            x = obs_def["x"] * PLAYER_VIEW_SCALE
            y = obs_def["y"] * PLAYER_VIEW_SCALE
            scale = obs_def["scale"]

            orig_image = self.obstacle_images[filename]
            new_width = int(orig_image.get_width() * scale * PLAYER_VIEW_SCALE)
            new_height = int(orig_image.get_height() * scale * PLAYER_VIEW_SCALE)
            scaled_image = pygame.transform.smoothscale(orig_image, (new_width, new_height))

            x -= new_width // 2
            y -= new_height // 2

            colliders = self._create_colliders_for_image(filename, new_width, new_height)

            if "Tree1" in filename or "Tree2" in filename:
                # 나무일 경우 덮개(cover) 충돌체 추가
                cover_collider = Collider(
                    shape="ellipse",
                    center=(new_width / 2, new_height / 2),
                    size=(new_width / 2, new_height / 2)
                )

                trunk_image = self.obstacle_images.get("TreeStump.png")

                if trunk_image:
                    # 나무 밑둥 이미지 크기 조정
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
                # 일반 장애물 생성
                obstacle = Obstacle(
                    scaled_image,
                    x,
                    y,
                    colliders,
                    image_filename=filename
                )

            self.static_obstacles.append(obstacle)

    def _create_colliders_for_image(self, filename, w, h):
        # 장애물 종류에 따라 충돌체 생성
        colliders = []

        if "LavaPond1" in filename:
            rx = w * 0.45
            ry = h * 0.4
            colliders.append(Collider("ellipse", (w/2, h/2), (rx, ry), bullet_passable=True))
        elif "Pond1" in filename:
            rx = w * 0.27
            ry = h * 0.28
            colliders.append(Collider("ellipse", (w/2, h/2), (rx, ry), bullet_passable=True))
        elif "Pond2" in filename:
            rx = w * 0.32
            ry = h * 0.25
            colliders.append(Collider("ellipse", (w/2, h/2), (rx, ry), bullet_passable=True))
        elif "Rock1" in filename:
            rx = w * 0.35
            ry = h * 0.4
            colliders.append(Collider("ellipse", (w/2, h/2), (rx, ry), bullet_passable=False))
        elif "Rock2" in filename:
            rx = w * 0.43
            ry = h * 0.4
            colliders.append(Collider("ellipse", (w/2, h/2), (rx, ry), bullet_passable=False))
        elif "Rock3" in filename:
            rx = w * 0.34
            ry = h * 0.35
            colliders.append(Collider("ellipse", (w/2, h/2), (rx, ry), bullet_passable=False))
        elif "Tree1" in filename or "Tree2" in filename:
            radius = 0.15
            colliders.append(Collider("ellipse", (w/2, h/2), (w * radius, h * radius), bullet_passable=False))
        elif "FallenLog1" in filename:
            width = w * 0.3
            height = h * 0.7
            colliders.append(Collider("rectangle", (w/2, h/2), (width, height), bullet_passable=False))
        elif "FallenLog2" in filename:
            width = w * 0.7
            height = h * 0.3
            colliders.append(Collider("rectangle", (w/2, h/2), (width, height), bullet_passable=False))
        elif "Vehicle1" in filename:
            width = w * 0.65
            height = h * 0.9
            colliders.append(Collider("rectangle", (w/2, h/2), (width, height), bullet_passable=False))
        elif "Vehicle2" in filename:
            width = w * 0.95
            height = h * 0.7
            colliders.append(Collider("rectangle", (w/2, h/2), (width, height), bullet_passable=False))
        elif "Vehicle3" in filename:
            width = w * 0.4
            height = h * 0.8
            colliders.append(Collider("rectangle", (w/2, h/2), (width, height), bullet_passable=False))
        elif "Vehicle4" in filename:
            width = w * 0.82
            height = h * 0.36
            colliders.append(Collider("rectangle", (w/2, h/2), (width, height), bullet_passable=False))
        elif "Barricade1" in filename:
            width = w * 0.90
            height = h * 0.45
            colliders.append(Collider("rectangle", (w/2, h/2), (width, height), bullet_passable=False))
        elif "Dump1" in filename:
            width = w * 0.40
            height = h * 0.36
            colliders.append(Collider("ellipse", (w/2, h/2), (width, height), bullet_passable=False))
        elif "Dump2" in filename:
            width = w * 0.35
            height = h * 0.35
            colliders.append(Collider("ellipse", (w/2, h/2), (width, height), bullet_passable=False))
        elif "ElectricBox1" in filename:
            width = w * 0.70
            height = h * 0.70
            colliders.append(Collider("rectangle", (w/2, h/2), (width, height), bullet_passable=False))
        elif "FirePlug1" in filename:
            width = w * 0.28
            height = h * 0.28
            colliders.append(Collider("ellipse", (w/2, h/2), (width, height), bullet_passable=False))
        elif "Hole1" in filename:
            width = w * 0.23
            height = h * 0.23
            colliders.append(Collider("ellipse", (w/2, h/2), (width, height), bullet_passable=True))
        elif "TrashCan1" in filename:
            width = w * 0.70
            height = h * 0.70
            colliders.append(Collider("rectangle", (w/2, h/2), (width, height), bullet_passable=False))
        elif "Altar1" in filename:
            width = w * 0.72
            height = h * 0.72
            colliders.append(Collider("rectangle", (w/2, h/2), (width, height), bullet_passable=False))
        elif "Altar2" in filename:
            rx = w * 0.40
            ry = h * 0.40
            colliders.append(Collider("ellipse", (w/2, h/2), (rx, ry), bullet_passable=False))
        elif "BrokenStoneStatue1" in filename:
            width = w * 0.32
            height = h * 0.35
            colliders.append(Collider("ellipse", (w/2, h/2), (width, height), bullet_passable=True))
        elif "Coffin1" in filename:
            width = w * 0.45
            height = h * 0.78
            colliders.append(Collider("rectangle", (w/2, h/2), (width, height), bullet_passable=False))
        elif "Coffin2" in filename:
            width = w * 0.65
            height = h * 0.6
            colliders.append(Collider("rectangle", (w/2, h/2), (width, height), bullet_passable=False))
        elif "LavaStone1" in filename:
            rx = w * 0.40
            ry = h * 0.35
            colliders.append(Collider("ellipse", (w/2, h/2), (rx, ry), bullet_passable=False))
        elif "LavaStone2" in filename:
            rx = w * 0.40
            ry = h * 0.35
            colliders.append(Collider("ellipse", (w/2, h/2), (rx, ry), bullet_passable=False))
        elif "Skull1" in filename:
            rx = w * 0.4
            ry = h * 0.4
            colliders.append(Collider("ellipse", (w/2, h/2), (rx, ry), bullet_passable=False))
        elif "Skull2" in filename:
            rx = w * 0.4
            ry = h * 0.36
            colliders.append(Collider("ellipse", (w/2, h/2), (rx, ry), bullet_passable=False))
        elif "Skull3" in filename:
            rx = w * 0.35
            ry = h * 0.4
            colliders.append(Collider("ellipse", (w/2, h/2), (rx, ry), bullet_passable=False))
        else:
            colliders.append(Collider("rectangle", (w/2, h/2), (w * 0.80, h * 0.80), bullet_passable=False))

        return colliders

    def draw_non_trees(self, screen, world_offset_x, world_offset_y):
        # 나무가 아닌 장애물 그리기
        for obs in self.static_obstacles + self.combat_obstacles:
            if not obs.is_covering:
                obs.draw(screen, world_offset_x, world_offset_y)

    def draw_trees(self, screen, world_offset_x, world_offset_y, player_center, enemies):
        # 나무(덮개형) 장애물 그리기
        for obs in self.static_obstacles + self.combat_obstacles:
            if obs.is_covering:
                obs.draw(screen, world_offset_x, world_offset_y, player_center, enemies)

    def draw(self, screen, world_offset_x, world_offset_y):
        # 모든 장애물과 충돌체 디버그 표시
        for obs in self.static_obstacles + self.combat_obstacles:
            obs.draw(screen, world_offset_x, world_offset_y)
            for c in obs.colliders:
                c.draw(screen, world_offset_x, world_offset_y, (obs.world_x, obs.world_y))

    def check_collision_circle(self, circle_center_world, circle_radius):
        # 원형 충돌체가 장애물과 충돌했는지 체크
        all_obs = self.static_obstacles + self.combat_obstacles
        for obs in all_obs:
            for collider in obs.colliders:
                        collider_world_center = (
                            obs.world_x + collider.center[0],
                            obs.world_y + collider.center[1]
                        )
                        if collider.check_collision_circle(circle_center_world, circle_radius, (obs.world_x, obs.world_y)):
                            return True
        return False