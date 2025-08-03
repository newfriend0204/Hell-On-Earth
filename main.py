import pygame
import math
import random
from config import *
import config
from asset_manager import load_images, load_weapon_assets
from sound_manager import load_sounds
from entities import Bullet, ScatteredBullet, ScatteredBlood, ExplosionEffectPersistent, FieldWeapon
from collider import Collider
from renderer_3d import Renderer3D
from obstacle_manager import ObstacleManager
from ai import ENEMY_CLASSES
from weapon import WEAPON_CLASSES
from ui import draw_weapon_detail_ui, handle_tab_click, draw_status_tab
import world
from maps import MAPS, FIGHT_MAPS, BOSS_MAPS

# 맵 상태 초기화
CURRENT_MAP = MAPS[0]
stage_settings = STAGE_DATA[CURRENT_STAGE]
world.MIN_F_ROOMS = stage_settings["min_f_rooms"]
world.MAX_F_ROOMS = stage_settings["max_f_rooms"]
grid = world.generate_map()
grid = world.place_acquire_rooms(grid, count=stage_settings["acquire_rooms"])
world.initialize_room_states(grid)
world.print_grid(grid)

pygame.init()
pygame.font.init()
pygame.mixer.init()

DEBUG_FONT = pygame.font.SysFont('malgungothic', 24)
BASE_DIR = os.path.dirname(__file__)
ASSET_DIR = os.path.join(BASE_DIR, "Asset")
FONT_PATH = os.path.join(ASSET_DIR, "Font", "SUIT-Regular.ttf")
KOREAN_FONT_18 = pygame.font.Font(FONT_PATH, 18)

pygame.mouse.set_visible(False)

#screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hell On Earth")

images = load_images()
sounds = load_sounds()
config.images = images
config.dropped_items = []
weapon_assets = load_weapon_assets(images)
START_WEAPONS = [
    WEAPON_CLASSES[4],
    WEAPON_CLASSES[5],
    WEAPON_CLASSES[6],
    WEAPON_CLASSES[7],
]

original_player_image = images["player"]
original_bullet_image = images["bullet1"]
original_cartridge_image = images["cartridge_case1"]
cursor_image = images["cursor"]
background_image = images["background"]
background_rect = background_image.get_rect()

obstacle_manager = ObstacleManager(
    # 장애물 관리자 초기화
    obstacle_images=images["obstacles"],
    obstacle_masks=images["obstacle_masks"],
    map_width=BG_WIDTH,
    map_height=BG_HEIGHT,
    min_scale=1.3,
    max_scale=2.0,
    num_obstacles_range=(5, 8)
)
obstacle_manager.generate_obstacles_from_map(CURRENT_MAP)

expansion = 350 * PLAYER_VIEW_SCALE

hole_width = 300 * PLAYER_VIEW_SCALE
hole_height = 300 * PLAYER_VIEW_SCALE

wall_thickness = 10 * PLAYER_VIEW_SCALE

world_instance = world.World(
    # 월드(맵) 객체 생성
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

s_pos = None
# 시작 위치(S) 찾기
for y, row in enumerate(grid):
    for x, cell in enumerate(row):
        if cell == 'S':
            s_pos = (x, y)
            break
    if s_pos:
        break
current_room_pos = list(s_pos)
world.reveal_neighbors(s_pos[0], s_pos[1], grid)

north_hole_open = False
south_hole_open = False
west_hole_open = False
east_hole_open = False

sx, sy = s_pos
WIDTH, HEIGHT = world.get_map_dimensions()

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

effective_bg_width = world_instance.effective_bg_width
effective_bg_height = world_instance.effective_bg_height

map_width = effective_bg_width
map_height = effective_bg_height

left_wall_width = (map_width / 2) - (hole_width / 2)
right_wall_width = left_wall_width
top_wall_height = (map_height / 2) - (hole_height / 2)
bottom_wall_height = top_wall_height

world_instance.left_wall_width = left_wall_width
world_instance.top_wall_height = top_wall_height

if CURRENT_MAP is MAPS[0]:
    # 시작 맵이면 중앙 스폰
    player_world_x, player_world_y = world_instance.get_spawn_point(
        direction=None,
        is_start_map=True
    )
else:
    spawn_direction = "west"
    player_world_x, player_world_y = world_instance.get_spawn_point(
        spawn_direction,
        margin=50
    )

field_weapons = []
room_field_weapons = {}
#디버그-필드에 무기 놓는 코드
# start_weapon = FieldWeapon(
#     WEAPON_CLASSES[1],
#     SCREEN_WIDTH//2,
#     SCREEN_HEIGHT//2,
#     weapon_assets,
#     sounds
# )
# field_weapons.append(start_weapon)

world_x = player_world_x - SCREEN_WIDTH // 2
world_y = player_world_y - SCREEN_HEIGHT // 2

walls = world_instance.generate_walls(
    # 기본 벽 생성
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
config.bullets = bullets

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
tab_menu_selected = 0
tab_rects = []
fade_in_after_resume = False
selected_tab = 1
weapon_tab_open = True

renderer = Renderer3D(screen)

clock = pygame.time.Clock()
running = True

player_radius = int(30 * PLAYER_VIEW_SCALE)

player_hp_max = 200
player_hp = player_hp_max
last_hp_visual = player_hp * 1.0

def consume_ammo(cost):
    global ammo_gauge
    ammo_gauge -= cost

current_weapon_index = 0
ammo_gauge_max = 300
ammo_gauge = ammo_gauge_max 
last_ammo_visual = ammo_gauge * 1.0

current_boss = None
last_boss_hp_visual = 0

damage_flash_alpha = 0
damage_flash_fade_speed = 5

blood_effects = []
config.blood_effects = blood_effects
config.effects = []

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

config.bullets = bullets
config.scattered_bullets = scattered_bullets
config.PLAYER_VIEW_SCALE = PLAYER_VIEW_SCALE  

weapon_ui_cache = {
    "slot_surface": None,
    "numbers": [],
    "resized_images": {}
}

space_pressed_last_frame = False

def try_pickup_weapon():
    # 스페이스 무기 줍기 단발 입력을 이벤트로 처리
    global weapons, field_weapons, current_weapon_index, changing_weapon, change_weapon_target, change_animation_timer, previous_distance, target_distance, current_distance
    player_center_x = player_rect.centerx + world_x
    player_center_y = player_rect.centery + world_y
    for fw in field_weapons[:]:
        if fw.is_player_near(player_center_x, player_center_y):
            sounds["swap_gun"].play()

            if len(weapons) < 4:
                new_weapon = fw.weapon_class.create_instance(
                    weapon_assets, sounds, lambda: ammo_gauge,
                    consume_ammo, get_player_world_position
                )
                weapons.append(new_weapon)
                current_weapon_index = len(weapons) - 1
            else:
                current_weapon_class = weapons[current_weapon_index].__class__
                dropped_fw = FieldWeapon(
                    current_weapon_class, fw.world_x, fw.world_y, weapon_assets, sounds
                )
                field_weapons.append(dropped_fw)
                room_key = tuple(current_room_pos)
                if room_key not in room_field_weapons:
                    room_field_weapons[room_key] = []
                room_field_weapons[room_key].append(dropped_fw)
                new_weapon = fw.weapon_class.create_instance(
                    weapon_assets, sounds, lambda: ammo_gauge,
                    consume_ammo, get_player_world_position
                )
                weapons[current_weapon_index] = new_weapon

            changing_weapon = True
            change_weapon_target = current_weapon_index
            change_animation_timer = 0.0
            previous_distance = current_distance
            target_distance = weapons[current_weapon_index].distance_from_center

            # ★ 방 전용 무기 목록에서도 제거
            room_key = tuple(current_room_pos)
            if room_key in room_field_weapons and fw in room_field_weapons[room_key]:
                room_field_weapons[room_key].remove(fw)

            field_weapons.remove(fw)
            break

def damage_player(amount):
    # 플레이어 피해 처리
    global player_hp, damage_flash_alpha, shake_timer, shake_elapsed, shake_magnitude
    player_hp = max(0, player_hp - amount)

    damage_flash_alpha = 255
    shake_timer = shake_timer_max
    shake_elapsed = 0.0
    shake_magnitude = 3

def get_player_world_position():
    return (
        world_x + player_rect.centerx,
        world_y + player_rect.centery
    )

def init_weapon_ui_cache(weapons):
    # 무기 UI 슬롯 이미지 캐싱
    slot_width = 92
    slot_height = 54
    slot_alpha = 180

    surface = pygame.Surface((slot_width, slot_height), pygame.SRCALPHA)
    surface = pygame.Surface((slot_width, slot_height), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))
    pygame.draw.rect(surface, (200, 200, 200, slot_alpha), (0, 0, slot_width, slot_height), border_radius=10)
    weapon_ui_cache["slot_surface"] = surface

    font = pygame.font.SysFont('arial', 18)
    weapon_ui_cache["numbers"] = [font.render(str(i + 1), True, (255, 255, 255)) for i in range(4)]

    weapon_ui_cache["resized_images"].clear()
    for weapon in weapons:
        img = weapon.front_image
        img_w, img_h = img.get_size()
        scale = min(slot_width / img_w, slot_height / img_h) * 0.85
        new_size = (int(img_w * scale), int(img_h * scale))
        scaled_img = pygame.transform.smoothscale(img, new_size)
        weapon_ui_cache["resized_images"][id(img)] = scaled_img

weapons = [
    cls.create_instance(
        weapon_assets,
        sounds,
        lambda: ammo_gauge,
        consume_ammo,
        get_player_world_position
    )
    for cls in START_WEAPONS
]
init_weapon_ui_cache(weapons)

def advance_to_next_stage():
    # 현재 스테이지를 다음 스테이지로 전환하고 시작방으로 이동
    visited_f_rooms.clear()

    import config
    stage_order = list(STAGE_DATA.keys())
    idx = stage_order.index(config.CURRENT_STAGE)

    if idx >= len(stage_order) - 1:
        print("[DEBUG] 마지막 스테이지입니다. 더 이상 진행할 수 없습니다.")
        return

    next_stage = stage_order[idx + 1]
    config.CURRENT_STAGE = next_stage
    print(f"[DEBUG] 스테이지 전환: {config.CURRENT_STAGE} → {next_stage}")

    stage_settings = STAGE_DATA[next_stage]
    world.MIN_F_ROOMS = stage_settings["min_f_rooms"]
    world.MAX_F_ROOMS = stage_settings["max_f_rooms"]

    global grid
    grid = world.generate_map()
    world.place_acquire_rooms(grid, count=stage_settings["acquire_rooms"])
    world.initialize_room_states(grid)
    world.print_grid(grid)

    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == 'S':
                world.reveal_neighbors(x, y, grid)
                break

    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == 'S':
                current_room_pos[0] = x
                current_room_pos[1] = y
                change_room(None)
                return
            
def change_room(direction):
    # 방 전환 처리
    global current_room_pos, CURRENT_MAP, world_instance, world_x, world_y
    global enemies, changing_room, effective_bg_width, effective_bg_height, current_boss

    WIDTH, HEIGHT = world.get_map_dimensions()
    changing_room = True

    if direction is None:
        new_x, new_y = current_room_pos
        dx, dy = 0, 0
        spawn_direction = None
    else:
        dx, dy = DIRECTION_OFFSET[direction]
        new_x = current_room_pos[0] + dx
        new_y = current_room_pos[1] + dy
        spawn_direction = SPAWN_FROM_OPPOSITE[direction]

    if not (0 <= new_x < WIDTH and 0 <= new_y < HEIGHT):
        print("[DEBUG] 이동 불가: 맵 경계 밖")
        changing_room = False
        return

    new_room_type = grid[new_y][new_x]

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
                "cleared": False,
                "enemy_types": []
            }
        fight_map_index = visited_f_rooms[room_key].get("fight_map_index", random.randint(0, len(FIGHT_MAPS) - 1))
        CURRENT_MAP = FIGHT_MAPS[fight_map_index]

        if visited_f_rooms[room_key]["cleared"]:
            CURRENT_MAP = {
                "obstacles": CURRENT_MAP["obstacles"],
                "enemy_infos": [],
                "crop_rect": CURRENT_MAP["crop_rect"]
            }
            config.combat_state = False
            config.combat_enabled = False

    elif new_room_type == 'E':
        stage_boss_index = STAGE_DATA[config.CURRENT_STAGE]["boss_map"]
        CURRENT_MAP = BOSS_MAPS[stage_boss_index]
        config.combat_state = True
        config.combat_enabled = True
    else:
        CURRENT_MAP = MAPS[0]

    current_room_pos = [new_x, new_y]
    sx, sy = new_x, new_y
    WIDTH, HEIGHT = world.get_map_dimensions()

    north_hole_open = (sy > 0 and grid[sy - 1][sx] != 'N')
    south_hole_open = (sy < HEIGHT - 1 and grid[sy + 1][sx] != 'N')
    west_hole_open = (sx > 0 and grid[sy][sx - 1] != 'N')
    east_hole_open = (sx < WIDTH - 1 and grid[sy][sx + 1] != 'N')

    obstacle_manager.static_obstacles.clear()
    obstacle_manager.generate_obstacles_from_map(CURRENT_MAP)
    config.obstacle_manager = obstacle_manager

    new_world = world.World(
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

    if new_room_type == 'A':
        acquire_index = random.randint(2, 2)
        CURRENT_MAP = MAPS[acquire_index]
        config.combat_state = False
        config.combat_enabled = False

        world.reveal_neighbors(new_x, new_y, grid)

        room_key = (new_x, new_y)
        if room_key not in room_field_weapons:
            center_x = new_world.effective_bg_width / 2
            center_y = new_world.effective_bg_height / 2
            spacing = 150 * PLAYER_VIEW_SCALE

            weapon_classes = random.sample(WEAPON_CLASSES, 2)
            weapons_in_room = []
            for i, weapon_class in enumerate(weapon_classes):
                fw = FieldWeapon(
                    weapon_class,
                    center_x + (i - 0.5) * spacing * 2,
                    center_y,
                    weapon_assets,
                    sounds
                )
                weapons_in_room.append(fw)
            room_field_weapons[room_key] = weapons_in_room

        field_weapons.clear()
        field_weapons.extend(room_field_weapons[room_key])
    else:
        field_weapons.clear()

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

    if spawn_direction is None:
        spawn_world_x, spawn_world_y = new_world.get_spawn_point(
            direction=None,
            is_start_map=True
        )
    else:
        spawn_world_x, spawn_world_y = new_world.get_spawn_point(
            direction=spawn_direction,
            margin=275
        )
        if direction in ("west", "east"):
            spawn_world_y += dy_from_center
        else:
            spawn_world_x += dx_from_center

    world_instance = new_world
    world_x = spawn_world_x - player_center_x
    world_y = spawn_world_y - player_center_y

    effective_bg_width = world_instance.effective_bg_width
    effective_bg_height = world_instance.effective_bg_height

    walls = world_instance.generate_walls(
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
    config.dropped_items.clear()
    config.global_enemy_bullets.clear()
    config.effects.clear()
    for enemy in enemies:
        if hasattr(enemy, "scattered_bullets"):
            enemy.scattered_bullets.clear()

    enemies = []
    rank_min, rank_max = STAGE_DATA[config.CURRENT_STAGE]["enemy_rank_range"]

    enemies_by_rank = {}
    for cls in ENEMY_CLASSES:
        rank = getattr(cls, "rank", None)
        if rank is not None:
            enemies_by_rank.setdefault(rank, []).append(cls)

    room_key = (new_x, new_y)
    for idx, info in enumerate(CURRENT_MAP["enemy_infos"]):
        ex = info["x"] * PLAYER_VIEW_SCALE
        ey = info["y"] * PLAYER_VIEW_SCALE
        if "enemy_type" in info:
            enemy_type = info["enemy_type"].lower()
            for cls in ENEMY_CLASSES:
                if cls.__name__.lower() == enemy_type:
                    enemy = cls(
                        world_x=ex,
                        world_y=ey,
                        images=images,
                        sounds=sounds,
                        map_width=map_width,
                        map_height=map_height,
                        damage_player_fn=damage_player,
                        kill_callback=increment_kill_count
                    )
                    enemies.append(enemy)
                    if enemy_type in ("boss1", "boss2"):
                        current_boss = enemy
                    break
        else:
            if "enemy_types" in visited_f_rooms[room_key] and len(visited_f_rooms[room_key]["enemy_types"]) > idx:
                enemy_class_name = visited_f_rooms[room_key]["enemy_types"][idx]
                enemy_class = next(cls for cls in ENEMY_CLASSES if cls.__name__ == enemy_class_name)
            else:
                possible_ranks = [r for r in range(rank_min, rank_max + 1) if r in enemies_by_rank]
                if not possible_ranks:
                    continue
                rank_choice = random.choice(possible_ranks)
                valid_classes = [c for c in enemies_by_rank[rank_choice] if not c.__name__.lower().startswith("boss")]
                if not valid_classes:
                    continue
                enemy_class = random.choice(valid_classes)
                visited_f_rooms[room_key]["enemy_types"].append(enemy_class.__name__)
            enemy = enemy_class(
                world_x=ex,
                world_y=ey,
                images=images,
                sounds=sounds,
                map_width=map_width,
                map_height=map_height,
                damage_player_fn=damage_player,
                kill_callback=increment_kill_count
            )
            enemies.append(enemy)

    if not any("enemy_type" in e_info and e_info["enemy_type"] in ("boss1", "boss2") for e_info in CURRENT_MAP["enemy_infos"]):
        current_boss = None

    config.all_enemies = enemies

    if len(CURRENT_MAP["enemy_infos"]) == 0:
        config.combat_state = False
        config.combat_enabled = False
    else:
        config.combat_state = False
        config.combat_enabled = True

    sounds["room_move"].play()
    print(f"[DEBUG] Entered room at ({new_x}, {new_y}), room_state: {world.room_states[new_y][new_x]}")

    pygame.time.set_timer(pygame.USEREVENT + 1, 200)

def increment_kill_count():
    # 처치 수 증가
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
    # 커튼 효과 방 전환
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
    # 미니맵 그리기
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
    background_surface.fill((0, 0, 0, 0))
    pygame.draw.rect(
        background_surface,
        (100, 100, 100, 200),
        background_surface.get_rect(),
        border_radius=12
    )
    screen.blit(background_surface, (start_x - background_margin, start_y - background_margin))

    connectable_states = {1, 3, 5, 6}

    for y in range(grid_height):
        for x in range(grid_width):
            state = world.room_states[y][x]

            cx = start_x + x * (mini_tile + tile_gap) + mini_tile // 2
            cy = start_y + y * (mini_tile + tile_gap) + mini_tile // 2

            if x + 1 < grid_width and state in connectable_states and world.room_states[y][x + 1] in connectable_states:
                cx2 = start_x + (x + 1) * (mini_tile + tile_gap) + mini_tile // 2
                pygame.draw.rect(screen, (50, 50, 50),
                    pygame.Rect(min(cx, cx2), cy - 2, abs(cx2 - cx), 4))

            if y + 1 < grid_height and state in connectable_states and world.room_states[y + 1][x] in connectable_states:
                cy2 = start_y + (y + 1) * (mini_tile + tile_gap) + mini_tile // 2
                pygame.draw.rect(screen, (50, 50, 50),
                    pygame.Rect(cx - 2, min(cy, cy2), 4, abs(cy2 - cy)))

    for y in range(grid_height):
        for x in range(grid_width):
            state = world.room_states[y][x]
            color = None
            alpha = 255

            if state in (0, 2, 4, 7):
                color = (50, 50, 50)
                alpha = 20
            elif state == 1:
                color = (120, 255, 120)
            elif state in (3, 9):
                color = (255, 120, 120)
            elif state == 5:
                color = (50, 50, 50)
            elif state == 6:
                color = (160, 160, 160)
            elif state == 8:
                color = (255, 255, 150)

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

    pygame.draw.rect(screen, (255, 0, 0), (cursor_center_x - half, cursor_center_y - half, bar, edge))
    pygame.draw.rect(screen, (255, 0, 0), (cursor_center_x - half, cursor_center_y - half, edge, bar))
    pygame.draw.rect(screen, (255, 0, 0), (cursor_center_x + half - bar, cursor_center_y - half, bar, edge))
    pygame.draw.rect(screen, (255, 0, 0), (cursor_center_x + half - edge, cursor_center_y - half, edge, bar))
    pygame.draw.rect(screen, (255, 0, 0), (cursor_center_x - half, cursor_center_y + half - edge, bar, edge))
    pygame.draw.rect(screen, (255, 0, 0), (cursor_center_x - half, cursor_center_y + half - bar, edge, bar))
    pygame.draw.rect(screen, (255, 0, 0), (cursor_center_x + half - bar, cursor_center_y + half - edge, bar, edge))
    pygame.draw.rect(screen, (255, 0, 0), (cursor_center_x + half - edge, cursor_center_y + half - bar, edge, bar))

def draw_weapon_ui(screen, weapons, current_weapon_index):
    # 무기 UI 그리기
    slot_width = 92
    slot_height = 54
    padding = 8
    offset_y_selected = -10
    screen_width, screen_height = screen.get_size()
    total_width = 4 * slot_width + 3 * padding
    start_x = screen_width - total_width - 20
    y_base = screen_height - slot_height - 20

    slot_surface = weapon_ui_cache["slot_surface"]
    numbers = weapon_ui_cache["numbers"]
    resized = weapon_ui_cache["resized_images"]

    mouse_pos = pygame.mouse.get_pos()
    tooltip_weapon_name = None

    if changing_weapon:
        t = min(change_animation_timer / change_animation_time, 1.0)
        eased_t = 1 - (1 - t) ** 2
    else:
        t = 1.0
        eased_t = 1.0

    for i in range(4):
        x = start_x + i * (slot_width + padding)

        if changing_weapon:
            if i == current_weapon_index:
                y_offset = int(offset_y_selected * (1 - t))
            elif i == change_weapon_target:
                y_offset = int(offset_y_selected * eased_t)
            else:
                y_offset = 0
        else:
            if i == current_weapon_index:
                y_offset = offset_y_selected
            else:
                y_offset = 0

        y = y_base + y_offset

        rect = pygame.Rect(x, y, slot_width, slot_height)
        screen.blit(slot_surface, (x, y))

        if i < len(weapons):
            weapon = weapons[i]
            img = weapon.front_image
            img_id = id(img)

            if img_id not in resized:
                img_w, img_h = img.get_size()
                scale = min(slot_width / img_w, slot_height / img_h) * 0.85
                new_size = (int(img_w * scale), int(img_h * scale))
                scaled_img = pygame.transform.smoothscale(img, new_size)
                resized[img_id] = scaled_img

            scaled_img = resized[img_id]
            img_rect = scaled_img.get_rect(center=(x + slot_width // 2, y + slot_height // 2))
            screen.blit(scaled_img, img_rect)

            if rect.collidepoint(mouse_pos):
                tooltip_weapon_name = weapon.name

        screen.blit(numbers[i], (x + 5, y + slot_height - numbers[i].get_height() - 5))

        should_draw_border = False
        if changing_weapon:
            if i == change_weapon_target:
                should_draw_border = True
        else:
            if i == current_weapon_index:
                should_draw_border = True

        if should_draw_border:
            tier_colors = {
                1: (255, 255, 255),
                2: (0, 255, 0),
                3: (0, 128, 255),
                4: (160, 32, 240),
                5: (255, 255, 0),
            }
            tier = getattr(weapons[i], "tier", 1)
            border_color = tier_colors.get(tier, (255, 255, 255))
            pygame.draw.rect(screen, border_color, (x, y, slot_width, slot_height), 4, border_radius=10)

    if tooltip_weapon_name and not config.combat_state:
        tooltip_font = KOREAN_FONT_18
        tooltip_surface = tooltip_font.render(tooltip_weapon_name, True, (255, 255, 255))
        tooltip_bg = pygame.Surface((tooltip_surface.get_width() + 10, tooltip_surface.get_height() + 6), pygame.SRCALPHA)
        tooltip_bg.fill((0, 0, 0))
        tooltip_x = mouse_pos[0] + 10
        tooltip_y = mouse_pos[1] - tooltip_surface.get_height() - 14
        screen.blit(tooltip_bg, (tooltip_x, tooltip_y))
        screen.blit(tooltip_surface, (tooltip_x + 5, tooltip_y + 3))

def draw_boss_hp_bar(screen, boss, last_boss_hp_visual):
    bar_width = 600
    bar_height = 28
    x = (SCREEN_WIDTH - bar_width) // 2
    y = 20
    border_radius = bar_height // 3

    # 배경
    bg_surface = pygame.Surface((bar_width + 6, bar_height + 4), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, (255, 255, 255, 80), (0, 0, bar_width + 6, bar_height + 4), border_radius=border_radius + 2)
    screen.blit(bg_surface, (x - 3, y - 2))

    # HP 보간
    smoothing_speed = 0.5
    interpolated_hp = last_boss_hp_visual + (boss.hp - last_boss_hp_visual) * smoothing_speed

    ratio = max(0.0, interpolated_hp / boss.max_hp)

    # 색상 조건 변경
    if ratio >= 0.75:
        color = (0, 200, 0)       # 초록색
    elif ratio >= 0.50:
        color = (200, 200, 0)     # 노란색
    elif ratio >= 0.25:
        color = (255, 165, 0)     # 주황색
    else:
        color = (200, 0, 0)       # 빨간색

    filled_width = int(bar_width * ratio)
    pygame.draw.rect(screen, color, (x, y, filled_width, bar_height), border_radius=border_radius)

    # 텍스트 (한국어 폰트)
    text_surface = KOREAN_FONT_18.render(f"보스 HP: {int(boss.hp)}/{boss.max_hp}", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y + bar_height // 2))
    screen.blit(text_surface, text_rect)

    return interpolated_hp
def draw_hp_bar_remodeled(surface, current_hp, max_hp, pos, size, last_hp_drawn):
    x, y = pos
    width, height = size
    border_radius = height // 3

    bg_surface = pygame.Surface((width + 6, height + 4), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, (255, 255, 255, 80), (0, 0, width + 6, height + 4), border_radius=border_radius + 2)
    surface.blit(bg_surface, (x - 3, y - 2))

    smoothing_speed = 0.5
    interpolated_hp = last_hp_drawn + (current_hp - last_hp_drawn) * smoothing_speed

    ratio = max(0.0, interpolated_hp / max_hp)
    if ratio > 0.5:
        color = (0, 180, 0)
    elif ratio > 0.25:
        color = (200, 200, 0)
    else:
        color = (180, 0, 0)

    filled_width = int(width * ratio)
    pygame.draw.rect(surface, color, (x, y, filled_width, height), border_radius=border_radius)

    return interpolated_hp

def draw_ammo_bar_remodeled(surface, current_ammo, max_ammo, pos, size, last_ammo_drawn):
    x, y = pos
    width, height = size
    border_radius = height // 3

    bg_surface = pygame.Surface((width + 6, height + 4), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, (255, 255, 255, 80), (0, 0, width + 6, height + 4), border_radius=border_radius + 2)
    surface.blit(bg_surface, (x - 3, y - 2))

    smoothing_speed = 0.5
    interpolated_ammo = last_ammo_drawn + (current_ammo - last_ammo_drawn) * smoothing_speed

    ratio = max(0, interpolated_ammo / max_ammo)
    filled_width = int(width * ratio)
    bar_color = (255, 150, 0)
    pygame.draw.rect(surface, bar_color, (x, y, filled_width, height), border_radius=border_radius)

    return interpolated_ammo

enemies = []
rank_min, rank_max = STAGE_DATA[config.CURRENT_STAGE]["enemy_rank_range"]

enemies_by_rank = {}
for cls in ENEMY_CLASSES:
    rank = getattr(cls, "rank", None)
    if rank is not None:
        enemies_by_rank.setdefault(rank, []).append(cls)

room_key = tuple(current_room_pos)
visited_f_rooms.setdefault(room_key, {}).setdefault("enemy_types", [])

for idx, info in enumerate(CURRENT_MAP["enemy_infos"]):
    ex = info["x"] * PLAYER_VIEW_SCALE
    ey = info["y"] * PLAYER_VIEW_SCALE
    if "enemy_type" in info:
        # 보스맵 등 enemy_type이 있는 경우
        enemy_type = info["enemy_type"].lower()
        for cls in ENEMY_CLASSES:
            if cls.__name__.lower() == enemy_type:
                enemy = cls(
                    world_x=ex,
                    world_y=ey,
                    images=images,
                    sounds=sounds,
                    map_width=map_width,
                    map_height=map_height,
                    kill_callback=increment_kill_count
                )
                enemies.append(enemy)
                break
    else:
        if idx < len(visited_f_rooms[room_key]["enemy_types"]):
            # 기존 기록 사용
            enemy_class_name = visited_f_rooms[room_key]["enemy_types"][idx]
            enemy_class = next(cls for cls in ENEMY_CLASSES if cls.__name__ == enemy_class_name)
        else:
            # 새로 생성 후 기록
            possible_ranks = [r for r in range(rank_min, rank_max + 1) if r in enemies_by_rank]
            if not possible_ranks:
                continue
            rank_choice = random.choice(possible_ranks)
            enemy_class = random.choice(enemies_by_rank[rank_choice])
            visited_f_rooms[room_key]["enemy_types"].append(enemy_class.__name__)
        enemy = enemy_class(
            world_x=ex,
            world_y=ey,
            images=images,
            sounds=sounds,
            map_width=map_width,
            map_height=map_height,
            kill_callback=increment_kill_count
        )
        enemies.append(enemy)

if len(enemies) == 0:
    config.combat_enabled = False
    print("[DEBUG] No enemies in map. Combat disabled.")
else:
    config.combat_enabled = True
    print(f"[DEBUG] Enemies in map: {len(enemies)}. Combat enabled.")

while running:
    # 게임 루프 시작
    current_time = pygame.time.get_ticks()
    events = pygame.event.get()

    for event in events:
        # 이벤트 처리
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
                if grid[current_room_pos[1]][current_room_pos[0]] == 'E' and not config.combat_state:
                    advance_to_next_stage()
                else:
                    print("[DEBUG] 스페이스 전환 조건 불충족: E방이 아니거나 전투 중")
                player_world_x = world_x + player_rect.centerx * PLAYER_VIEW_SCALE
                player_world_y = world_y + player_rect.centery * PLAYER_VIEW_SCALE
                print(f"[DEBUG] Player world position: ({player_world_x:.2f}, {player_world_y:.2f})")
                try_pickup_weapon()
            elif event.key == pygame.K_TAB:
                paused = not paused
                if paused:
                    pygame.mouse.set_visible(True)
                    tab_menu_selected = 0
                    selected_tab = 0
                    bullets[:] = [b for b in bullets if not isinstance(b, ExplosionEffectPersistent)]
                    screen.fill((0, 0, 0))
                    world_instance.draw_full(
                        screen, world_x, world_y, shake_offset_x, shake_offset_y,
                        combat_walls_info, obstacle_manager, expansion
                    )
                    pygame.display.flip()
                else:
                    pygame.mouse.set_visible(False)
                    for bullet in bullets:
                        if isinstance(bullet, ExplosionEffectPersistent):
                            bullet.resume()
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                slot = event.key - pygame.K_1
                if 0 <= slot < len(weapons) and current_weapon_index != slot:
                    sounds["swap_gun"].play()
                    if hasattr(weapons[current_weapon_index], "on_weapon_switch"):
                        weapons[current_weapon_index].on_weapon_switch()
                    changing_weapon = True
                    change_weapon_target = slot
                    change_animation_timer = 0.0
                    previous_distance = current_distance
                    target_distance = weapons[slot].distance_from_center
            elif event.key == pygame.K_q:
                print("[DEBUG] Q pressed: Killing all enemies instantly (dev cheat)")
                cx, cy = current_room_pos
                for enemy in enemies[:]:
                    if enemy.alive:
                        enemy.hit(9999, blood_effects)  # 강제로 사망시킴
                        enemies.remove(enemy)
                room_key = (cx, cy)

                if room_key in visited_f_rooms:
                    visited_f_rooms[room_key]["cleared"] = True

                world.update_room_state_after_combat(cy, cx)

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
                if paused:
                    if hasattr(event, 'pos'):
                        clicked_tab = handle_tab_click(pygame.mouse.get_pos(), ui_tab_rects, sounds)
                        if clicked_tab is not None and clicked_tab != selected_tab:
                            selected_tab = clicked_tab
            elif event.button == 3:
                mouse_right_button_down = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_left_button_down = False
            elif event.button == 3:
                mouse_right_button_down = False

    if paused:
        # 일시정지 상태일 때 UI 처리
        screen.fill((0, 0, 0))
        world_instance.draw_full(
            screen, world_x, world_y, shake_offset_x, shake_offset_y,
            combat_walls_info, obstacle_manager, expansion
        )

        for bullet in bullets[:]:
            if isinstance(bullet, ExplosionEffectPersistent):
                if bullet.finished:
                    bullets.remove(bullet)
                continue

        if selected_tab != 0:
            ui_tab_rects = draw_weapon_detail_ui(screen, selected_tab, weapons, sounds)
        else:
            ui_tab_rects = draw_status_tab(screen, player_hp, player_hp_max, ammo_gauge, ammo_gauge_max, selected_tab, sounds)
        pygame.display.flip()
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
    player_center = (world_x + player_rect.centerx, world_y + player_rect.centery)
    weapon = weapons[current_weapon_index]
    current_weapon_instance = weapon
    
    #적 바보 만들기
    player_pos = get_player_world_position()
    for enemy in enemies:
        if config.combat_state:
            enemy.update(
                delta_time,
                world_x=world_x,
                world_y=world_y,
                player_rect=player_rect,
                enemies=enemies
            )
    config.all_enemies = enemies

    for scatter in scattered_bullets[:]:
        scatter.update()
        if scatter.alpha <= 0:
            scattered_bullets.remove(scatter)

    for effect in config.effects[:]:
        if hasattr(effect, "update"):
            effect.update()
        if getattr(effect, "finished", False):
            config.effects.remove(effect)

    if changing_weapon:
        change_animation_timer += clock.get_time() / 1000.0
        t = min(change_animation_timer / change_animation_time, 1.0)

        if t < 0.5:
            current_distance = (1.0 - (t / 0.5)) * previous_distance
        else:
            current_distance = ((t - 0.5) / 0.5) * target_distance

        if t >= 1.0:
            changing_weapon = False
            current_weapon_index = change_weapon_target
            current_weapon = current_weapon_index + 1
            weapon = weapons[current_weapon_index]
            current_distance = weapon.distance_from_center
    else:
        current_distance = weapon.distance_from_center

    keys = pygame.key.get_pressed()

    if recoil_in_progress or mouse_left_button_down:
        max_speed = normal_max_speed
    else:
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            if allow_sprint:
                max_speed = sprint_max_speed
        else:
            max_speed = normal_max_speed

    if weapon:
        max_speed *= (1 - weapon.speed_penalty)

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
        # 전투 시작 조건 체크
        if (0 <= player_center_world_x <= effective_bg_width and
            0 <= player_center_world_y <= effective_bg_height):
            config.combat_state = True
            print("[DEBUG] Combat START!")

            world.reveal_neighbors(current_room_pos[0], current_room_pos[1], grid)

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

            combat_walls = world_instance.generate_thin_combat_walls(
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
        # 플레이어-장애물 충돌 처리
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
        # 플레이어 발사체 업데이트
        if isinstance(bullet, ExplosionEffectPersistent):
            bullet.update()
        else:
            bullet.update(obstacle_manager)

        if hasattr(bullet, "finished") and bullet.finished:
            bullets.remove(bullet)
            continue
        elif getattr(bullet, "to_remove", False):
            if hasattr(bullet, "drawn_once") and not bullet.drawn_once:
                continue
            bullets.remove(bullet)
            continue

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

    config.world_x = world_x
    config.world_y = world_y
    config.player_rect = player_rect

    scaled_player_image = pygame.transform.smoothscale(
    original_player_image,
        (
            int(original_player_image.get_width() * PLAYER_VIEW_SCALE),
            int(original_player_image.get_height() * PLAYER_VIEW_SCALE)
        )
    )
    rotated_player_image = pygame.transform.rotate(scaled_player_image, -angle_degrees + 90)
    rotated_player_rect = rotated_player_image.get_rect(center=player_rect.center)

    gun_pos_x = player_rect.centerx + math.cos(angle_radians) * (current_distance + recoil_offset)
    gun_pos_y = player_rect.centery + math.sin(angle_radians) * (current_distance + recoil_offset)

    fire_delay = weapon.fire_delay
    recoil_strength = weapon.recoil_strength

    if weapon:
        if not changing_weapon:
            weapon.on_update(mouse_left_button_down, mouse_right_button_down)
            if weapon.last_shot_time == pygame.time.get_ticks():
                recoil_in_progress = True
                recoil_offset = 0
                recoil_velocity = -weapon.recoil_strength
                allow_sprint = False
                shake_timer = int(weapon.shake_strength)

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

    bullets = [
        b for b in bullets
        if not getattr(b, "to_remove", False) or (hasattr(b, "drawn_at_least_once") and not b.drawn_at_least_once)
    ]
    config.bullets = bullets

    if config.combat_state and all(not enemy.alive for enemy in enemies):
        # 전투 종료 처리
        cx, cy = current_room_pos
        room_key = (cx, cy)

        if room_key in visited_f_rooms:
            visited_f_rooms[room_key]["cleared"] = True

        world.update_room_state_after_combat(cy, cx)

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

    world_instance.draw_full(
        screen,
        world_x,
        world_y,
        shake_offset_x,
        shake_offset_y,
        combat_walls_info,
        obstacle_manager,
        expansion
    )

    # 필드 무기 표시 및 습득 처리
    player_center_x = player_rect.centerx + world_x
    player_center_y = player_rect.centery + world_y
    for fw in field_weapons[:]:
        near = fw.is_player_near(player_center_x, player_center_y)
        fw.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y, player_near=near)

    for scatter in scattered_bullets[:]:
        # 탄피 이펙트 업데이트
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
        # 피 이펙트 업데이트
        blood.update()
        if blood.alpha <= 0:
            blood_effects.remove(blood)

    for blood in blood_effects:
        blood.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    for item in config.dropped_items[:]:
        # 드롭 아이템 처리
        item.update()
        item.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)
        if item.state == "magnet" and item.is_close_to_player():
            if item.item_type == "health":
                player_hp = min(player_hp_max, player_hp + item.value)
            elif item.item_type == "ammo":
                ammo_gauge = min(ammo_gauge_max, ammo_gauge + item.value)
            config.dropped_items.remove(item)

    obstacle_manager.draw_non_trees(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    for enemy in enemies:
        enemy.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y, shake_offset_x, shake_offset_y)

    for effect in config.effects:
        if hasattr(effect, "draw"):
            effect.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    for bullet in bullets[:]:
        # 플레이어 발사체 적 충돌 처리
        if isinstance(bullet, ExplosionEffectPersistent):
            bullet.update()
            if bullet.finished:
                bullets.remove(bullet)
                continue
        else:
            bullet.update(obstacle_manager)
            if getattr(bullet, "to_remove", False):
                bullets.remove(bullet)
                continue
        bullet.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    for bullet in config.global_enemy_bullets[:]:
        # 적 발사체 업데이트 및 플레이어 충돌 체크
        bullet.update(obstacle_manager)

        if check_circle_collision(
            bullet.collider.center,
            bullet.collider.size if isinstance(bullet.collider.size, (int, float)) else 5.0,
            player_center,
            player_radius
        ):
            from entities import HomingMissile
            if isinstance(bullet, HomingMissile):
                bullet.explode()
            else:
                player_hp -= bullet.damage
                damage_flash_alpha = 255
                shake_timer = shake_timer_max
                shake_elapsed = 0.0
                shake_magnitude = 3

            bullet.to_remove = True
            if bullet in config.global_enemy_bullets:
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

    ammo_bar_pos = (80, SCREEN_HEIGHT - 80)
    ammo_bar_size = (400, 20)
    last_ammo_visual = draw_ammo_bar_remodeled(screen, ammo_gauge, ammo_gauge_max, ammo_bar_pos, ammo_bar_size, last_ammo_visual)
    hp_bar_pos = (80, SCREEN_HEIGHT - 50)
    hp_bar_size = (400, 20)
    last_hp_visual = draw_hp_bar_remodeled(screen, player_hp, player_hp_max, hp_bar_pos, hp_bar_size, last_hp_visual)

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
        if isinstance(bullet, ExplosionEffectPersistent):
            continue 
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
                    bullet.to_remove = True
                    hit = True
                    break

        if hit:
            bullet.to_remove = True
            continue
    
    if not changing_room:
        # 방 전환 위치 체크
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

        world_instance.draw_full(
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

        obstacle_manager.draw_trees(screen, world_x, world_y, player_center_world, enemies)

    if slide_direction:
        # 방 전환 실행
        def draw_new_room():
            change_room(next_dir)
            render_game_frame()
        old_surface = screen.copy()
        swipe_curtain_transition(screen, old_surface, draw_new_room, direction=slide_direction, duration=0.5)
        continue

    if weapon:
        render_weapon = weapon
        if changing_weapon and t >= 0.5:
            render_weapon = weapons[change_weapon_target]

        if render_weapon:
            scaled_image = pygame.transform.smoothscale(
                render_weapon.topdown_image,
                (
                    int(render_weapon.topdown_image.get_width() * PLAYER_VIEW_SCALE),
                    int(render_weapon.topdown_image.get_height() * PLAYER_VIEW_SCALE)
                )
            )
            rotated_weapon = pygame.transform.rotate(scaled_image, -angle_degrees - 90)
            rotated_weapon_rect = rotated_weapon.get_rect(center=(gun_pos_x, gun_pos_y))
            screen.blit(rotated_weapon, rotated_weapon_rect.move(shake_offset_x, shake_offset_y))
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
    draw_weapon_ui(screen, weapons, current_weapon_index)
    if current_boss and type(current_boss).__name__ in ("Boss1", "Boss2") and current_boss.alive:
        last_boss_hp_visual = draw_boss_hp_bar(screen, current_boss, last_boss_hp_visual)

    cursor_rect = cursor_image.get_rect(center=(mouse_x, mouse_y))
    screen.blit(cursor_image, cursor_rect)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()