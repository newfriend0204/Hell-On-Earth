import random
import pygame
from config import *
from obstacle_manager import ObstacleManager
from maps import MAPS
from collections import deque

class Room:
    def __init__(self, room_type, grid_x, grid_y, world_x, world_y, size_x, size_y):
        self.room_type = room_type  # 'S', 'E', 'F', 'N'
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.world_x = world_x
        self.world_y = world_y
        self.size_x = size_x
        self.size_y = size_y
        self.connected_paths = {}  # {'N': Pathway, ...}
        self.obstacle_manager = None
        self.map_data = None
        self.enemies = []
        self.background_surface = None

    def generate_obstacles(self, images, map_data):
        self.obstacle_manager = ObstacleManager(
            obstacle_images=images["obstacles"],
            obstacle_masks=images["obstacle_masks"],
            map_width=self.size_x,
            map_height=self.size_y,
            min_scale=1.3,
            max_scale=2.0,
            num_obstacles_range=(5, 8)
        )
        self.obstacle_manager.generate_obstacles_from_map(map_data)
        self.map_data = map_data

    def draw(self, screen, world_offset_x, world_offset_y, player_center):
        if self.background_surface:
            screen.blit(
                self.background_surface,
                (-world_offset_x, -world_offset_y)
            )
        if self.obstacle_manager:
            self.obstacle_manager.draw_non_trees(screen, world_offset_x, world_offset_y)
            self.obstacle_manager.draw_trees(screen, world_offset_x, world_offset_y, player_center, [])

class Pathway:
    def __init__(self, direction, rect, texture_surface):
        self.direction = direction  # 'N', 'S', 'E', 'W'
        self.rect = rect
        self.texture_surface = texture_surface

    def draw(self, screen, world_offset_x, world_offset_y):
        screen.blit(
            self.texture_surface,
            (self.rect.x - world_offset_x, self.rect.y - world_offset_y)
        )

class World:
    def __init__(self, images, sounds):
        self.images = images
        self.sounds = sounds
        self.grid_size = 8
        self.room_size_x = int(400 * PLAYER_VIEW_SCALE)
        self.room_size_y = int(400 * PLAYER_VIEW_SCALE)
        self.rooms = {}
        self.current_room = None
        self.player_spawn_pos = (0, 0)
        self.f_room_map_assignments = {}   # (x, y) -> chosen_map

    def generate_map(self):
        grid_size = self.grid_size
        grid = [['N' for _ in range(grid_size)] for _ in range(grid_size)]

        # -------------------------------
        # 1. S, E 좌표 결정
        # -------------------------------
        weighted_coords = []
        for y in range(grid_size):
            for x in range(grid_size):
                center_dist = max(abs(x - grid_size // 2), abs(y - grid_size // 2))
                weight = max(1, (grid_size // 2 - center_dist + 1))
                weighted_coords.extend([(x, y)] * weight)

        found = False
        for _ in range(300):
            sx, sy = random.choice(weighted_coords)
            ex, ey = random.choice(weighted_coords)
            if (sx, sy) == (ex, ey):
                continue
            dist = abs(sx - ex) + abs(sy - ey)
            if 3 <= dist <= 5:
                found = True
                break
        if not found:
            raise Exception("No suitable S,E positions found")

        grid[sy][sx] = 'S'
        grid[ey][ex] = 'E'

        # -------------------------------
        # 2. BFS로 S→E 경로 만들기
        # -------------------------------
        visited = [[False] * grid_size for _ in range(grid_size)]
        parent = [[None] * grid_size for _ in range(grid_size)]

        q = deque()
        q.append((sx, sy))
        visited[sy][sx] = True

        while q:
            cx, cy = q.popleft()
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    if not visited[ny][nx]:
                        visited[ny][nx] = True
                        parent[ny][nx] = (cx, cy)
                        q.append((nx, ny))

        # 역추적
        path = []
        cx, cy = ex, ey
        while (cx, cy) != (sx, sy):
            path.append((cx, cy))
            cx, cy = parent[cy][cx]

        # 경로에 F 배치
        path_f_coords = []
        for px, py in path:
            if grid[py][px] == 'N':
                grid[py][px] = 'F'
                path_f_coords.append((px, py))

        # -------------------------------
        # 3. 추가 F 배치 (최대 6칸)
        # -------------------------------
        all_f_coords = set(path_f_coords)
        while len(all_f_coords) < 6:
            candidates = []
            for fx, fy in all_f_coords.union({(sx, sy)}):
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nx, ny = fx + dx, fy + dy
                    if 0 <= nx < grid_size and 0 <= ny < grid_size:
                        if grid[ny][nx] == 'N':
                            candidates.append((nx, ny))
            if not candidates:
                break
            nx, ny = random.choice(candidates)
            grid[ny][nx] = 'F'
            all_f_coords.add((nx, ny))

        # -------------------------------
        # 4. E가 F와 1면만 맞닿도록 수정
        # -------------------------------
        e_neighbors = []
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = ex + dx, ey + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size:
                if grid[ny][nx] == 'F':
                    e_neighbors.append((nx, ny))
        if len(e_neighbors) > 1:
            keep = random.choice(e_neighbors)
            for nx, ny in e_neighbors:
                if (nx, ny) != keep:
                    grid[ny][nx] = 'N'
                    all_f_coords.discard((nx, ny))

        # -------------------------------
        # 5. 모든 F가 S로 도달 가능한지 검사
        # -------------------------------
        visited = set()
        q = deque()
        q.append((sx, sy))
        visited.add((sx, sy))

        while q:
            cx, cy = q.popleft()
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    if (nx, ny) not in visited:
                        if grid[ny][nx] in ('F', 'S'):
                            visited.add((nx, ny))
                            q.append((nx, ny))
        for fx, fy in all_f_coords:
            if (fx, fy) not in visited:
                grid[fy][fx] = 'N'

        # -------------------------------
        # 6. Room 생성
        # -------------------------------
        for y in range(grid_size):
            for x in range(grid_size):
                if grid[y][x] != 'N':
                    world_x = x * self.room_size_x
                    world_y = y * self.room_size_y
                    room = Room(grid[y][x], x, y, world_x, world_y, self.room_size_x, self.room_size_y)

                    if room.room_type in ('S', 'E'):
                        # crop_rect 읽기
                        crop_rect_data = MAPS[0]["crop_rect"] if MAPS else {"x_ratio": 1.0, "y_ratio": 1.0}
                        x_ratio = crop_rect_data.get("x_ratio", 1.0)
                        y_ratio = crop_rect_data.get("y_ratio", 1.0)

                        bg_surface = self.images["background"]

                        crop_width = int(bg_surface.get_width() * x_ratio)
                        crop_height = int(bg_surface.get_height() * y_ratio)

                        # 자르기
                        cropped_bg = bg_surface.subsurface(pygame.Rect(0, 0, crop_width, crop_height))

                        # 스케일링
                        scaled_bg = pygame.transform.smoothscale(
                            cropped_bg,
                            (self.room_size_x, self.room_size_y)
                        )

                        room.background_surface = scaled_bg
                    elif room.room_type == 'F':
                        if (x, y) in self.f_room_map_assignments:
                            chosen_map = self.f_room_map_assignments[(x, y)]
                        else:
                            chosen_map = random.choice(MAPS)
                            self.f_room_map_assignments[(x, y)] = chosen_map

                        room.generate_obstacles(self.images, chosen_map)

                    self.rooms[(x, y)] = room

        if (sx, sy) not in self.rooms:
            raise Exception(f"Start room S not found in self.rooms at ({sx}, {sy})")

        self.current_room = self.rooms[(sx, sy)]
        self.player_spawn_pos = (
            self.current_room.world_x + self.room_size_x // 2,
            self.current_room.world_y + self.room_size_y // 2
        )

        # -------------------------------
        # 7. Pathway 생성
        # -------------------------------
        for (x, y), room in self.rooms.items():
            for dir_name, (dx, dy) in {
                'N': (0, -1),
                'S': (0, 1),
                'W': (-1, 0),
                'E': (1, 0)
            }.items():
                neighbor_pos = (x + dx, y + dy)
                if neighbor_pos in self.rooms:
                    neighbor_room = self.rooms[neighbor_pos]
                    if dir_name in room.connected_paths:
                        continue
                    scaled_size = int(200 * PLAYER_VIEW_SCALE)

                    if dir_name == 'N':
                        path_rect = pygame.Rect(
                            int(room.world_x + (room.size_x - scaled_size) // 2),
                            int(room.world_y),
                            scaled_size,
                            scaled_size
                        )
                    elif dir_name == 'S':
                        path_rect = pygame.Rect(
                            int(room.world_x + (room.size_x - scaled_size) // 2),
                            int(room.world_y + room.size_y - scaled_size),
                            scaled_size,
                            scaled_size
                        )
                    elif dir_name == 'W':
                        path_rect = pygame.Rect(
                            int(room.world_x),
                            int(room.world_y + (room.size_y - scaled_size) // 2),
                            scaled_size,
                            scaled_size
                        )
                    elif dir_name == 'E':
                        path_rect = pygame.Rect(
                            int(room.world_x + room.size_x - scaled_size),
                            int(room.world_y + (room.size_y - scaled_size) // 2),
                            scaled_size,
                            scaled_size
                        )

                    green_surface = pygame.Surface((scaled_size, scaled_size))
                    green_surface.fill((0, 255, 0))

                    path = Pathway(dir_name, path_rect, green_surface)
                    room.connected_paths[dir_name] = path

                    # 반대편에도 연결
                    opposite_dir = {'N': 'S', 'S': 'N', 'W': 'E', 'E': 'W'}[dir_name]
                    neighbor_room.connected_paths[opposite_dir] = Pathway(
                        opposite_dir,
                        path_rect.copy(),
                        green_surface
                    )

        self.print_map_diagram(grid)

    def print_map_diagram(self, grid):
        symbols = {
            'N': '⬛',
            'S': '🟦',
            'E': '🟥',
            'F': '🟩'
        }
        for row in grid:
            print("".join(symbols.get(cell, '?') for cell in row))

    def draw(self, screen, player_center):
        world_offset_x = self.current_room.world_x
        world_offset_y = self.current_room.world_y

        for room in self.rooms.values():
            for path in room.connected_paths.values():
                path.draw(screen, world_offset_x, world_offset_y)
        self.current_room.draw(screen, world_offset_x, world_offset_y, player_center)

    def check_pathway_collision(self, player_center):
        for path in self.current_room.connected_paths.values():
            if path.rect.collidepoint(player_center):
                return path
        return None

    def move_to_room(self, path):
        dx, dy = 0, 0
        if path.direction == 'N':
            dy = -1
        elif path.direction == 'S':
            dy = 1
        elif path.direction == 'W':
            dx = -1
        elif path.direction == 'E':
            dx = 1

        new_pos = (self.current_room.grid_x + dx, self.current_room.grid_y + dy)
        if new_pos in self.rooms:
            self.current_room = self.rooms[new_pos]
            print(f"[DEBUG] 방 이동 → {new_pos}")
            self.spawn_player_in_room(path.direction)

    def spawn_player_in_room(self, from_direction):
        offset_x, offset_y = 0, 0
        margin = 20
        if from_direction == 'N':
            offset_y = self.room_size_y - margin
            offset_x = self.room_size_x // 2
        elif from_direction == 'S':
            offset_y = margin
            offset_x = self.room_size_x // 2
        elif from_direction == 'W':
            offset_x = self.room_size_x - margin
            offset_y = self.room_size_y // 2
        elif from_direction == 'E':
            offset_x = margin
            offset_y = self.room_size_y // 2

        self.player_spawn_pos = (
            self.current_room.world_x + offset_x,
            self.current_room.world_y + offset_y
        )

    def get_player_spawn(self):
        return self.player_spawn_pos
