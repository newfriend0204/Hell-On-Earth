import pygame
from config import *
import config
import math
from entities import Obstacle
from collider import Collider
import random

WIDTH, HEIGHT = 8, 8
MIN_F_ROOMS = 8
MAX_F_ROOMS = 8

def manhattan(p1, p2):
    return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])

def get_map_dimensions():
    return WIDTH, HEIGHT

def find_path(start, end):
    path = []
    x, y = start
    while (x, y) != end:
        moves = []
        if x < end[0]:
            moves.append((x+1, y))
        elif x > end[0]:
            moves.append((x-1, y))
        if y < end[1]:
            moves.append((x, y+1))
        elif y > end[1]:
            moves.append((x, y-1))
        if not moves:
            break
        x, y = random.choice(moves)
        path.append((x, y))
    return path

def neighbors(x, y):
    offsets = [(-1,0),(1,0),(0,-1),(0,1)]
    return [(x+dx, y+dy) for dx, dy in offsets
            if 0 <= x+dx < WIDTH and 0 <= y+dy < HEIGHT]

def count_adjacent_fight(grid, ex, ey):
    count = 0
    for nx, ny in neighbors(ex, ey):
        if grid[ny][nx] == 'F':
            count += 1
    return count

def generate_map():
    grid = [['N']*WIDTH for _ in range(HEIGHT)]
    min_distance = MIN_F_ROOMS - 1
    max_distance = MAX_F_ROOMS - 1

    while True:
        sx, sy = random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)
        tries = 0
        while True:
            ex, ey = random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)
            dist = manhattan((sx, sy), (ex, ey))
            if min_distance <= dist <= max_distance and (sx, sy) != (ex, ey):
                break
            tries += 1
            if tries > 1000:
                sx, sy = random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)
                tries = 0

        path = find_path((sx, sy), (ex, ey))
        grid = [['N']*WIDTH for _ in range(HEIGHT)]
        grid[sy][sx] = 'S'
        grid[ey][ex] = 'E'
        f_positions = []
        for px, py in path:
            if grid[py][px] == 'N':
                grid[py][px] = 'F'
                f_positions.append((px, py))

        total_f_needed = max(MIN_F_ROOMS, min(MAX_F_ROOMS, len(f_positions)))
        total_f_needed = max(total_f_needed, MIN_F_ROOMS)

        if len(f_positions) < total_f_needed:
            available = []
            for fx, fy in f_positions:
                for nx, ny in neighbors(fx, fy):
                    if grid[ny][nx] == 'N' and (nx, ny) != (ex, ey):
                        available.append((nx, ny))
            random.shuffle(available)
            for nx, ny in available:
                if len(f_positions) >= total_f_needed:
                    break
                grid[ny][nx] = 'F'
                if count_adjacent_fight(grid, ex, ey) > 1:
                    grid[ny][nx] = 'N'
                else:
                    f_positions.append((nx, ny))

        visited = set()
        stack = [(sx, sy)]
        while stack:
            cx, cy = stack.pop()
            visited.add((cx, cy))
            for nx, ny in neighbors(cx, cy):
                if (nx, ny) not in visited and grid[ny][nx] in ('F', 'E'):
                    stack.append((nx, ny))
        all_f_reachable = all(pos in visited for pos in f_positions)
        if all_f_reachable and len(f_positions) >= MIN_F_ROOMS:
            break
    return grid

def print_grid(grid):
    SYMBOLS = {
        'N': '⬛',
        'S': '⬜',
        'E': '🟥',
        'F': '🟩',
    }
    for row in grid:
        print("".join(SYMBOLS.get(cell, ' ') for cell in row))

class World:
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
        return (
            (self.crop_surface.get_width() // 2) - (SCREEN_WIDTH // 2),
            (self.crop_surface.get_height() // 2) - (SCREEN_HEIGHT // 2)
        )
    
    def get_spawn_point(self, direction, margin=0, is_start_map=False):
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