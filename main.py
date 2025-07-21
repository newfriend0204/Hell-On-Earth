import pygame
import math
import random
from config import *
import config
from asset_manager import load_images
from sound_manager import load_sounds
from entities import Bullet, ScatteredBullet, ScatteredBlood
from collider import Collider
from renderer_3d import Renderer3D
from obstacle_manager import ObstacleManager
from ai import Enemy1, Enemy2
from world import World, generate_map, print_grid, get_map_dimensions
from maps import MAPS, FIGHT_MAPS

CURRENT_MAP = MAPS[0]

grid = generate_map()
print_grid(grid)

pygame.init()
pygame.font.init()
pygame.mixer.init()

DEBUG_FONT = pygame.font.SysFont('malgungothic', 24)

pygame.mouse.set_visible(False)

#screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hell On Earth")

images = load_images()
sounds = load_sounds()

original_player_image = images["player"]
original_gun_image_1 = images["gun1"]
original_gun_image_2 = images["gun2"]
original_gun_image_3 = images["gun3"]
original_bullet_image = images["bullet1"]
original_cartridge_image = images["cartridge_case1"]
cursor_image = images["cursor"]
background_image = images["background"]
background_rect = background_image.get_rect()

obstacle_manager = ObstacleManager(
    obstacle_images=images["obstacles"],
    obstacle_masks=images["obstacle_masks"],
    map_width=BG_WIDTH,
    map_height=BG_HEIGHT,
    min_scale=1.3,
    max_scale=2.0,
    num_obstacles_range=(5, 8)
)
obstacle_manager.generate_obstacles_from_map(CURRENT_MAP)

s_pos = None
for y, row in enumerate(grid):
    for x, cell in enumerate(row):
        if cell == 'S':
            s_pos = (x, y)
            break
    if s_pos:
        break
current_room_pos = list(s_pos)

north_hole_open = False
south_hole_open = False
west_hole_open = False
east_hole_open = False

sx, sy = s_pos
WIDTH, HEIGHT = get_map_dimensions()

if sy > 0:
    if grid[sy - 1][sx] != 'N':
        north_hole_open = True

if sy < HEIGHT - 1:
    if grid[sy + 1][sx] != 'N':
        south_hole_open = True

if sx > 0:
    if grid[sy][sx - 1] != 'N':
        west_hole_open = True

if sx < WIDTH - 1:
    if grid[sy][sx + 1] != 'N':
        east_hole_open = True

expansion = 350 * PLAYER_VIEW_SCALE

hole_width = 300 * PLAYER_VIEW_SCALE
hole_height = 300 * PLAYER_VIEW_SCALE

wall_thickness = 10 * PLAYER_VIEW_SCALE

world = World(
    background_image=background_image,
    crop_rect=CURRENT_MAP.get("crop_rect"),
    PLAYER_VIEW_SCALE=PLAYER_VIEW_SCALE,
    BG_WIDTH=BG_WIDTH,
    BG_HEIGHT=BG_HEIGHT,
    hole_width=hole_width,
    hole_height=hole_height,
    left_wall_width=0,
    top_wall_height=0,
    tunnel_length=10000 * PLAYER_VIEW_SCALE
)

effective_bg_width = world.effective_bg_width
effective_bg_height = world.effective_bg_height

map_width = effective_bg_width
map_height = effective_bg_height

left_wall_width = (map_width / 2) - (hole_width / 2)
right_wall_width = left_wall_width
top_wall_height = (map_height / 2) - (hole_height / 2)
bottom_wall_height = top_wall_height

world.left_wall_width = left_wall_width
world.top_wall_height = top_wall_height

if CURRENT_MAP is MAPS[0]:
    player_world_x, player_world_y = world.get_spawn_point(
        direction=None,
        is_start_map=True
    )
else:
    spawn_direction = "west"
    player_world_x, player_world_y = world.get_spawn_point(
        spawn_direction,
        margin=50
    )

world_x = player_world_x - SCREEN_WIDTH // 2
world_y = player_world_y - SCREEN_HEIGHT // 2

walls = world.generate_walls(
    map_width=map_width,
    map_height=map_height,
    wall_thickness=wall_thickness,
    hole_width=hole_width,
    hole_height=hole_height,
    left_wall_width=left_wall_width,
    right_wall_width=right_wall_width,
    top_wall_height=top_wall_height,
    bottom_wall_height=bottom_wall_height,
    north_hole_open=north_hole_open,
    south_hole_open=south_hole_open,
    west_hole_open=west_hole_open,
    east_hole_open=east_hole_open,
    expansion=expansion,
)
obstacle_manager.static_obstacles.extend(walls)
combat_walls_info = []
combat_walls = []

player_rect = original_player_image.get_rect(
    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
)

gun_canvas_size = original_gun_image_1.get_size()
gun_canvas = pygame.Surface(gun_canvas_size, pygame.SRCALPHA)

world_vx = 0
world_vy = 0

acceleration_rate = 0.8 * PLAYER_VIEW_SCALE
deceleration_rate = 0.9 * PLAYER_VIEW_SCALE

normal_max_speed = NORMAL_MAX_SPEED * PLAYER_VIEW_SCALE
sprint_max_speed = SPRINT_MAX_SPEED * PLAYER_VIEW_SCALE

move_left = move_right = move_up = move_down = False

max_speed = normal_max_speed
allow_sprint = True
recoil_in_progress = False

changing_weapon = False
change_weapon_target = None
change_animation_time = 0.25
change_animation_timer = 0.0
previous_distance = 0
target_distance = 0
current_distance = 0

current_weapon = 1
bullets = []
scattered_bullets = []
last_shot_time = 0

mouse_left_button_down = False
mouse_right_button_down = False

recoil_offset = 0
recoil_velocity = 0

shake_offset_x = 0
shake_offset_y = 0
shake_timer = 0
shake_timer_max = 15
shake_magnitude = 3
shake_elapsed = 0.0
shake_speed = 50.0

walk_timer = 0
walk_delay = 500

paused = False
fade_in_after_resume = False

renderer = Renderer3D(screen)

clock = pygame.time.Clock()
running = True

player_radius = int(30 * PLAYER_VIEW_SCALE)

player_hp = 300
player_hp_max = 300

damage_flash_alpha = 0
damage_flash_fade_speed = 5

blood_effects = []

kill_count = 0

changing_room = False
visited_f_rooms = {}
DIRECTION_OFFSET = {
    "north": (0, -1),
    "south": (0, 1),
    "west": (-1, 0),
    "east": (1, 0)
}

SPAWN_FROM_OPPOSITE = {
    "north": "south",
    "south": "north",
    "west": "east",
    "east": "west"
}

def change_room(direction):
    global current_room_pos, CURRENT_MAP, world, world_x, world_y, enemies, changing_room
    global effective_bg_width, effective_bg_height

    WIDTH, HEIGHT = get_map_dimensions()
    changing_room = True

    dx, dy = DIRECTION_OFFSET[direction]
    new_x = current_room_pos[0] + dx
    new_y = current_room_pos[1] + dy

    if not (0 <= new_x < WIDTH and 0 <= new_y < HEIGHT):
        print("[DEBUG] 이동 불가: 맵 경계 밖")
        changing_room = False
        return

    new_room_type = grid[new_y][new_x]
    spawn_direction = SPAWN_FROM_OPPOSITE[direction]

    if new_room_type == 'N':
        print("[DEBUG] 이동 불가: 빈 방")
        changing_room = False
        return

    curr_center_x = effective_bg_width / 2
    curr_center_y = effective_bg_height / 2
    player_world_x = world_x + player_rect.centerx
    player_world_y = world_y + player_rect.centery
    dx_from_center = player_world_x - curr_center_x
    dy_from_center = player_world_y - curr_center_y

    combat_walls_info.clear()
    combat_walls.clear()
    obstacle_manager.combat_obstacles.clear()

    if new_room_type == 'F':
        room_key = (new_x, new_y)
        if room_key not in visited_f_rooms:
            fight_map_index = random.randint(0, len(FIGHT_MAPS) - 1)
            visited_f_rooms[room_key] = {
                "fight_map_index": fight_map_index,
                "cleared": False
            }
            print(f"[DEBUG] FIGHT_MAP 랜덤 선택: index {fight_map_index}")
        fight_map_index = visited_f_rooms[room_key]["fight_map_index"]
        CURRENT_MAP = FIGHT_MAPS[fight_map_index]

        if visited_f_rooms[room_key]["cleared"]:
            CURRENT_MAP = {
                "obstacles": CURRENT_MAP["obstacles"],
                "enemy_infos": [],
                "crop_rect": CURRENT_MAP["crop_rect"]
            }
    else:
        CURRENT_MAP = MAPS[0]

    current_room_pos = [new_x, new_y]
    sx, sy = new_x, new_y
    WIDTH, HEIGHT = get_map_dimensions()

    north_hole_open = (sy > 0 and grid[sy - 1][sx] != 'N')
    south_hole_open = (sy < HEIGHT - 1 and grid[sy + 1][sx] != 'N')
    west_hole_open = (sx > 0 and grid[sy][sx - 1] != 'N')
    east_hole_open = (sx < WIDTH - 1 and grid[sy][sx + 1] != 'N')

    obstacle_manager.static_obstacles.clear()
    obstacle_manager.generate_obstacles_from_map(CURRENT_MAP)

    new_world = World(
        background_image=background_image,
        crop_rect=CURRENT_MAP.get("crop_rect"),
        PLAYER_VIEW_SCALE=PLAYER_VIEW_SCALE,
        BG_WIDTH=BG_WIDTH,
        BG_HEIGHT=BG_HEIGHT,
        hole_width=hole_width,
        hole_height=hole_height,
        left_wall_width=0,
        top_wall_height=0,
        tunnel_length=10000 * PLAYER_VIEW_SCALE
    )

    map_width = new_world.effective_bg_width
    map_height = new_world.effective_bg_height

    left_wall_width = (map_width / 2) - (hole_width / 2)
    right_wall_width = left_wall_width
    top_wall_height = (map_height / 2) - (hole_height / 2)
    bottom_wall_height = top_wall_height

    new_world.left_wall_width = left_wall_width
    new_world.top_wall_height = top_wall_height

    player_center_x = player_rect.centerx
    player_center_y = player_rect.centery

    spawn_world_x, spawn_world_y = new_world.get_spawn_point(
        direction=spawn_direction,
        margin=275
    )

    if direction in ("west", "east"):
        spawn_world_y += dy_from_center
    else:
        spawn_world_x += dx_from_center

    world = new_world
    world_x = spawn_world_x - player_center_x
    world_y = spawn_world_y - player_center_y

    effective_bg_width = world.effective_bg_width
    effective_bg_height = world.effective_bg_height

    walls = world.generate_walls(
        map_width=map_width,
        map_height=map_height,
        wall_thickness=wall_thickness,
        hole_width=hole_width,
        hole_height=hole_height,
        left_wall_width=left_wall_width,
        right_wall_width=right_wall_width,
        top_wall_height=top_wall_height,
        bottom_wall_height=bottom_wall_height,
        north_hole_open=north_hole_open,
        south_hole_open=south_hole_open,
        west_hole_open=west_hole_open,
        east_hole_open=east_hole_open,
        expansion=expansion
    )
    obstacle_manager.static_obstacles = [w for w in obstacle_manager.static_obstacles if w.image_filename != "invisible_wall"]
    obstacle_manager.static_obstacles.extend(walls)

    bullets.clear()
    scattered_bullets.clear()
    blood_effects.clear()
    config.global_enemy_bullets.clear()
    for enemy in enemies:
        if hasattr(enemy, "scattered_bullets"):
            enemy.scattered_bullets.clear()

    enemies = []
    for info in CURRENT_MAP["enemy_infos"]:
        ex = info["x"] * PLAYER_VIEW_SCALE
        ey = info["y"] * PLAYER_VIEW_SCALE
        enemy_type = info["enemy_type"]

        if enemy_type == "enemy2":
            enemy = Enemy2(
                world_x=ex,
                world_y=ey,
                image=images["enemy2"],
                gun_image=images["gun2"],
                bullet_image=images["enemy_bullet"],
                sounds=sounds,
                get_player_center_world_fn=get_player_center_world,
                obstacle_manager=obstacle_manager,
                check_circle_collision_fn=check_circle_collision,
                check_ellipse_circle_collision_fn=check_ellipse_circle_collision,
                player_bullet_image=images["bullet1"],
                cartridge_image=images["cartridge_case1"],
                kill_callback=increment_kill_count,
                map_width=map_width,
                map_height=map_height
            )
        else:
            enemy = Enemy1(
                world_x=ex,
                world_y=ey,
                image=images["enemy1"],
                gun_image=images["gun1"],
                bullet_image=images["enemy_bullet"],
                sounds=sounds,
                get_player_center_world_fn=get_player_center_world,
                obstacle_manager=obstacle_manager,
                check_circle_collision_fn=check_circle_collision,
                check_ellipse_circle_collision_fn=check_ellipse_circle_collision,
                player_bullet_image=images["bullet1"],
                cartridge_image=images["cartridge_case1"],
                kill_callback=increment_kill_count,
                map_width=map_width,
                map_height=map_height
            )
        enemies.append(enemy)

    if len(CURRENT_MAP["enemy_infos"]) == 0:
        config.combat_state = False
        config.combat_enabled = False
    else:
        config.combat_state = False
        config.combat_enabled = True

    pygame.time.set_timer(pygame.USEREVENT + 1, 200)

def increment_kill_count():
    global kill_count
    kill_count += 1

def check_circle_collision(center1, radius1, center2, radius2):
    dx = center1[0] - center2[0]
    dy = center1[1] - center2[1]
    dist_sq = dx * dx + dy * dy
    r_sum = radius1 + radius2
    return dist_sq <= r_sum * r_sum

def check_ellipse_circle_collision(circle_center, circle_radius, ellipse_center, rx, ry):
    dx = circle_center[0] - ellipse_center[0]
    dy = circle_center[1] - ellipse_center[1]
    test = (dx ** 2) / ((rx + circle_radius) ** 2) + \
           (dy ** 2) / ((ry + circle_radius) ** 2)
    return test <= 1.0


def get_player_center_world(world_x, world_y):
    return (
        world_x + player_rect.centerx,
        world_y + player_rect.centery
    )

def fade_out(screen, duration, step_delay):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0))
    steps = int(duration / step_delay)
    clock = pygame.time.Clock()
    for i in range(steps + 1):
        alpha = int(255 * (i / steps))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(1 / step_delay)

def fade_in(screen, duration, step_delay):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0))
    steps = int(duration / step_delay)
    clock = pygame.time.Clock()
    for i in range(steps + 1):
        alpha = int(255 * (1 - i / steps))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(1 / step_delay)

def make_swipe_gradient(width, height, horizontal=True, reverse=False):
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    for i in range(width if horizontal else height):
        alpha = int(255 * (i / (width-1 if horizontal else height-1)))
        if reverse:
            alpha = 255 - alpha
        if horizontal:
            pygame.draw.rect(overlay, (0, 0, 0, alpha), (i, 0, 1, height))
        else:
            pygame.draw.rect(overlay, (0, 0, 0, alpha), (0, i, width, 1))
    return overlay

def swipe_transition(screen, old_surface, new_surface, direction="right", duration=0.45, fps=60):
    width, height = screen.get_size()
    frames = int(duration * fps)
    clock = pygame.time.Clock()
    horizontal = direction in ("left", "right")
    reverse = direction in ("left", "up")
    overlay = make_soft_curtain(width, height, horizontal=(direction in ("left", "right")), direction=direction)
    for i in range(frames + 1):
        t = i / frames
        offset = int((width if horizontal else height) * t)
        screen.fill((0,0,0))
        if direction == "right":
            screen.blit(new_surface, (0,0))
            screen.blit(overlay, (-width + offset, 0))
        elif direction == "left":
            screen.blit(new_surface, (0,0))
            screen.blit(overlay, (width - offset, 0))
        elif direction == "down":
            screen.blit(new_surface, (0,0))
            screen.blit(overlay, (0, -height + offset))
        elif direction == "up":
            screen.blit(new_surface, (0,0))
            screen.blit(overlay, (0, height - offset))
        pygame.display.flip()
        clock.tick(fps)

def swipe_curtain_transition(screen, old_surface, draw_new_room_fn, direction="right", duration=0.5, fps=60):
    width, height = screen.get_size()
    frames = int(duration * fps // 2)
    clock = pygame.time.Clock()
    horizontal = direction in ("left", "right")

    overlay = make_soft_curtain(width, height, horizontal=horizontal, direction=direction)

    for i in range(frames + 1):
        t = i / frames
        t_eased = 1 - (1 - t) ** 2
        offset = int((width if horizontal else height) * t_eased)

        screen.blit(old_surface, (0, 0))

        if direction == "right":
            screen.blit(overlay, (offset - width, 0))
        elif direction == "left":
            screen.blit(overlay, (width - offset, 0))
        elif direction == "down":
            screen.blit(overlay, (0, offset - height))
        elif direction == "up":
            screen.blit(overlay, (0, height - offset))

    pygame.display.flip()
    clock.tick(fps)

    draw_new_room_fn()
    new_surface = screen.copy()

    for i in range(frames + 1):
        t = i / frames
        t_eased = t ** 2
        offset = int((width if horizontal else height) * t_eased)

        screen.blit(new_surface, (0, 0))

        if direction == "right":
            screen.blit(overlay, (offset - width, 0))
        elif direction == "left":
            screen.blit(overlay, (width - offset, 0))
        elif direction == "down":
            screen.blit(overlay, (0, offset - height))
        elif direction == "up":
            screen.blit(overlay, (0, height - offset))

        pygame.display.flip()
        clock.tick(fps)

def make_soft_curtain(width, height, horizontal=True, direction="right"):
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    fade_ratio = 0.25
    if horizontal:
        for x in range(width):
            if direction == "right":
                progress = x / width
            else:
                progress = (width - x) / width

            fade = min(1.0, max(0.0, progress / fade_ratio))
            alpha = int(255 * fade)
            pygame.draw.line(overlay, (0, 0, 0, alpha), (x, 0), (x, height))
    else:
        for y in range(height):
            if direction == "down":
                progress = y / height
            else:
                progress = (height - y) / height

            fade = min(1.0, max(0.0, progress / fade_ratio))
            alpha = int(255 * fade)
            pygame.draw.line(overlay, (0, 0, 0, alpha), (0, y, width, 1))

    return overlay

def make_soft_curtain(width, height, horizontal=True, direction="right"):
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    fade_ratio = 0.25

    if horizontal:
        for x in range(width):
            if direction == "right":
                progress = x / width
            else:
                progress = (width - x) / width

            fade = min(1.0, max(0.0, progress / fade_ratio))
            alpha = int(255 * fade)
            pygame.draw.line(overlay, (0, 0, 0, alpha), (x, 0), (x, height))
    else:
        for y in range(height):
            if direction == "down":
                progress = (height - y) / height
            else:
                progress = y / height

            fade = min(1.0, max(0.0, progress / fade_ratio))
            alpha = int(255 * fade)
            pygame.draw.line(overlay, (0, 0, 0, alpha), (0, y), (width, y))

    return overlay

def make_soft_curtain(width, height, horizontal=True, direction="right"):
    scale = 2
    curtain_width = int(width * scale)
    curtain_height = int(height * scale)
    overlay = pygame.Surface((curtain_width, curtain_height), pygame.SRCALPHA)

    fade_length = int((curtain_width if horizontal else curtain_height) * 0.25)

    if horizontal:
        for x in range(curtain_width):
            if direction == "right":
                pos = curtain_width - x
            else:
                pos = x

            if pos < fade_length:
                fade = pos / fade_length
                alpha = int(255 * fade)
            else:
                alpha = 255

            pygame.draw.line(overlay, (0, 0, 0, alpha), (x, 0), (x, curtain_height))
    else:
        for y in range(curtain_height):
            if direction == "down":
                pos = curtain_height - y
            else:
                pos = y

            if pos < fade_length:
                fade = pos / fade_length
                alpha = int(255 * fade)
            else:
                alpha = 255

            pygame.draw.line(overlay, (0, 0, 0, alpha), (0, y), (curtain_width, y))

    return overlay

def swipe_curtain_transition(screen, old_surface, draw_new_room_fn, direction="right", duration=0.5, fps=60):
    width, height = screen.get_size()
    frames = int(duration * fps // 2)
    clock = pygame.time.Clock()
    horizontal = direction in ("left", "right")

    overlay = make_soft_curtain(width, height, horizontal=horizontal, direction=direction)
    curtain_width, curtain_height = overlay.get_size()

    max_offset = (curtain_width if horizontal else curtain_height) - (width if horizontal else height) // 4

    for i in range(frames + 1):
        t = i / frames
        t_eased = 1 - (1 - t) ** 2
        offset = int(max_offset * t_eased)

        screen.blit(old_surface, (0, 0))

        if direction == "right":
            screen.blit(overlay, (offset - curtain_width, 0))
        elif direction == "left":
            screen.blit(overlay, (width - offset, 0))
        elif direction == "down":
            screen.blit(overlay, (0, offset - curtain_height))
        elif direction == "up":
            screen.blit(overlay, (0, height - offset))

        pygame.display.flip()
        clock.tick(fps)

    draw_new_room_fn()
    new_surface = screen.copy()
    pygame.time.delay(100)

    reverse_direction = {
        "left": "right",
        "right": "left",
        "up": "down",
        "down": "up"
    }[direction]

    overlay = make_soft_curtain(width, height, horizontal=horizontal, direction=reverse_direction)
    curtain_width, curtain_height = overlay.get_size()
    max_offset = (curtain_width if horizontal else curtain_height) - (width if horizontal else height) // 4

    for i in range(frames + 1):
        t = i / frames
        t_eased = t ** 2
        offset = int(max_offset * (1 - t_eased))

        screen.blit(new_surface, (0, 0))

        if reverse_direction == "right":
            screen.blit(overlay, (offset - curtain_width, 0))
        elif reverse_direction == "left":
            screen.blit(overlay, (width - offset, 0))
        elif reverse_direction == "down":
            screen.blit(overlay, (0, offset - curtain_height))
        elif reverse_direction == "up":
            screen.blit(overlay, (0, height - offset))

        pygame.display.flip()
        clock.tick(fps)

def draw_minimap(screen, grid, current_room_pos):
    mini_tile = 14
    tile_gap = 3
    padding = 10
    background_margin = 5
    grid_width = len(grid[0])
    grid_height = len(grid)

    total_width = grid_width * (mini_tile + tile_gap) - tile_gap
    total_height = grid_height * (mini_tile + tile_gap) - tile_gap

    display_width, display_height = screen.get_size()
    start_x = display_width - total_width - padding
    start_y = padding

    background_surface = pygame.Surface(
        (total_width + background_margin * 2, total_height + background_margin * 2),
        pygame.SRCALPHA
    )
    background_surface.fill((100, 100, 100, 160))
    screen.blit(background_surface, (start_x - background_margin, start_y - background_margin))

    valid_cells = {'F', 'S', 'E'}
    connection_color = (160, 160, 160)
    connection_thickness = 4

    for y in range(grid_height):
        for x in range(grid_width):
            cell = grid[y][x]
            if cell not in valid_cells:
                continue

            cx = start_x + x * (mini_tile + tile_gap) + mini_tile // 2
            cy = start_y + y * (mini_tile + tile_gap) + mini_tile // 2

            if x + 1 < grid_width and grid[y][x + 1] in valid_cells:
                cx2 = start_x + (x + 1) * (mini_tile + tile_gap) + mini_tile // 2
                pygame.draw.rect(screen, connection_color,
                    pygame.Rect(min(cx, cx2), cy - connection_thickness // 2, abs(cx2 - cx), connection_thickness))

            if y + 1 < grid_height and grid[y + 1][x] in valid_cells:
                cy2 = start_y + (y + 1) * (mini_tile + tile_gap) + mini_tile // 2
                pygame.draw.rect(screen, connection_color,
                    pygame.Rect(cx - connection_thickness // 2, min(cy, cy2), connection_thickness, abs(cy2 - cy)))

    for y in range(grid_height):
        for x in range(grid_width):
            cell = grid[y][x]
            color = None
            alpha = 255

            if cell == 'S':
                color = (120, 255, 120)
            elif cell == 'E':
                color = (255, 120, 120)
            elif cell == 'F':
                color = (160, 160, 160)
            elif cell == 'N':
                color = (100, 100, 100)
                alpha = 20

            if color:
                rect = pygame.Rect(
                    start_x + x * (mini_tile + tile_gap),
                    start_y + y * (mini_tile + tile_gap),
                    mini_tile,
                    mini_tile
                )
                tile_surface = pygame.Surface((mini_tile, mini_tile), pygame.SRCALPHA)
                tile_surface.fill((*color, alpha))
                screen.blit(tile_surface, rect.topleft)

    cx, cy = current_room_pos
    cursor_center_x = start_x + cx * (mini_tile + tile_gap) + mini_tile // 2
    cursor_center_y = start_y + cy * (mini_tile + tile_gap) + mini_tile // 2

    time_ms = pygame.time.get_ticks()
    phase = (time_ms // 1500) % 2

    base_size = 32
    scale_factor = 0.6 if phase == 0 else 0.65

    cursor_size = int(base_size * scale_factor)
    half = cursor_size // 2

    bar = 2
    edge = 6

    pygame.draw.rect(screen, (255, 0, 0),
        (cursor_center_x - half, cursor_center_y - half, bar, edge))
    pygame.draw.rect(screen, (255, 0, 0),
        (cursor_center_x - half, cursor_center_y - half, edge, bar))

    pygame.draw.rect(screen, (255, 0, 0),
        (cursor_center_x + half - bar, cursor_center_y - half, bar, edge))
    pygame.draw.rect(screen, (255, 0, 0),
        (cursor_center_x + half - edge, cursor_center_y - half, edge, bar))

    pygame.draw.rect(screen, (255, 0, 0),
        (cursor_center_x - half, cursor_center_y + half - edge, bar, edge))
    pygame.draw.rect(screen, (255, 0, 0),
        (cursor_center_x - half, cursor_center_y + half - bar, edge, bar))

    pygame.draw.rect(screen, (255, 0, 0),
        (cursor_center_x + half - bar, cursor_center_y + half - edge, bar, edge))
    pygame.draw.rect(screen, (255, 0, 0),
        (cursor_center_x + half - edge, cursor_center_y + half - bar, edge, bar))

enemies = []
for info in CURRENT_MAP["enemy_infos"]:
    ex = info["x"] * PLAYER_VIEW_SCALE
    ey = info["y"] * PLAYER_VIEW_SCALE
    enemy_type = info["enemy_type"]

    if enemy_type == "enemy2":
        enemy = Enemy2(
            world_x=ex,
            world_y=ey,
            image=images["enemy2"],
            gun_image=images["gun2"],
            bullet_image=images["enemy_bullet"],
            sounds=sounds,
            get_player_center_world_fn=get_player_center_world,
            obstacle_manager=obstacle_manager,
            check_circle_collision_fn=check_circle_collision,
            check_ellipse_circle_collision_fn=check_ellipse_circle_collision,
            player_bullet_image=images["bullet1"],
            cartridge_image=images["cartridge_case1"],
            kill_callback=increment_kill_count,
            map_width=map_width,
            map_height=map_height,
        )
    else:
        enemy = Enemy1(
            world_x=ex,
            world_y=ey,
            image=images["enemy1"],
            gun_image=images["gun1"],
            bullet_image=images["enemy_bullet"],
            sounds=sounds,
            get_player_center_world_fn=get_player_center_world,
            obstacle_manager=obstacle_manager,
            check_circle_collision_fn=check_circle_collision,
            check_ellipse_circle_collision_fn=check_ellipse_circle_collision,
            player_bullet_image=images["bullet1"],
            cartridge_image=images["cartridge_case1"],
            kill_callback=increment_kill_count,
            map_width=map_width,
            map_height=map_height,
        )

    enemies.append(enemy)
if len(enemies) == 0:
    config.combat_enabled = False
    print("[DEBUG] No enemies in map. Combat disabled.")
else:
    config.combat_enabled = True
    print(f"[DEBUG] Enemies in map: {len(enemies)}. Combat enabled.")

while running:
    current_time = pygame.time.get_ticks()
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.USEREVENT + 1:
            changing_room = False
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                move_up = True
            elif event.key == pygame.K_s:
                move_down = True
            elif event.key == pygame.K_a:
                move_left = True
            elif event.key == pygame.K_d:
                move_right = True
            elif event.key == pygame.K_SPACE:
                player_world_x = world_x + player_rect.centerx * PLAYER_VIEW_SCALE
                player_world_y = world_y + player_rect.centery * PLAYER_VIEW_SCALE
                print(f"[DEBUG] Player world position: ({player_world_x:.2f}, {player_world_y:.2f})")
            elif event.key == pygame.K_TAB:
                fade_out(screen, duration=0.3, step_delay=0.01)
                paused = not paused
                if paused:
                    pygame.mouse.set_visible(True)
                    if current_weapon == 1:
                        obj_file = "Gun13DObject.obj"
                        zoom = GUN1_ZOOM_LEVEL
                    elif current_weapon == 2:
                        obj_file = "Gun23DObject.obj"
                        zoom = GUN2_ZOOM_LEVEL
                    elif current_weapon == 3:
                        obj_file = "Gun33DObject.obj"
                        zoom = GUN3_ZOOM_LEVEL
                    else:
                        obj_file = "Gun13DObject.obj"
                        zoom = GUN1_ZOOM_LEVEL

                    renderer.load_new_obj(obj_file, zoom_level=zoom)
                    renderer.reset_view()
                    fade_in(screen, duration=0.3, step_delay=0.01)
                else:
                    pygame.mouse.set_visible(False)
                    fade_in_after_resume = True
            elif event.key == pygame.K_1:
                if current_weapon != 1 and not changing_weapon:
                    changing_weapon = True
                    change_weapon_target = 1
                    change_animation_timer = 0.0
                    previous_distance = current_distance
                    target_distance = GUN1_DISTANCE_FROM_CENTER
            elif event.key == pygame.K_2:
                if current_weapon != 2 and not changing_weapon:
                    changing_weapon = True
                    change_weapon_target = 2
                    change_animation_timer = 0.0
                    previous_distance = current_distance
                    target_distance = GUN2_DISTANCE_FROM_CENTER
            elif event.key == pygame.K_3:
                if current_weapon != 3 and not changing_weapon:
                    changing_weapon = True
                    change_weapon_target = 3
                    change_animation_timer = 0.0
                    previous_distance = current_distance
                    target_distance = GUN3_DISTANCE_FROM_CENTER
            elif event.key == pygame.K_q:
                print("[DEBUG] Q pressed: Killing all enemies instantly (dev cheat)")
                for enemy in enemies[:]:
                    if enemy.alive:
                        enemy.hit(9999, blood_effects)  # 강제로 사망시킴
                        enemies.remove(enemy)
                        blood_effects.append(ScatteredBlood(enemy.world_x, enemy.world_y))

                config.combat_state = False
                config.combat_enabled = False

                for wall in combat_walls:
                    if wall in obstacle_manager.combat_obstacles:
                        obstacle_manager.combat_obstacles.remove(wall)
                combat_walls.clear()

                for info in combat_walls_info:
                    info["state"] = "hiding"
                    info["target_pos"] = info["start_pos"]
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                move_up = False
            elif event.key == pygame.K_s:
                move_down = False
            elif event.key == pygame.K_a:
                move_left = False
            elif event.key == pygame.K_d:
                move_right = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_left_button_down = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_left_button_down = False

    if paused:
        renderer.handle_events(events)
        renderer.render_model(clock)
        clock.tick(60)
        continue

    if changing_room:
        clock.tick(60)
        continue

    if fade_in_after_resume:
        screen.fill((0, 0, 0))
        pygame.display.flip()
        fade_in(screen, duration=0.3, step_delay=0.01)
        fade_in_after_resume = False

    delta_time = clock.get_time()
    player_center = (world_x + player_rect.centerx, 
                    world_y + player_rect.centery)
    
    #적 바보 만들기
    for enemy in enemies:
        if config.combat_state:
            enemy.update(
                dt=delta_time,
                world_x=world_x,
                world_y=world_y,
                player_rect=player_rect,
                enemies=enemies
            )

    for scatter in scattered_bullets[:]:
        scatter.update()
        if scatter.alpha <= 0:
            scattered_bullets.remove(scatter)

    if current_weapon == 1:
        distance_from_center = GUN1_DISTANCE_FROM_CENTER
    elif current_weapon == 2:
        distance_from_center = GUN2_DISTANCE_FROM_CENTER
    elif current_weapon == 3:
        distance_from_center = GUN3_DISTANCE_FROM_CENTER
    else:
        distance_from_center = GUN1_DISTANCE_FROM_CENTER

    if changing_weapon:
        change_animation_timer += clock.get_time() / 1000.0
        t = min(change_animation_timer / change_animation_time, 1.0)
        if t < 0.5:
            current_distance = (1.0 - (t / 0.5)) * previous_distance
        else:
            if current_weapon != change_weapon_target:
                current_weapon = change_weapon_target
            current_distance = ((t - 0.5) / 0.5) * target_distance
        if t >= 1.0:
            changing_weapon = False
            current_distance = target_distance
    else:
        current_distance = distance_from_center

    keys = pygame.key.get_pressed()

    if recoil_in_progress or mouse_left_button_down:
        max_speed = normal_max_speed
    else:
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            if allow_sprint:
                max_speed = sprint_max_speed
        else:
            max_speed = normal_max_speed

    if current_weapon == 1:
        max_speed *= (1 - GUN1_SPEED_PENALTY)
    elif current_weapon == 2:
        max_speed *= (1 - GUN2_SPEED_PENALTY)
    elif current_weapon == 3:
        max_speed *= (1 - GUN3_SPEED_PENALTY)
    else:
        max_speed *= (1 - GUN1_SPEED_PENALTY)

    if move_left:
        world_vx -= acceleration_rate
    elif move_right:
        world_vx += acceleration_rate
    else:
        if world_vx > 0:
            world_vx = max(0.0, world_vx - deceleration_rate)
        elif world_vx < 0:
            world_vx = min(0.0, world_vx + deceleration_rate)

    if move_up:
        world_vy -= acceleration_rate
    elif move_down:
        world_vy += acceleration_rate
    else:
        if world_vy > 0:
            world_vy = max(0.0, world_vy - deceleration_rate)
        elif world_vy < 0:
            world_vy = min(0.0, world_vy + deceleration_rate)

    world_vx = max(-max_speed, min(max_speed, world_vx))
    world_vy = max(-max_speed, min(max_speed, world_vy))

    test_world_x = world_x + world_vx
    test_world_y = world_y

    player_center_world_x = world_x + player_rect.centerx
    player_center_world_y = world_y + player_rect.centery

    if config.combat_enabled and not config.combat_state:
        if (0 <= player_center_world_x <= effective_bg_width and
            0 <= player_center_world_y <= effective_bg_height):
            config.combat_state = True
            print("[DEBUG] Combat START!")

            combat_walls_info.clear()

            adjust_x = (effective_bg_width - hole_width) / 2 - left_wall_width
            adjust_y = (effective_bg_height - hole_height) / 2 - top_wall_height

            scaled_img = images["wall_barrier"]
            rotated_img = images["wall_barrier_rotated"]

            scaled_width = scaled_img.get_width()
            scaled_height = scaled_img.get_height()
            rotated_width = rotated_img.get_width()
            rotated_height = rotated_img.get_height()

            center_x = left_wall_width + adjust_x + (hole_width / 2)
            center_y = top_wall_height + adjust_y + (hole_height / 2)

            offset_x = -0.5
            offset_y = -0.5

            WALL_SPAWN_OFFSET_FACTOR = 1.2
            north_target_x = center_x - scaled_width / 2 + offset_x
            north_target_y = 0 - wall_thickness + offset_y - 155
            north_start_x = north_target_x - scaled_width
            north_start_y = north_target_y

            combat_walls_info.append({
                "side": "north",
                "image": scaled_img,
                "target_pos": (int(north_target_x), int(north_target_y)),
                "current_pos": (int(north_start_x), int(north_start_y)),
                "start_pos": (int(north_start_x), int(north_start_y)),
                "state": "visible",
            })

            west_target_x = 0 - wall_thickness + offset_x - 155
            west_target_y = center_y - rotated_height / 2 + offset_y
            west_start_x = west_target_x
            west_start_y = west_target_y - rotated_height

            combat_walls_info.append({
                "side": "west",
                "image": rotated_img,
                "target_pos": (int(west_target_x), int(west_target_y)),
                "current_pos": (int(west_start_x), int(west_start_y)),
                "start_pos": (int(west_start_x), int(west_start_y)),
                "state": "visible",
            })

            south_target_x = center_x - scaled_width / 2 + offset_x
            south_target_y = effective_bg_height + offset_y - 95
            south_start_x = south_target_x + scaled_width
            south_start_y = south_target_y

            combat_walls_info.append({
                "side": "south",
                "image": scaled_img,
                "target_pos": (int(south_target_x), int(south_target_y)),
                "current_pos": (int(south_start_x), int(south_start_y)),
                "start_pos": (int(south_start_x), int(south_start_y)),
                "state": "visible",
            })

            east_target_x = effective_bg_width + offset_x - 95
            east_target_y = center_y - rotated_height / 2 + offset_y
            east_start_x = east_target_x
            east_start_y = east_target_y + rotated_height

            combat_walls_info.append({
                "side": "east",
                "image": rotated_img,
                "target_pos": (int(east_target_x), int(east_target_y)),
                "current_pos": (int(east_start_x), int(east_start_y)),
                "start_pos": (int(east_start_x), int(east_start_y)),
                "state": "visible",
            })

            combat_walls = world.generate_thin_combat_walls(
                left_wall_width=left_wall_width,
                top_wall_height=top_wall_height,
                hole_width=hole_width,
                hole_height=hole_height
            )
            obstacle_manager.combat_obstacles.extend(combat_walls)

    penetration_total_x = 0.0

    if config.combat_state:
        obstacles_to_check = obstacle_manager.static_obstacles + obstacle_manager.combat_obstacles
    else:
        obstacles_to_check = obstacle_manager.static_obstacles

    for obs in obstacles_to_check:
        for c in obs.colliders:
            penetration = c.compute_penetration_circle(
                (player_center_world_x, player_center_world_y),
                player_radius,
                (obs.world_x, obs.world_y)
            )
            if penetration:
                penetration_total_x += penetration[0]

    for enemy in enemies:
        dx = player_center_world_x - enemy.world_x
        dy = player_center_world_y - enemy.world_y
        dist_sq = dx * dx + dy * dy
        r_sum = player_radius + enemy.radius
        if dist_sq < r_sum * r_sum:
            dist = math.sqrt(dist_sq) if dist_sq > 0 else 0.0001
            penetration = r_sum - dist
            penetration_total_x += (dx / dist) * penetration

    if penetration_total_x != 0.0:
        world_x += penetration_total_x * 0.5

        n_len = math.hypot(penetration_total_x, 0.0)
        if n_len > 0:
            nx = penetration_total_x / n_len
            ny = 0.0

            tx = -ny
            ty = nx

            dot = world_vx * tx + world_vy * ty
            world_vx = dot * tx
            world_vy = dot * ty
    else:
        world_x = test_world_x

    test_world_x = world_x
    test_world_y = world_y + world_vy

    player_center_world_x = test_world_x + player_rect.centerx
    player_center_world_y = test_world_y + player_rect.centery

    penetration_total_y = 0.0

    for obs in obstacles_to_check:
        for c in obs.colliders:
            penetration = c.compute_penetration_circle(
                (player_center_world_x, player_center_world_y),
                player_radius,
                (obs.world_x, obs.world_y)
            )
            if penetration:
                penetration_total_y += penetration[1]

    for enemy in enemies:
        dx = player_center_world_x - enemy.world_x
        dy = player_center_world_y - enemy.world_y
        dist_sq = dx * dx + dy * dy
        r_sum = player_radius + enemy.radius
        if dist_sq < r_sum * r_sum:
            dist = math.sqrt(dist_sq) if dist_sq > 0 else 0.0001
            penetration = r_sum - dist
            penetration_total_y += (dy / dist) * penetration

    if penetration_total_y != 0.0:
        world_y += penetration_total_y * 0.5

        n_len = math.hypot(0.0, penetration_total_y)
        if n_len > 0:
            nx = 0.0
            ny = penetration_total_y / n_len

            tx = -ny
            ty = nx

            dot = world_vx * tx + world_vy * ty
            world_vx = dot * tx
            world_vy = dot * ty
    else:
        world_y = test_world_y
    
    for bullet in bullets[:]:
        bullet.update(obstacle_manager)

    half_screen_width = SCREEN_WIDTH // 2
    half_screen_height = SCREEN_HEIGHT // 2

    world_x = max(-half_screen_width - expansion,
                min(effective_bg_width - half_screen_width + expansion, world_x))

    world_y = max(-half_screen_height - expansion,
                min(effective_bg_height - half_screen_height + expansion, world_y))

    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x - player_rect.centerx
    dy = mouse_y - player_rect.centery
    angle_radians = math.atan2(dy, dx)
    angle_degrees = math.degrees(angle_radians)

    scaled_player_image = pygame.transform.smoothscale(
    original_player_image,
    (
        int(original_player_image.get_width() * PLAYER_VIEW_SCALE),
        int(original_player_image.get_height() * PLAYER_VIEW_SCALE)
    )
    )
    rotated_player_image = pygame.transform.rotate(scaled_player_image, -angle_degrees + 90)
    rotated_player_rect = rotated_player_image.get_rect(center=player_rect.center)

    if current_weapon == 1:
        current_gun_image = original_gun_image_1
    elif current_weapon == 2:
        current_gun_image = original_gun_image_2
    elif current_weapon == 3:
        current_gun_image = original_gun_image_3 
    else:
        current_gun_image = original_gun_image_1


    gun_pos_x = player_rect.centerx + math.cos(angle_radians) * (current_distance + recoil_offset)
    gun_pos_y = player_rect.centery + math.sin(angle_radians) * (current_distance + recoil_offset)
    scaled_gun_image = pygame.transform.smoothscale(
    current_gun_image,
    (
        int(current_gun_image.get_width() * PLAYER_VIEW_SCALE),
        int(current_gun_image.get_height() * PLAYER_VIEW_SCALE)
    )
    )
    rotated_gun_image = pygame.transform.rotate(scaled_gun_image, -angle_degrees + 90)
    rotated_gun_rect = rotated_gun_image.get_rect(center=(gun_pos_x, gun_pos_y))

    if current_weapon == 1:
        fire_delay = GUN1_FIRE_DELAY
        recoil_strength = GUN1_RECOIL
        fire_sound = sounds["gun1_fire"]
    elif current_weapon == 2:
        fire_delay = GUN2_FIRE_DELAY
        recoil_strength = GUN2_RECOIL
        fire_sound = sounds["gun2_fire"]
    elif current_weapon == 3:
        fire_delay = GUN3_FIRE_DELAY
        recoil_strength = GUN3_RECOIL
        fire_sound = sounds["gun3_fire"]
    else:
        fire_delay = GUN1_FIRE_DELAY
        recoil_strength = GUN1_RECOIL
        fire_sound = sounds["gun1_fire"]


    if mouse_left_button_down and not changing_weapon:
        if current_time - last_shot_time > fire_delay:
            fire_sound.play()

            if current_weapon == 1:
                spread_angle = GUN1_SPREAD_ANGLE
            elif current_weapon == 2:
                spread_angle = GUN2_SPREAD_ANGLE
            elif current_weapon == 3:
                spread_angle = GUN3_SPREAD_ANGLE
            else:
                spread_angle = GUN1_SPREAD_ANGLE
            recoil_offset = 0
            recoil_velocity = -recoil_strength

            allow_sprint = False
            recoil_in_progress = True

            spawn_offset = 30 * PLAYER_VIEW_SCALE
            vertical_offset = 6 * PLAYER_VIEW_SCALE
            offset_angle = angle_radians + math.radians(90)
            offset_dx = math.cos(offset_angle) * vertical_offset
            offset_dy = math.sin(offset_angle) * vertical_offset

            if current_weapon == 3:
                for i in range(GUN3_NUM_BULLETS):
                    spread_angle_range = GUN3_SPREAD_ANGLE
                    spread_angle = math.radians(random.uniform(-spread_angle_range, spread_angle_range))
                    direction_x = math.cos(angle_radians + spread_angle)
                    direction_y = math.sin(angle_radians + spread_angle)

                    bullet_world_x = world_x + player_rect.centerx + direction_x * spawn_offset + offset_dx
                    bullet_world_y = world_y + player_rect.centery + direction_y * spawn_offset + offset_dy

                    target_world_x = bullet_world_x + direction_x * 100
                    target_world_y = bullet_world_y + direction_y * 100

                    new_bullet = Bullet(
                        bullet_world_x,
                        bullet_world_y,
                        target_world_x,
                        target_world_y,
                        0,
                        original_bullet_image,
                        speed=7.5 * PLAYER_VIEW_SCALE,
                        max_distance=500 * PLAYER_VIEW_SCALE
                    )
                    bullets.append(new_bullet)

                eject_angle = angle_radians + math.radians(90 + random.uniform(-15, 15))
                eject_speed = 1
                vx = math.cos(eject_angle) * eject_speed
                vy = math.sin(eject_angle) * eject_speed

                scatter_x = bullet_world_x
                scatter_y = bullet_world_y

                scatter = ScatteredBullet(
                    scatter_x,
                    scatter_y,
                    vx,
                    vy,
                    original_cartridge_image,
                    scale=1.5,
                )

                scattered_bullets.append(scatter)
            else:
                direction_x = math.cos(angle_radians)
                direction_y = math.sin(angle_radians)

                bullet_world_x = world_x + player_rect.centerx + direction_x * spawn_offset + offset_dx
                bullet_world_y = world_y + player_rect.centery + direction_y * spawn_offset + offset_dy
                target_world_x = world_x + mouse_x
                target_world_y = world_y + mouse_y

                new_bullet = Bullet(
                    bullet_world_x,
                    bullet_world_y,
                    target_world_x,
                    target_world_y,
                    spread_angle,
                    original_bullet_image,
                    speed=10 * PLAYER_VIEW_SCALE,
                    max_distance=2000 * PLAYER_VIEW_SCALE
                )

                bullets.append(new_bullet)

                eject_angle = angle_radians + math.radians(90 + random.uniform(-15, 15))
                eject_speed = 1
                vx = math.cos(eject_angle) * eject_speed
                vy = math.sin(eject_angle) * eject_speed

                scatter_x = bullet_world_x
                scatter_y = bullet_world_y

                scattered_bullets.append(ScatteredBullet(scatter_x, scatter_y, vx, vy, original_cartridge_image))

            shake_timer = 10
            last_shot_time = current_time

    recoil_velocity += 1.5
    recoil_offset += recoil_velocity
    if recoil_offset > 0:
        recoil_offset = 0
        recoil_velocity = 0
        recoil_in_progress = False
        allow_sprint = True

    delta_seconds = clock.get_time() / 1000.0
    if shake_timer > 0:
        shake_elapsed += delta_seconds
        ratio = shake_timer / shake_timer_max
        current_magnitude = shake_magnitude * ratio
        shake_offset_x = math.sin(shake_elapsed * shake_speed) * current_magnitude
        shake_offset_y = math.cos(shake_elapsed * shake_speed) * current_magnitude
        shake_timer -= 1
    else:
        shake_offset_x = 0
        shake_offset_y = 0

    bullets = [b for b in bullets if not getattr(b, "to_remove", False)]

    if config.combat_state and all(not enemy.alive for enemy in enemies):
        config.combat_state = False
        config.combat_enabled = False
        print("[DEBUG] Combat END. Player can go back to tunnel.")
        for wall in combat_walls:
            if wall in obstacle_manager.combat_obstacles:
                obstacle_manager.combat_obstacles.remove(wall)
        combat_walls.clear()
        for info in combat_walls_info:
            info["state"] = "hiding"
            info["target_pos"] = info["start_pos"]

    screen.fill((0, 0, 0))

    world.draw_full(
        screen,
        world_x,
        world_y,
        shake_offset_x,
        shake_offset_y,
        combat_walls_info,
        obstacle_manager,
        expansion
    )

    for scatter in scattered_bullets[:]:
        scatter.update()
        if scatter.alpha <= 0:
            scattered_bullets.remove(scatter)
        else:
            scatter.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    for enemy in enemies:
        for scatter in enemy.scattered_bullets[:]:
            scatter.update()
            if scatter.alpha <= 0:
                enemy.scattered_bullets.remove(scatter)
            else:
                scatter.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    for blood in blood_effects[:]:
        blood.update()
        if blood.alpha <= 0:
            blood_effects.remove(blood)

    for blood in blood_effects:
        blood.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    obstacle_manager.draw_non_trees(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    for enemy in enemies:
        enemy.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y, shake_offset_x, shake_offset_y)

    for bullet in bullets[:]:
        bullet.update(obstacle_manager)
        bullet.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    for bullet in config.global_enemy_bullets[:]:
        bullet.update(obstacle_manager)

        if check_circle_collision(
            bullet.collider.center,
            bullet.collider.size if isinstance(bullet.collider.size, (int, float)) else 5.0,
            player_center,
            player_radius
        ):
            player_hp -= 20
            damage_flash_alpha = 255
            shake_timer = shake_timer_max
            shake_elapsed = 0.0
            shake_magnitude = 3

            bullet.to_remove = True
            config.global_enemy_bullets.remove(bullet)
            continue

        if bullet.is_offscreen(SCREEN_WIDTH, SCREEN_HEIGHT, world_x, world_y):
            config.global_enemy_bullets.remove(bullet)
            continue

        if getattr(bullet, "to_remove", False):
            config.global_enemy_bullets.remove(bullet)
            continue

        bullet.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    player_center_world = (
        world_x + player_rect.centerx,
        world_y + player_rect.centery
    )
    obstacle_manager.draw_trees(screen, world_x - shake_offset_x, world_y - shake_offset_y, player_center_world, enemies)

    # 빨간색 선 히트박스 보이기
    # for obs in obstacles_to_check:
    #     for c in obs.colliders:
    #         c.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y, (obs.world_x, obs.world_y))

    hp_bar_width = 300
    hp_bar_height = 30
    display_width, display_height = screen.get_size()
    hp_bar_x = display_width // 2 - hp_bar_width // 2
    hp_bar_y = display_height - 60
    hp_ratio = max(0, player_hp / player_hp_max)
    current_width = int(hp_bar_width * hp_ratio)
    pygame.draw.rect(screen, (80, 80, 80), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (hp_bar_x, hp_bar_y, current_width, hp_bar_height))
    hp_text = DEBUG_FONT.render(f"HP: {player_hp}", True, (255, 255, 255))
    screen.blit(hp_text, (hp_bar_x + hp_bar_width + 10, hp_bar_y))
    display_w, display_h = screen.get_size()

    if damage_flash_alpha > 0:
        display_w, display_h = screen.get_size()
        overlay = pygame.Surface((display_w, display_h), pygame.SRCALPHA)

        border_thickness = 40

        for i in range(border_thickness):
            alpha = int(damage_flash_alpha * (1 - i / border_thickness))
            color = (255, 0, 0, alpha)

            overlay.fill(color, rect=(i, i, display_w - i * 2, 1))
            overlay.fill(color, rect=(i, display_h - i - 1, display_w - i * 2, 1))
            overlay.fill(color, rect=(i, i, 1, display_h - i * 2))
            overlay.fill(color, rect=(display_w - i - 1, i, 1, display_h - i * 2))

        screen.blit(overlay, (0, 0))
        damage_flash_alpha = max(0, damage_flash_alpha - damage_flash_fade_speed)


    for bullet in bullets[:]:
        bullet.update(obstacle_manager)
        if getattr(bullet, "to_remove", False):
            bullet.to_remove = True
            continue

        bullet_center_world = bullet.collider.center

        bullet_radius = 5.0

        if bullet.collider:
            if bullet.collider.shape == "circle":
                if isinstance(bullet.collider.size, tuple):
                    bullet_radius = float(bullet.collider.size[0])
                else:
                    bullet_radius = float(bullet.collider.size)
            elif bullet.collider.shape == "ellipse":
                bullet_radius = float(max(bullet.collider.size))
            elif bullet.collider.shape == "rectangle":
                w, h = bullet.collider.size
                bullet_radius = max(math.sqrt((w / 2) ** 2 + (h / 2) ** 2), 5.0)

        hit = False
        if config.combat_state:
            for enemy in enemies[:]:
                enemy_center_world = (enemy.world_x, enemy.world_y)
                if check_circle_collision(
                    bullet_center_world,
                    bullet_radius,
                    enemy_center_world,
                    enemy.radius
                ):
                    if current_weapon == 1:
                        damage = 30
                    elif current_weapon == 2:
                        damage = 20
                    elif current_weapon == 3:
                        damage = 10
                    else:
                        damage = 30
                    enemy.hit(damage, blood_effects)
                    if not enemy.alive:
                        enemies.remove(enemy)
                        blood_effects.append(
                            ScatteredBlood(enemy.world_x, enemy.world_y)
                        )
                    bullet.to_remove = True
                    hit = True
                    break

        if hit:
            bullet.to_remove = True
            continue

        if bullet.is_offscreen(SCREEN_WIDTH, SCREEN_HEIGHT, world_x, world_y):
            bullet.to_remove = True
            continue
    
    if not changing_room:
        slide_direction = None
        if world_x <= -half_screen_width - expansion:
            slide_direction = "right"
            next_dir = "west"
        elif world_x >= effective_bg_width - half_screen_width + expansion:
            slide_direction = "left"
            next_dir = "east"
        elif world_y <= -half_screen_height - expansion:
            slide_direction = "down"
            next_dir = "north"
        elif world_y >= effective_bg_height - half_screen_height + expansion:
            slide_direction = "up"
            next_dir = "south"
        else:
            slide_direction = None

    def render_game_frame():
        screen.fill((0, 0, 0))

        world.draw_full(
            screen, world_x, world_y, shake_offset_x, shake_offset_y,
            combat_walls_info, obstacle_manager, expansion
        )

        player_center_world = (
            world_x + player_rect.centerx,
            world_y + player_rect.centery
        )

        obstacle_manager.draw_non_trees(screen, world_x, world_y)
        for blood in blood_effects:
            blood.draw(screen, world_x, world_y)
        for enemy in enemies:
            enemy.draw(screen, world_x, world_y, shake_offset_x, shake_offset_y)

        for bullet in bullets:
            bullet.draw(screen, world_x, world_y)
        for bullet in config.global_enemy_bullets:
            bullet.draw(screen, world_x, world_y)

        obstacle_manager.draw_trees(screen, world_x, world_y, player_center_world, enemies)

        display_w, display_h = screen.get_size()
        hp_ratio = max(0, player_hp / player_hp_max)
        hp_bar_width = 300
        hp_bar_height = 30
        hp_bar_x = display_w // 2 - hp_bar_width // 2
        hp_bar_y = display_h - 60
        current_width = int(hp_bar_width * hp_ratio)

        pygame.draw.rect(screen, (80, 80, 80), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (hp_bar_x, hp_bar_y, current_width, hp_bar_height))

        screen.blit(DEBUG_FONT.render(f"Speed: {math.sqrt(world_vx ** 2 + world_vy ** 2):.2f}", True, (255, 255, 255)), (10, 10))
        screen.blit(DEBUG_FONT.render(f"Weapon: gun{current_weapon}", True, (255, 255, 255)), (10, 40))
        screen.blit(DEBUG_FONT.render(f"Kills: {kill_count}", True, (255, 255, 255)), (10, 70))

    if slide_direction:
        def draw_new_room():
            change_room(next_dir)
            render_game_frame()
        old_surface = screen.copy()
        swipe_curtain_transition(screen, old_surface, draw_new_room, direction=slide_direction, duration=0.5)
        continue

    screen.blit(rotated_gun_image, rotated_gun_rect.move(shake_offset_x, shake_offset_y))
    screen.blit(rotated_player_image, rotated_player_rect.move(shake_offset_x, shake_offset_y))

    speed = math.sqrt(world_vx ** 2 + world_vy ** 2)
    text_surface = DEBUG_FONT.render(f"Speed: {speed:.2f}", True, (255, 255, 255))
    screen.blit(text_surface, (10, 10))

    weapon_name = f"gun{current_weapon}"
    weapon_surface = DEBUG_FONT.render(f"Weapon: {weapon_name}", True, (255, 255, 255))
    screen.blit(weapon_surface, (10, 40))

    kill_surface = DEBUG_FONT.render(f"Kills: {kill_count}", True, (255, 255, 255))
    screen.blit(kill_surface, (10, 70))

    fps = clock.get_fps()
    fps_surface = DEBUG_FONT.render(f"FPS: {fps:.1f}", True, (255, 255, 0))
    screen.blit(fps_surface, (10, 100))

    draw_minimap(screen, grid, current_room_pos)

    cursor_rect = cursor_image.get_rect(center=(mouse_x, mouse_y))
    screen.blit(cursor_image, cursor_rect)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()