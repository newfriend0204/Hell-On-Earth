import pygame
from config import *
import config
import math
from entities import Obstacle
from collider import Collider
import random

#맵의 가로/세로 타일 개수
WIDTH, HEIGHT = 8, 8
# 전투방(F) 최소 / 최대 개수
MIN_F_ROOMS = 8
MAX_F_ROOMS = 8

# 각 방의 상태를 저장하는 2차원 리스트
# 0: 빈 방(N)
# 1: 시작(S)
# 2: 미발견 끝방(E)
# 3: 발견된 끝방(E)
# 4: 미발견 전투방(F)
# 5: 발견된 전투방(F)
# 6: 클리어된 전투방(F)
# 7: 미발견 획득방(A)
# 8: 발견된 획득방(A)
# 9: 클리어된 끝방(E)
room_states = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

def apply_stage_room_settings(stage_data):
    global MIN_F_ROOMS, MAX_F_ROOMS
    MIN_F_ROOMS = stage_data.get("min_f_rooms", MIN_F_ROOMS)
    MAX_F_ROOMS = stage_data.get("max_f_rooms", MAX_F_ROOMS)
    return stage_data.get("acquire_rooms", 3)

def initialize_room_states(grid):
    # 생성된 맵의 문자(S, E, F, A, N)를 숫자 상태로 변환하여 room_states에 저장
    for y in range(HEIGHT):
        for x in range(WIDTH):
            cell = grid[y][x]
            if cell == 'N':
                room_states[y][x] = 0
            elif cell == 'S':
                room_states[y][x] = 1
            elif cell == 'E':
                room_states[y][x] = 2
            elif cell == 'F':
                room_states[y][x] = 4
            elif cell == 'A':
                room_states[y][x] = 7

def update_room_state_after_combat(y, x):
    # 전투 종료 후 해당 좌표의 전투방 상태를 '클리어'로 변경
    if room_states[y][x] in (4, 5):
        room_states[y][x] = 6
    elif room_states[y][x] in (2, 3):
        room_states[y][x] = 9

def reveal_neighbors(x, y, grid):
    # 현재 방의 상하좌우 인접방을 '발견' 상태로 변경
    for nx, ny in neighbors(x, y):
        if grid[ny][nx] == 'E' and room_states[ny][nx] == 2:
            room_states[ny][nx] = 3
        elif grid[ny][nx] == 'F' and room_states[ny][nx] == 4:
            room_states[ny][nx] = 5
        elif grid[ny][nx] == 'A' and room_states[ny][nx] == 7:
            room_states[ny][nx] = 8

def manhattan(p1, p2):
    # 맨해튼 거리 계산 (대각선 무시, x+y 차이의 절댓값 합)
    return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])

def get_map_dimensions():
    # 맵의 가로, 세로 크기를 반환
    return WIDTH, HEIGHT

def count_direction_changes(path):
    # 경로에서 방향이 몇 번 바뀌는지 계산
    changes = 0
    if len(path) < 2:
        return 0
    dx0 = path[1][0] - path[0][0]
    dy0 = path[1][1] - path[0][1]
    for i in range(2, len(path)):
        dx = path[i][0] - path[i-1][0]
        dy = path[i][1] - path[i-1][1]
        if (dx, dy) != (dx0, dy0):
            changes += 1
            dx0, dy0 = dx, dy
    return changes

def find_path(start, end):
    # 시작 지점에서 끝 지점까지 단순 경로 생성
    # 상하좌우로 한 칸씩 이동, 랜덤 우선순위 적용
    path = []
    x, y = start
    while (x, y) != end:
        moves = []
        if x < end[0]: moves.append((x+1, y))
        if x > end[0]: moves.append((x-1, y))
        if y < end[1]: moves.append((x, y+1))
        if y > end[1]: moves.append((x, y-1))
        random.shuffle(moves)
        for mx, my in moves:
            if (mx, my) != path[-1] if path else True:
                x, y = mx, my
                path.append((x, y))
                break
    return path

def neighbors(x, y):
    # 상하좌우 인접 좌표 목록 반환
    offsets = [(-1,0),(1,0),(0,-1),(0,1)]
    return [(x+dx, y+dy) for dx, dy in offsets
            if 0 <= x+dx < WIDTH and 0 <= y+dy < HEIGHT]

def find_end_room(grid):
    # E(보스방/종점) 좌표 반환.
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if grid[y][x] == 'E':
                return (x, y)
    return None

def find_boss_entry_room(grid):
    epos = find_end_room(grid)
    if not epos:
        return None
    ex, ey = epos
    for nx, ny in neighbors(ex, ey):
        if grid[ny][nx] == 'F':  # 보스방과 직접 연결된 전투방
            return (nx, ny)
    return None

def count_adjacent_fight(grid, ex, ey):
    # 특정 좌표 주변에 전투방이 몇 개 있는지 계산
    return sum(1 for nx, ny in neighbors(ex, ey) if grid[ny][nx] == 'F')

def expand_f_rooms(grid, f_positions, ex, ey, target_count):
    # 전투방(F) 개수를 목표치까지 확장하는 로직
    # E 방 주변은 전투방이 1개 이하가 되도록 제약
    attempts = 0
    while len(f_positions) < target_count and attempts < 1000:
        added = False
        new_candidates = []
        for fx, fy in f_positions:
            for nx, ny in neighbors(fx, fy):
                if grid[ny][nx] == 'N' and (nx, ny) != (ex, ey):
                    new_candidates.append((nx, ny))
        random.shuffle(new_candidates)
        for nx, ny in new_candidates:
            grid[ny][nx] = 'F'
            if count_adjacent_fight(grid, ex, ey) > 1:
                grid[ny][nx] = 'N'
                continue
            f_positions.append((nx, ny))
            added = True
            break
        if not added:
            break
        attempts += 1

def generate_map():
    # 전체 맵을 무작위로 생성하는 메인 함수
    # 1. S, E 위치 선택 (거리 제한 있음)
    # 2. S-E 경로 생성
    # 3. 경로에 전투방(F) 배치
    # 4. 목표 개수까지 전투방 확장
    # 5. 연결성 검사 후 성공 시 반환
    while True:
        grid = [['N']*WIDTH for _ in range(HEIGHT)]
        sx, sy = random.randint(2, 5), random.randint(2, 5)

        tries = 0
        while True:
            ex, ey = random.randint(1, WIDTH-2), random.randint(1, HEIGHT-2)
            dist = manhattan((sx, sy), (ex, ey))
            if 1 <= dist <= 6 and (sx, sy) != (ex, ey):
                break
            tries += 1
            if tries > 1000:
                continue

        path = find_path((sx, sy), (ex, ey))
        if count_direction_changes(path) < 3:
            continue

        grid[sy][sx] = 'S'
        grid[ey][ex] = 'E'
        f_positions = []

        for px, py in path:
            if grid[py][px] == 'N':
                grid[py][px] = 'F'
                f_positions.append((px, py))

        target_f_rooms = random.randint(MIN_F_ROOMS, MAX_F_ROOMS)
        expand_f_rooms(grid, f_positions, ex, ey, target_f_rooms)

        if len(f_positions) < target_f_rooms:
            continue

        visited = set()
        stack = [(sx, sy)]
        while stack:
            cx, cy = stack.pop()
            visited.add((cx, cy))
            for nx, ny in neighbors(cx, cy):
                if (nx, ny) not in visited and grid[ny][nx] in ('F', 'E'):
                    stack.append((nx, ny))

        all_f_reachable = all(pos in visited for pos in f_positions)
        if not all_f_reachable:
            continue
        

        # 디버그 - 보스 패턴 확인용
        # grid = [
        #     ['S', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        #     ['E', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        #     ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        #     ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        #     ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        #     ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        #     ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        #     ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N']
        # ]
        return grid
    
def place_acquire_rooms(grid, count=3):
    #Acquire 방(A) 배치
    candidates = []
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if grid[y][x] != 'N':
                continue
            # S, E와 인접하지 않게
            if any(grid[ny][nx] in ('S', 'E') for nx, ny in neighbors(x, y)):
                continue
            # F와 최소 한 칸 연결
            if not any(grid[ny][nx] == 'F' for nx, ny in neighbors(x, y)):
                continue
            candidates.append((x, y))
    random.shuffle(candidates)
    for i in range(min(count, len(candidates))):
        x, y = candidates[i]
        grid[y][x] = 'A'
        room_states[y][x] = 7
    return grid

def print_grid(grid):
    # 맵을 콘솔에 시각적으로 출력 (디버그용)
    SYMBOLS = {
        'N': '⬛',
        'S': '⬜',
        'E': '🟥',
        'F': '🟩',
        'A': '🟨'
    }
    for row in grid:
        print("".join(SYMBOLS.get(cell, ' ') for cell in row))

class World:
    # 게임 월드(맵) 관련 기능과 벽, 스폰포인트, 그리기 기능을 담당하는 클래스
    def __init__(
        self,
        background_image,
        crop_rect,
        PLAYER_VIEW_SCALE,
        BG_WIDTH,
        BG_HEIGHT,
        hole_width,
        hole_height,
        left_wall_width,
        top_wall_height,
        tunnel_length
    ):
        self.background_image = background_image
        self.PLAYER_VIEW_SCALE = PLAYER_VIEW_SCALE
        self.BG_WIDTH = BG_WIDTH
        self.BG_HEIGHT = BG_HEIGHT

        self.hole_width = hole_width
        self.hole_height = hole_height
        self.left_wall_width = left_wall_width
        self.top_wall_height = top_wall_height
        self.tunnel_length = tunnel_length

        self.crop_surface, self.effective_bg_width, self.effective_bg_height = \
            self.create_crop_surface(crop_rect)

        self.horizontal_tunnel_surface = self.create_horizontal_tunnel()
        self.vertical_tunnel_surface = self.create_vertical_tunnel()

    def create_crop_surface(self, crop_rect):
        # 맵 배경 이미지를 crop_rect 비율에 맞춰 잘라내거나 반복 타일링
        if crop_rect:
            x_ratio = crop_rect.get("x_ratio", 1.0)
            y_ratio = crop_rect.get("y_ratio", 1.0)

            crop_width = int(self.BG_WIDTH * x_ratio)
            crop_height = int(self.BG_HEIGHT * y_ratio)

            if x_ratio <= 1.0 and y_ratio <= 1.0:
                crop_surface = self.background_image.subsurface(
                    pygame.Rect(0, 0, crop_width, crop_height)
                ).copy()
            else:
                crop_surface = pygame.Surface((crop_width, crop_height))
                for ty in range(math.ceil(y_ratio)):
                    for tx in range(math.ceil(x_ratio)):
                        crop_surface.blit(
                            self.background_image,
                            (tx * self.BG_WIDTH, ty * self.BG_HEIGHT)
                        )
            return crop_surface, crop_width, crop_height
        else:
            scaled = pygame.transform.smoothscale(
                self.background_image,
                (
                    int(self.background_image.get_width() * self.PLAYER_VIEW_SCALE),
                    int(self.background_image.get_height() * self.PLAYER_VIEW_SCALE)
                )
            )
            return scaled, scaled.get_width(), scaled.get_height()

    def create_horizontal_tunnel(self):
        # 가로 방향 터널 이미지 생성 (왼쪽-오른쪽 연결 통로)
        tile_width = self.background_image.get_width()
        tunnel_surface = pygame.Surface((self.tunnel_length, self.hole_height), pygame.SRCALPHA)

        tiles_needed = math.ceil(self.tunnel_length / tile_width)
        for i in range(tiles_needed):
            tunnel_surface.blit(
                self.background_image,
                (i * tile_width, 0),
                area=pygame.Rect(0, self.top_wall_height, tile_width, self.hole_height)
            )
        return tunnel_surface

    def create_vertical_tunnel(self):
        # 세로 방향 터널 이미지 생성 (위-아래 연결 통로)
        tile_height = self.background_image.get_height()
        tunnel_surface = pygame.Surface((self.hole_width, self.tunnel_length), pygame.SRCALPHA)

        tiles_needed = math.ceil(self.tunnel_length / tile_height)
        for i in range(tiles_needed):
            tunnel_surface.blit(
                self.background_image,
                (0, i * tile_height),
                area=pygame.Rect(self.left_wall_width, 0, self.hole_width, tile_height)
            )
        return tunnel_surface

    def draw(self, screen, world_x, world_y, shake_offset_x, shake_offset_y):
        # 맵의 기본 배경과 터널을 화면에 그린다
        center_x = (self.tunnel_length // 2) - (self.hole_width // 2)
        center_y = (self.tunnel_length // 2) - (self.hole_height // 2)

        screen.blit(
            self.horizontal_tunnel_surface,
            (
                -center_x - world_x + shake_offset_x,
                self.top_wall_height - world_y + shake_offset_y
            )
        )

        screen.blit(
            self.vertical_tunnel_surface,
            (
                self.left_wall_width - world_x + shake_offset_x,
                -center_y - world_y + shake_offset_y
            )
        )

        screen.blit(
            self.crop_surface,
            (-world_x + shake_offset_x, -world_y + shake_offset_y)
        )

    def get_initial_position(self):
        # 플레이어 초기 카메라 위치를 반환
        return (
            (self.crop_surface.get_width() // 2) - (SCREEN_WIDTH // 2),
            (self.crop_surface.get_height() // 2) - (SCREEN_HEIGHT // 2)
        )
    
    def get_spawn_point(self, direction, margin=0, is_start_map=False):
        # 방 입장 시 플레이어 스폰 위치 계산
        if is_start_map or direction is None:
            return (self.effective_bg_width / 2, self.effective_bg_height / 2)

        if direction == "north":
            x = self.left_wall_width + self.hole_width / 2
            y = -margin
        elif direction == "south":
            x = self.left_wall_width + self.hole_width / 2
            y = self.effective_bg_height + margin
        elif direction == "west":
            x = -margin
            y = self.top_wall_height + self.hole_height / 2
        elif direction == "east":
            x = self.effective_bg_width + margin
            y = self.top_wall_height + self.hole_height / 2
        else:
            x = self.effective_bg_width / 2
            y = self.effective_bg_height / 2

        return (x, y)

    def generate_walls(self, map_width, map_height, wall_thickness, 
                    hole_width, hole_height,
                    left_wall_width, right_wall_width, 
                    top_wall_height, bottom_wall_height,
                    north_hole_open, south_hole_open,
                    west_hole_open, east_hole_open,
                    expansion, invisible_wall_filename="invisible_wall", extra_wall_size=2000):
        # 맵 경계와 통로 막힘 여부에 따라 벽 오브젝트 생성
        # invisible_wall_filename은 충돌만 있고 보이지 않는 벽

        walls = []
        extra_wall_size *= self.PLAYER_VIEW_SCALE
        expansion_extension = 300 * self.PLAYER_VIEW_SCALE

        def rect_obstacle(size, world_x, world_y):
            surface = pygame.Surface(size, pygame.SRCALPHA)
            collider = Collider(
                shape="rectangle",
                center=(size[0]/2, size[1]/2),
                size=size,
                bullet_passable=False
            )
            return Obstacle(
                surface,
                world_x=world_x,
                world_y=world_y,
                colliders=[collider],
                image_filename=invisible_wall_filename,
            )

        walls.append(rect_obstacle((left_wall_width, wall_thickness), 0, -wall_thickness))
        walls.append(rect_obstacle((right_wall_width, wall_thickness), map_width - right_wall_width, -wall_thickness))
        if not north_hole_open:
            walls.append(rect_obstacle(
                (hole_width, wall_thickness + extra_wall_size),
                left_wall_width,
                -wall_thickness - extra_wall_size
            ))

        walls.append(rect_obstacle((left_wall_width, wall_thickness), 0, map_height))
        walls.append(rect_obstacle((right_wall_width, wall_thickness), map_width - right_wall_width, map_height))
        if not south_hole_open:
            walls.append(rect_obstacle(
                (hole_width, wall_thickness + extra_wall_size),
                left_wall_width,
                map_height
            ))

        walls.append(rect_obstacle((wall_thickness, top_wall_height), -wall_thickness, 0))
        walls.append(rect_obstacle((wall_thickness, bottom_wall_height), -wall_thickness, map_height - bottom_wall_height))
        if not west_hole_open:
            walls.append(rect_obstacle(
                (wall_thickness + extra_wall_size, hole_height),
                -wall_thickness - extra_wall_size,
                top_wall_height
            ))

        walls.append(rect_obstacle((wall_thickness, top_wall_height), map_width, 0))
        walls.append(rect_obstacle((wall_thickness, bottom_wall_height), map_width, map_height - bottom_wall_height))
        if not east_hole_open:
            walls.append(rect_obstacle(
                (wall_thickness + extra_wall_size, hole_height),
                map_width,
                top_wall_height
            ))

        walls.append(rect_obstacle(
            (left_wall_width + expansion_extension, expansion),
            0 - expansion_extension,
            -expansion
        ))
        walls.append(rect_obstacle(
            (right_wall_width + expansion_extension, expansion),
            map_width - right_wall_width,
            -expansion
        ))

        walls.append(rect_obstacle(
            (left_wall_width + expansion_extension, expansion),
            0 - expansion_extension,
            map_height
        ))
        walls.append(rect_obstacle(
            (right_wall_width + expansion_extension, expansion),
            map_width - right_wall_width,
            map_height
        ))

        walls.append(rect_obstacle(
            (expansion, top_wall_height + expansion_extension),
            -expansion,
            0 - expansion_extension
        ))
        walls.append(rect_obstacle(
            (expansion, bottom_wall_height + expansion_extension),
            -expansion,
            map_height - bottom_wall_height
        ))

        walls.append(rect_obstacle(
            (expansion, top_wall_height + expansion_extension),
            map_width,
            0 - expansion_extension
        ))
        walls.append(rect_obstacle(
            (expansion, bottom_wall_height + expansion_extension),
            map_width,
            map_height - bottom_wall_height
        ))

        return walls

    def draw_wall_barriers(self, screen, world_x, world_y, combat_walls_info):
            # 전투 중 통로를 막는 벽(이미지)을 애니메이션으로 이동시켜 그림
            if not config.combat_state and not combat_walls_info:
                return

            walls_to_remove = []

            for info in combat_walls_info:
                img = info["image"]
                tx, ty = info["target_pos"]
                cx, cy = info["current_pos"]

                smoothing = 0.2
                new_x = cx + (tx - cx) * smoothing
                new_y = cy + (ty - cy) * smoothing

                if abs(new_x - tx) < 1 and abs(new_y - ty) < 1:
                    new_x = tx
                    new_y = ty
                    if info.get("state") == "hiding":
                        walls_to_remove.append(info)

                info["current_pos"] = (new_x, new_y)

                screen_x = new_x - world_x
                screen_y = new_y - world_y
                screen.blit(img, (screen_x, screen_y))

            for info in walls_to_remove:
                combat_walls_info.remove(info)

    def draw_invisible_walls(self, screen, world_x, world_y, obstacle_manager):
        # 디버그용: invisible_wall 오브젝트를 검정색으로 화면에 표시
        black_color = (0, 0, 0)

        for obs in obstacle_manager.static_obstacles + obstacle_manager.combat_obstacles:
            if obs.image_filename != "invisible_wall":
                continue

            if obs.world_x == 0 and obs.world_y == 0:
                continue

            rect = pygame.Rect(
                obs.world_x - world_x,
                obs.world_y - world_y,
                obs.image.get_width(),
                obs.image.get_height()
            )
            pygame.draw.rect(screen, black_color, rect)

    def draw_full(self, screen, world_x, world_y, shake_offset_x, shake_offset_y,
                combat_walls_info, obstacle_manager, expansion):
        # draw() + 전투벽 + 투명벽을 모두 그리는 함수
        self.draw(screen, world_x, world_y, shake_offset_x, shake_offset_y)

        clip_rect = pygame.Rect(
            -expansion,
            -expansion,
            self.effective_bg_width + expansion * 3,
            self.effective_bg_height + expansion * 3
        )
        screen.set_clip(clip_rect)

        self.draw_wall_barriers(screen, world_x - shake_offset_x, world_y - shake_offset_y, combat_walls_info)
        self.draw_invisible_walls(screen, world_x - shake_offset_x, world_y - shake_offset_y, obstacle_manager)

        screen.set_clip(None)

    def generate_thin_combat_walls(
        self,
        left_wall_width,
        top_wall_height,
        hole_width,
        hole_height,
        wall_thickness=10 * PLAYER_VIEW_SCALE
    ):
        # 전투 시작 시 플레이어 이동을 막는 얇은 충돌 벽 생성
        thin = wall_thickness
        effective_width = self.effective_bg_width
        effective_height = self.effective_bg_height

        adjust_x = (effective_width - hole_width) / 2 - left_wall_width
        adjust_y = (effective_height - hole_height) / 2 - top_wall_height

        combat_walls = []
        combat_walls.append(Obstacle(
            pygame.Surface((hole_width, thin), pygame.SRCALPHA),
            world_x=left_wall_width + adjust_x,
            world_y=0 - thin,
            colliders=[Collider("rectangle", (hole_width / 2, thin / 2), (hole_width, thin), False)],
            image_filename="combat_invisible_wall"
        ))

        combat_walls.append(Obstacle(
            pygame.Surface((hole_width, thin), pygame.SRCALPHA),
            world_x=left_wall_width + adjust_x,
            world_y=effective_height,
            colliders=[Collider("rectangle", (hole_width / 2, thin / 2), (hole_width, thin), False)],
            image_filename="combat_invisible_wall"
        ))

        combat_walls.append(Obstacle(
            pygame.Surface((thin, hole_height), pygame.SRCALPHA),
            world_x=0 - thin,
            world_y=top_wall_height + adjust_y,
            colliders=[Collider("rectangle", (thin / 2, hole_height / 2), (thin, hole_height), False)],
            image_filename="combat_invisible_wall"
        ))

        combat_walls.append(Obstacle(
            pygame.Surface((thin, hole_height), pygame.SRCALPHA),
            world_x=effective_width,
            world_y=top_wall_height + adjust_y,
            colliders=[Collider("rectangle", (thin / 2, hole_height / 2), (thin, hole_height), False)],
            image_filename="combat_invisible_wall"
        ))

        return combat_walls