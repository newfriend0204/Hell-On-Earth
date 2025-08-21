import pygame
import math
import random
from config import *
import config
import os
from asset_manager import load_images, load_weapon_assets
from sound_manager import load_sounds
from entities import (
    ExplosionEffectPersistent,
    FieldWeapon,
    MerchantNPC,
    DoctorNFNPC,
    SoldierNPC,
    ScientistNPC,
    Portal,
    Obstacle,
    DroneNPC,
    spawn_shock_particles,
    update_shock_particles,
    draw_shock_particles,
)
from collider import Collider
from obstacle_manager import ObstacleManager
from ai import ENEMY_CLASSES
from weapon import WEAPON_CLASSES, MeleeController
from ui import draw_weapon_detail_ui, handle_tab_click, draw_status_tab, weapon_stats, draw_combat_banner, draw_enemy_counter, draw_shock_overlay
import world
from maps import MAPS, BOSS_MAPS, S1_FIGHT_MAPS, S2_FIGHT_MAPS, S3_FIGHT_MAPS
from dialogue_manager import DialogueManager
from text_data import (
    merchant_dialogue,
    doctorNF_dialogue,
    drone_dialogue,
    doctorNF12_before_dialogue,
    doctorNF12_after_dialogue,
    doctorNF13_dialogue,
    doctorNF21_dialogue,
    doctorNF22_dialogue,
    scientist1_dialogue,
    scientist2_before_dialogue,
    scientist2_after_dialogue,
    scientist3_before_dialogue,
    scientist3_after_dialogue,
    soldier1_before_dialogue,
    soldier1_after_dialogue,
    soldier2_before_dialogue,
    soldier2_after_dialogue,
    soldier3_before_dialogue,
    soldier3_after_dialogue,
    soldier4_dialogue,
    BOSS_DESC
)

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
BOLD_FONT_PATH = os.path.join(ASSET_DIR, "Font", "SUIT-Bold.ttf")
KOREAN_FONT_18 = pygame.font.Font(FONT_PATH, 18)
KOREAN_FONT_BOLD_20 = pygame.font.Font(BOLD_FONT_PATH, 20)
KOREAN_FONT_BOLD_18 = pygame.font.Font(BOLD_FONT_PATH, 18)
TITLE_FONT = pygame.font.Font(BOLD_FONT_PATH, 64)
BUTTON_FONT = pygame.font.Font(BOLD_FONT_PATH, 28)
SUB_FONT = pygame.font.Font(FONT_PATH, 18)

pygame.mouse.set_visible(False)

#screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

ICON_PATH = os.path.join(ASSET_DIR, "Image", "GameIcon.png")
_icon_surface = pygame.image.load(ICON_PATH).convert_alpha()
_icon_surface = pygame.transform.smoothscale(
    _icon_surface,
    (int(_icon_surface.get_width()), int(_icon_surface.get_height()))
)
pygame.display.set_icon(_icon_surface)

pygame.display.set_caption("Hell On Earth")

def get_player_world_position():
    return (
        world_x + player_rect.centerx,
        world_y + player_rect.centery
    )

images = load_images()
sounds = load_sounds()
config.sounds = sounds
config.images = images
config.dropped_items = []
weapon_assets = load_weapon_assets(images)
melee = MeleeController(
    images, sounds,
    get_player_world_pos_fn=get_player_world_position
)

player_dead = False
death_started_ms = 0
death_gray_duration = 3000
death_black_delay = 500
gameover_sfx_played = False
_go_hover = -1
_go_scales = [1.0, 1.0]
_go_retry_rect = None
_go_exit_rect  = None
_retry_requested = False
_exit_requested  = False

START_WEAPONS = [
    WEAPON_CLASSES[25],
    WEAPON_CLASSES[26],
    WEAPON_CLASSES[27],
    WEAPON_CLASSES[28],
]

def _apply_stage_theme_images():
    theme = config.STAGE_THEME.get(config.CURRENT_STAGE, "map1")
    if theme == "map2":
        bg = images.get("background_map2", images["background"])
        images["wall_barrier"] = images.get("wall_barrier_map2", images["wall_barrier"])
        images["wall_barrier_rotated"] = images.get("wall_barrier_map2_rotated", images["wall_barrier_rotated"])
    elif theme == "map3":
        bg = images.get("background_map3", images["background"])
        images["wall_barrier"] = images.get("wall_barrier_map3", images["wall_barrier"])
        images["wall_barrier_rotated"] = images.get("wall_barrier_map3_rotated", images["wall_barrier_rotated"])
    else:
        bg = images.get("background_map1", images["background"])
        images["wall_barrier"] = images.get("wall_barrier_map1", images["wall_barrier"])
        images["wall_barrier_rotated"] = images.get("wall_barrier_map1_rotated", images["wall_barrier_rotated"])
    return bg

original_player_image = images["player"]
original_bullet_image = images["bullet1"]
original_cartridge_image = images["cartridge_case1"]
cursor_image = images["cursor"]
background_image = _apply_stage_theme_images()
background_rect = background_image.get_rect()

combat_banner_fx = {"mode": None, "t": 0.0, "duration": 1100}
stage_banner_fx = {"text": None, "t": 0.0, "duration": 2600}
next_room_enter_sound = "room_move"

defer_combat_banner = {"pending": False, "entry_pos": (0, 0)}
combat_banner_defer_dist_px = 0
enemy_counter_fx = {"state": None, "t": 0.0, "slide_in": 300, "fade_out": 300}

TITLE_FONT  = pygame.font.Font(BOLD_FONT_PATH, 64)
BUTTON_FONT = pygame.font.Font(BOLD_FONT_PATH, 28)
SUB_FONT    = pygame.font.Font(FONT_PATH, 18)

MENU_BUTTONS = [
    {"id": "start",   "label": "시작하기"},
    {"id": "howto",   "label": "조작법"},
    {"id": "credits", "label": "크레딧"},
    {"id": "quit",    "label": "나가기"},
]
_menu_scales = [1.0 for _ in MENU_BUTTONS]
_menu_hover  = -1
_menu_modal = None
_menu_modal_hover = -1

def _draw_dim(surface, alpha=160):
    dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    dim.fill((0, 0, 0, alpha))
    surface.blit(dim, (0, 0))

def _draw_center_panel(surface, w, h):
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (18, 18, 18, 235), (0, 0, w, h), border_radius=16)
    pygame.draw.rect(panel, (200, 200, 200, 90), (0, 0, w, h), width=2, border_radius=18)
    rect = panel.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    surface.blit(panel, rect)
    return rect

def _draw_menu_confirm_quit(surface):
    # '정말 나가시겠습니까?' (붉은글씨), [예]/[아니요]
    global _menu_modal_hover
    _draw_dim(surface, 170)
    rect = _draw_center_panel(surface, 560, 260)

    prompt = BUTTON_FONT.render("정말 나가시겠습니까?", True, (220, 60, 60))
    surface.blit(prompt, ( (SCREEN_WIDTH - prompt.get_width())//2, rect.y + 42))

    mouse_pos = pygame.mouse.get_pos()
    # 먼저 기본으로 그려서 rect 얻고, hover면 다시 하이라이트로 그린다.
    yes_center = (SCREEN_WIDTH//2 - 90, rect.bottom - 60)
    no_center  = (SCREEN_WIDTH//2 + 90, rect.bottom - 60)
    yes_rect = _draw_button(surface, "예", yes_center, False, 1.0)
    no_rect  = _draw_button(surface, "아니요", no_center, False, 1.0)

    hovered = -1
    if yes_rect.collidepoint(mouse_pos): hovered = 0
    elif no_rect.collidepoint(mouse_pos): hovered = 1
    if hovered != -1:
        if hovered != _menu_modal_hover:
            sounds["button_select"].play()
        _menu_modal_hover = hovered
        # 하이라이트로 다시 그리기
        _ = _draw_button(surface, "예", yes_center, hovered==0, 1.08 if hovered==0 else 1.0)
        _ = _draw_button(surface, "아니요", no_center, hovered==1, 1.08 if hovered==1 else 1.0)
    else:
        _menu_modal_hover = -1

    return yes_rect, no_rect

def _draw_menu_panel(surface, title, lines):
    # 조작법/크레딧 팝업. 닫기 버튼 하나.
    global _menu_modal_hover
    _draw_dim(surface, 170)
    rect = _draw_center_panel(surface, 700, 600)

    # 제목
    title_surf = TITLE_FONT.render(title, True, (235, 235, 235))
    surface.blit(title_surf, ((SCREEN_WIDTH - title_surf.get_width())//2, rect.y + 24))

    # 본문
    y = rect.y + 24 + title_surf.get_height() + 12
    for line in lines:
        txt = BUTTON_FONT.render(line, True, (220, 220, 220))
        surface.blit(txt, (rect.x + 36, y))
        y += txt.get_height() + 8
        if y > rect.bottom - 90:
            break

    # 닫기 버튼
    mouse_pos = pygame.mouse.get_pos()
    close_center = (SCREEN_WIDTH//2, rect.bottom - 46)
    close_rect = _draw_button(surface, "닫기", close_center, False, 1.0)
    hovered = 0 if close_rect.collidepoint(mouse_pos) else -1
    if hovered != -1:
        if hovered != _menu_modal_hover:
            sounds["button_select"].play()
        _menu_modal_hover = hovered
        _ = _draw_button(surface, "닫기", close_center, True, 1.08)
    else:
        _menu_modal_hover = -1
    return close_rect

def _lerp(a, b, t): return a + (b - a) * t

def _draw_button(surface, text, center_xy, hovered=False, scale=1.0):
    label = BUTTON_FONT.render(text, True, (230, 230, 230))
    pad_x, pad_y = 28, 14
    w, h = label.get_width() + pad_x * 2, label.get_height() + pad_y * 2
    w = int(w * scale); h = int(h * scale)
    btn = pygame.Surface((w, h), pygame.SRCALPHA)
    bg = (18, 18, 18, 230) if not hovered else (26, 26, 26, 240)
    pygame.draw.rect(btn, bg, (0, 0, w, h), border_radius=14)
    pygame.draw.rect(btn, (200, 200, 200, 90), (0, 0, w, h), width=2, border_radius=16)
    label = pygame.transform.smoothscale(label, (int(label.get_width()*scale), int(label.get_height()*scale)))
    btn.blit(label, ((w-label.get_width())//2, (h-label.get_height())//2))
    rect = btn.get_rect(center=center_xy)
    surface.blit(btn, rect)
    return rect

LOGO_PATH = os.path.join(ASSET_DIR, "Image", "GameLogo.png")
_game_logo = pygame.image.load(LOGO_PATH).convert_alpha()
_max_w = int(SCREEN_WIDTH * 0.9)
_max_h = int(SCREEN_HEIGHT * 0.45)
if _game_logo.get_width() > _max_w:
    nw = _max_w
    nh = int(_game_logo.get_height() * (nw / _game_logo.get_width()))
    _game_logo = pygame.transform.smoothscale(_game_logo, (nw, nh))
if _game_logo.get_height() > _max_h:
    nh = _max_h
    nw = int(_game_logo.get_width() * (nh / _game_logo.get_height()))
    _game_logo = pygame.transform.smoothscale(_game_logo, (nw, nh))

def _draw_title(surface):
    # 메인 메뉴 상단에 게임 로고를 표시
    top = 56
    rect = _game_logo.get_rect()
    rect.centerx = SCREEN_WIDTH // 2
    rect.top = top

    shadow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    shadow.blit(_game_logo, (0, 0))
    shadow.fill((0, 0, 0, 80), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(shadow, (rect.x + 3, rect.y + 3))
    surface.blit(_game_logo, rect)

    return rect.bottom

HOWTO_LINES = [
    "조작법", "",
    "이동: W/A/S/D",
    "공격: 마우스 좌클릭",
    "보조 발사: 마우스 우클릭",
    "근접 공격: V",
    "무기 교체: 숫자키 (1~4)",
    "상호작용: Space",
    "무기 상세/탭 UI: Tab",
    "나머지는 게임을 들어가면 자세히 알게 됩니다.",
]

CREDITS_LINES = [
    "크레딧", "",
    "게임 이름:Hell on Earth",
    "",
    "게임 아이디어 제공/코딩:홍승표(1%)",
    "",
    "도움:GPT-4o, GPT-4.1, GPT-5 Thinking(99%)",
    "",
    "이미지 제공:GPT-4o, GPT-5 Thinking",
    "",
    "사운드 제공:음원 사이트(https://pixabay.com),직접 녹음",
]

def init_new_game():
    global grid, current_room_pos, visited_f_rooms, room_portals, current_portal, portal_spawn_at_ms
    global player_hp_max, player_hp, last_hp_visual, ammo_gauge_max, ammo_gauge, last_ammo_visual
    global bullets, scattered_bullets, enemies, field_weapons, room_field_weapons, next_room_enter_sound
    global room_shop_items, room_drone_rooms, room_acquire_type, room_entry_dir_cache
    import config, world

    # 진행상황 초기화
    config.player_score = 0
    visited_f_rooms = {}
    room_portals = {}
    current_portal = None
    portal_spawn_at_ms = None
    bullets[:] = []
    scattered_bullets[:] = []
    enemies[:] = []
    field_weapons = []
    room_field_weapons = {}
    room_shop_items = {}
    room_drone_rooms = {}
    room_acquire_type = {}
    room_entry_dir_cache = {}
    try:
        config.dropped_items = []
        config.effects = []
        config.active_dots = []
        config.blood_effects = []
    except Exception:
        pass

    # 스테이지를 1-1로 리셋하고 맵 재생성
    config.CURRENT_STAGE = "1-1"
    stage_settings = STAGE_DATA[config.CURRENT_STAGE]
    world.MIN_F_ROOMS = stage_settings["min_f_rooms"]
    world.MAX_F_ROOMS = stage_settings["max_f_rooms"]
    grid = world.generate_map()
    grid = world.place_acquire_rooms(grid, count=stage_settings["acquire_rooms"])
    world.initialize_room_states(grid)
    world.print_grid(grid)

    # 시작 방 좌표 복원
    s_pos = None
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == 'S':
                s_pos = (x, y); break
        if s_pos: break
    current_room_pos = list(s_pos)
    world.reveal_neighbors(s_pos[0], s_pos[1], grid)

    # 플레이어 수치 초기화
    player_hp_max = 200
    player_hp     = player_hp_max
    last_hp_visual = float(player_hp)
    ammo_gauge_max = 300
    ammo_gauge     = ammo_gauge_max
    last_ammo_visual = float(ammo_gauge)

    # (선택) 무기 인스턴스도 재생성해서 내부 쿨다운/상태 초기화
    try:
        global weapons, current_weapon_index, changing_weapon, change_animation_timer, recoil_in_progress
        weapons = [
            cls.create_instance(
                weapon_assets, sounds,
                lambda: ammo_gauge, consume_ammo, get_player_world_position
            )
            for cls in START_WEAPONS
        ]
        init_weapon_ui_cache(weapons)
        current_weapon_index = 0
        changing_weapon = False
        change_animation_timer = 0.0
        recoil_in_progress = False
    except Exception:
        pass

    # 현재 방을 재로딩해서 실제 오브젝트/벽/스폰 재설정
    next_room_enter_sound = None
    change_room(None)

pause_menu_active = False
pause_menu_hover  = -1
pause_scales      = [1.0, 1.0]
pause_buttons     = [{"id":"resume","label":"계속하기"},{"id":"quit","label":"나가기"}]
pause_frozen_frame = None
confirm_quit_active = False
confirm_left_released = False
pause_request = False
confirm_hover = -1
confirm_scales = [1.0, 1.0]
start_transition_pending = False
start_transition_old_surface = None

dialogue_manager = DialogueManager()
last_merchant_ms = 0
mouse_left_released_after_dialogue = False
mouse_left_released_after_pause = False
mouse_left_released_after_transition = False
merchant_pos = None
npcs = []
dialogue_capture_request = False
dialogue_frozen_frame = None
_pending_dialogue = None
_pending_dialogue_effect_cb = None
_pending_dialogue_close_cb = None

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

clock = pygame.time.Clock()
running = True

player_radius = int(30 * PLAYER_VIEW_SCALE)

player_hp_max = 200000 # 디버그 원래는 200
player_hp = player_hp_max
last_hp_visual = player_hp * 1.0

def consume_ammo(cost):
    global ammo_gauge
    ammo_gauge -= cost

current_weapon_index = 0
ammo_gauge_max = 40000 # 디버그 원래는 300
ammo_gauge = ammo_gauge_max 
last_ammo_visual = ammo_gauge * 1.0

current_boss = None
last_boss_hp_visual = 0

damage_flash_alpha = 0
damage_flash_fade_speed = 5

blood_effects = config.blood_effects
config.effects = []
config.active_dots = []

kill_count = 0

boss_intro_active = False
boss_intro_shown_this_entry = False
boss_intro_start_ms = 0
boss_intro_approach_ms = 450
boss_intro_pause_ms = 3600
boss_intro_exit_ms = 450
BOSS_PULSE_MS = 400
boss_intro_duration = boss_intro_approach_ms + boss_intro_pause_ms + boss_intro_exit_ms
_boss_left_surf = None
_boss_right_block = None
_boss_right_block_rect = None

changing_room = False
visited_f_rooms = {}
room_portals = {}
current_portal = None
portal_spawn_at_ms = None
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

class ShopItem:
    def __init__(self, weapon_class, price, x, y):
        self.weapon_class = weapon_class
        self.price = price
        self.x = x
        self.y = y
        self.purchased = False

room_shop_items = {}
shop_items = []
room_drone_rooms = {}
room_acquire_type = {}
room_entry_dir_cache = {}

def _guess_entry_dir_for_room(cx_cell, cy_cell):
    # 현재 E방의 입실 방향(북/남/서/동)을 캐시를 활용해 추정.
    room_key = (cx_cell, cy_cell)
    entry_dir = room_entry_dir_cache.get(room_key)
    if entry_dir is None:
        for nx, ny in world.neighbors(cx_cell, cy_cell):
            if 0 <= nx < world.WIDTH and 0 <= ny < world.HEIGHT and grid[ny][nx] in ('F', 'S'):
                if ny < cy_cell:   entry_dir = "north"
                elif ny > cy_cell: entry_dir = "south"
                elif nx < cx_cell: entry_dir = "west"
                else:              entry_dir = "east"
                break
        room_entry_dir_cache[room_key] = entry_dir
    return entry_dir

def _get_offscreen_spawn_xy(entry_dir):
    # 입실 방향 기준으로 방 바깥쪽에서 슬라이드 인 하도록 스폰 좌표 계산.
    eff_w   = world_instance.effective_bg_width
    eff_h   = world_instance.effective_bg_height
    center_x = eff_w  / 2
    center_y = eff_h  / 2

    X_OFF_NS = int(158 * 0.75) * PLAYER_VIEW_SCALE
    Y_OFF_WE = int(144 * 0.75) * PLAYER_VIEW_SCALE
    OUT_TOP  = int(216 * 0.80) * PLAYER_VIEW_SCALE
    OUT_BOT  = int( 89 * 0.80) * PLAYER_VIEW_SCALE
    OUT_LEFT = int(170 * 0.80) * PLAYER_VIEW_SCALE
    OUT_RGHT = int(130 * 0.80) * PLAYER_VIEW_SCALE

    if entry_dir == "north":
        return center_x - X_OFF_NS, -OUT_TOP
    elif entry_dir == "south":
        return center_x - X_OFF_NS, eff_h + OUT_BOT
    elif entry_dir == "west":
        return -OUT_LEFT,          center_y - Y_OFF_WE
    elif entry_dir == "east":
        return eff_w + OUT_RGHT,   center_y - Y_OFF_WE
    else:
        return center_x, center_y

def _spawn_endroom_story_npc(cfg):
    # E방에 스토리 NPC 1명을 스폰하는 축약 함수.
    cx_cell, cy_cell = current_room_pos
    entry_dir = _guess_entry_dir_for_room(cx_cell, cy_cell)
    x, y = _get_offscreen_spawn_xy(entry_dir)
    rs = world.room_states[cy_cell][cx_cell]
    dlg = cfg["after"] if rs == 9 else cfg["before"]
    npcs.append(cfg["cls"](images[cfg["image"]], x, y, dlg))

# 스테이지별 E방 스토리 NPC 매핑
ENDROOM_NPC_CONFIG = {
    "1-1": {"cls": SoldierNPC,  "image": "soldier1",   "before": soldier1_before_dialogue,   "after": soldier1_after_dialogue},
    "1-2": {"cls": DoctorNFNPC, "image": "doctorNF",   "before": doctorNF12_before_dialogue, "after": doctorNF12_after_dialogue},
    "1-3": {"cls": SoldierNPC,  "image": "soldier2",   "before": soldier2_before_dialogue,   "after": soldier2_after_dialogue},

    "2-1": {"cls": ScientistNPC,"image": "scientist2", "before": scientist2_before_dialogue,  "after": scientist2_after_dialogue},
    "2-2": {"cls": SoldierNPC,  "image": "soldier3",   "before": soldier3_before_dialogue,    "after": soldier3_after_dialogue},
    "2-3": {"cls": ScientistNPC,"image": "scientist3", "before": scientist3_before_dialogue,  "after": scientist3_after_dialogue},
}

def spawn_room_npcs():
    # NPC 소환 시작
    npcs.clear()

    cx_cell, cy_cell = current_room_pos
    room_key = (cx_cell, cy_cell)
    room_type = grid[cy_cell][cx_cell]

    if room_type == 'A' and room_drone_rooms.get(room_key, False):
        center_x = world_instance.effective_bg_width / 2
        center_y = world_instance.effective_bg_height / 2
        npcs.append(
            DroneNPC(
                images["drone"],
                center_x,
                center_y - int(100 * PLAYER_VIEW_SCALE),
                drone_dialogue,
            )
        )
    elif room_type == 'A' and shop_items:
        center_x = world_instance.effective_bg_width / 2
        center_y = world_instance.effective_bg_height / 2 - 190
        npcs.append(
            MerchantNPC(
                images["merchant1"],
                center_x,
                center_y,
                merchant_dialogue,
            )
        )

    if "npc_infos" in CURRENT_MAP:
        for npc_info in CURRENT_MAP["npc_infos"]:
            if npc_info["npc_type"] == "doctorNF_npc" and config.CURRENT_STAGE == "1-1":
                npcs.append(
                    DoctorNFNPC(
                        images["doctorNF"],
                        npc_info["x"],
                        npc_info["y"],
                        doctorNF_dialogue,
                    )
                )
            elif npc_info["npc_type"] == "scientist1_npc" and config.CURRENT_STAGE == "1-2":
                npcs.append(
                    ScientistNPC(
                        images["scientist1"],
                        npc_info["x"],
                        npc_info["y"],
                        scientist1_dialogue,
                    )
                )
            elif npc_info["npc_type"] == "soldier2_npc" and config.CURRENT_STAGE == "2-3":
                npcs.append(
                    SoldierNPC(
                        images["soldier2"],
                        npc_info["x"],
                        npc_info["y"],
                        soldier4_dialogue,
                    )
                )
            elif npc_info["npc_type"] == "doctorNF_npc" and config.CURRENT_STAGE == "1-3":
                npcs.append(
                    DoctorNFNPC(
                        images["doctorNF"],
                        npc_info["x"],
                        npc_info["y"],
                        doctorNF13_dialogue,
                    )
                )
            elif npc_info["npc_type"] == "doctorNF_npc" and config.CURRENT_STAGE == "2-1":
                npcs.append(
                    DoctorNFNPC(
                        images["doctorNF"],
                        npc_info["x"],
                        npc_info["y"],
                        doctorNF21_dialogue,
                    )
                )
            elif npc_info["npc_type"] == "doctorNF_npc" and config.CURRENT_STAGE == "2-2":
                npcs.append(
                    DoctorNFNPC(
                        images["doctorNF"],
                        npc_info["x"],
                        npc_info["y"],
                        doctorNF22_dialogue,
                    )
                )

    if room_type == 'E':
        cfg = ENDROOM_NPC_CONFIG.get(config.CURRENT_STAGE)
        if cfg is not None:
            _spawn_endroom_story_npc(cfg)

def on_dialogue_close():
    global mouse_left_released_after_dialogue, dialogue_frozen_frame
    dialogue_frozen_frame = None
    render_game_frame()
    pygame.display.flip()
    for b in bullets:
        if isinstance(b, ExplosionEffectPersistent):
            b.resume()
    dialogue_frozen_frame = None
    screen.set_clip(None)
    render_game_frame()
    pygame.display.flip()

space_pressed_last_frame = False

def preview_effect_text(effect, messages=None):
    # 확인 단계에서 보여줄 안내 문구를 데이터 템플릿으로 생성.
    import math
    messages = messages or {}
    et  = effect.get("type")
    amt = int(effect.get("amount", 0))

    def fmt(key, **kw):
        tpl = messages.get(key)
        if not tpl:
            return ""
        try:
            return tpl.format(**kw)
        except Exception:
            return tpl

    if et == "hp_recover":
        before = player_hp
        after  = min(player_hp + amt, player_hp_max)
        gained = max(0, after - before)
        if gained <= 0:
            return fmt("full")
        cost = max(1, math.ceil(gained * config.ESSENCE_COST_PER_HP))
        cost = int(math.ceil(cost * config.get_stage_price_mult()))
        return fmt("prompt", cost=cost, gained=gained)

    if et == "ammo_recover":
        before = ammo_gauge
        after  = min(ammo_gauge + amt, ammo_gauge_max)
        gained = max(0, after - before)
        if gained <= 0:
            return fmt("full")
        cost = max(1, math.ceil(gained * config.ESSENCE_COST_PER_AMMO))
        cost = int(math.ceil(cost * config.get_stage_price_mult()))
        return fmt("prompt", cost=cost, gained=gained)
    
    if et == "hp_max_up":
        cnt = getattr(config, "drone_hp_up_count", 0)
        base = getattr(config, "DRONE_HP_UP_BASE_COST", 800)
        growth = getattr(config, "DRONE_COST_GROWTH", 1.35)
        cost = max(1, int(round(base * (growth ** cnt))))
        cost = int(math.ceil(cost * config.get_stage_price_mult()))
        return fmt("prompt", cost=cost, gained=amt)

    if et == "ammo_max_up":
        cnt = getattr(config, "drone_ammo_up_count", 0)
        base = getattr(config, "DRONE_AMMO_UP_BASE_COST", 700)
        growth = getattr(config, "DRONE_COST_GROWTH", 1.35)
        cost = max(1, int(round(base * (growth ** cnt))))
        cost = int(math.ceil(cost * config.get_stage_price_mult()))
        return fmt("prompt", cost=cost, gained=amt)

    return ""

def apply_effect(effect, messages=None, as_text_only=False):
    # 대화 이펙트 적용.
    import math
    global player_hp, player_hp_max, ammo_gauge, ammo_gauge_max, last_merchant_ms

    now = pygame.time.get_ticks()
    cooldown = getattr(config, "MERCHANT_COOLDOWN_MS", 0)
    if cooldown and (now - last_merchant_ms < cooldown):
        return "" if as_text_only else None
    last_merchant_ms = now

    messages = messages or {}
    et  = effect.get("type")
    amt = int(effect.get("amount", 0))

    def format_msg(key, **fmt):
        txt = messages.get(key)
        if not txt:
            return ""
        try:
            return txt.format(**fmt)
        except Exception:
            return txt

    def emit(key, **fmt):
        line = format_msg(key, **fmt)
        if as_text_only:
            return line
        if line:
            try:
                curr_node = dialogue_manager.dialogue_data[dialogue_manager.idx]
                speaker = curr_node.get("speaker", "")
            except Exception:
                speaker = ""
            dialogue_manager.enqueue_history_line(speaker, line)
        return None

    if et == "hp_recover":
        before = player_hp
        after  = min(player_hp + amt, player_hp_max)
        gained = max(0, after - before)
        if gained <= 0:
            return emit("full", gained=gained)
        cost = max(1, math.ceil(gained * config.ESSENCE_COST_PER_HP))
        cost = int(math.ceil(cost * config.get_stage_price_mult()))
        if config.player_score >= cost:
            config.player_score -= cost
            player_hp = after
            return emit("success", gained=gained, cost=cost)
        else:
            need = cost - config.player_score
            return emit("insufficient", need=need)
    elif et == "ammo_recover":
        before = ammo_gauge
        after  = min(ammo_gauge + amt, ammo_gauge_max)
        gained = max(0, after - before)
        if gained <= 0:
            return emit("full", gained=gained)
        cost = max(1, math.ceil(gained * config.ESSENCE_COST_PER_AMMO))
        cost = int(math.ceil(cost * config.get_stage_price_mult()))
        if config.player_score >= cost:
            config.player_score -= cost
            ammo_gauge = after
            return emit("success", gained=gained, cost=cost)
        else:
            need = cost - config.player_score
            return emit("insufficient", need=need)
    elif et == "hp_max_up":
        cnt = getattr(config, "drone_hp_up_count", 0)
        base = getattr(config, "DRONE_HP_UP_BASE_COST", 800)
        growth = getattr(config, "DRONE_COST_GROWTH", 1.35)
        cost = max(1, int(round(base * (growth ** cnt))))
        cost = int(math.ceil(cost * config.get_stage_price_mult()))
        if config.player_score >= cost:
            config.player_score -= cost
            prev_max = player_hp_max
            ratio = (player_hp / prev_max) if prev_max > 0 else 0.0

            player_hp_max += amt
            player_hp = min(player_hp_max, int(round(player_hp_max * ratio)))

            config.drone_hp_up_count = cnt + 1
            return emit("success", gained=amt, cost=cost)
        else:
            need = cost - config.player_score
            return emit("insufficient", need=need)
    elif et == "ammo_max_up":
        cnt = getattr(config, "drone_ammo_up_count", 0)
        base = getattr(config, "DRONE_AMMO_UP_BASE_COST", 700)
        growth = getattr(config, "DRONE_COST_GROWTH", 1.35)
        cost = max(1, int(round(base * (growth ** cnt))))
        cost = int(math.ceil(cost * config.get_stage_price_mult()))
        if config.player_score >= cost:
            config.player_score -= cost
            prev_max = ammo_gauge_max
            ratio = (ammo_gauge / prev_max) if prev_max > 0 else 0.0

            ammo_gauge_max += amt
            ammo_gauge = min(ammo_gauge_max, int(round(ammo_gauge_max * ratio)))

            config.drone_ammo_up_count = cnt + 1
            return emit("success", gained=amt, cost=cost)
        else:
            need = cost - config.player_score
            return emit("insufficient", need=need)
    return "" if as_text_only else None

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

            room_key = tuple(current_room_pos)
            if room_key in room_field_weapons and fw in room_field_weapons[room_key]:
                room_field_weapons[room_key].remove(fw)

            field_weapons.remove(fw)
            break

def damage_player(amount):
    # 디버그, 무적
    # return
    # 플레이어 피해 처리
    global player_hp, damage_flash_alpha, shake_timer, shake_elapsed, shake_magnitude
    global player_dead, death_started_ms
    player_hp = max(0, player_hp - amount)
    damage_flash_alpha = 255
    shake_timer = shake_timer_max
    shake_elapsed = 0.0
    shake_magnitude = 3
    if player_hp <= 0 and not player_dead:
        trigger_player_death()
config.damage_player = damage_player

def _apply_gray_blend_inplace(surface, t, preserve_red=False, red_thresh=200, dominance=2):
    # t: 0.0 ~ 1.0
    if t <= 0: 
        return
    import numpy as np
    arr = pygame.surfarray.array3d(surface).astype(np.float32)
    gray = (arr[:, :, 0]*0.299 + arr[:, :, 1]*0.587 + arr[:, :, 2]*0.114)[:, :, None]
    blended = arr * (1.0 - t) + gray * t
    if preserve_red:
        r = arr[:, :, 0]; g = arr[:, :, 1]; b = arr[:, :, 2]
        mask = (r > red_thresh) & (r > dominance * g) & (r > dominance * b)
        blended[mask] = arr[mask]
    pygame.surfarray.blit_array(surface, blended.astype('uint8'))

def trigger_player_death():
    # 플레이어를 즉시 숨기고, 피 이펙트 대량 생성
    from entities import ScatteredBlood
    global player_dead, death_started_ms, sounds, gameover_sfx_played
    global move_left, move_right, move_up, move_down
    global mouse_left_button_down, mouse_right_button_down
    move_left = move_right = move_up = move_down = False
    mouse_left_button_down = False
    mouse_right_button_down = False
    wx, wy = get_player_world_position()
    blood = ScatteredBlood(wx, wy, num_particles=500)
    for p in getattr(blood, "particles", []):
        p["vx"] *= 1.5
        p["vy"] *= 1.5
    config.blood_effects.append(blood)
    gameover_sfx_played = False
    from sound_manager import cut_bgm
    cut_bgm()
    player_dead = True
    death_started_ms = pygame.time.get_ticks()
    move_left = move_right = move_up = move_down = False
    mouse_left_button_down = False
    mouse_right_button_down = False

def init_weapon_ui_cache(weapons):
    # 무기 UI 슬롯 이미지 캐싱
    slot_width = 92
    slot_height = 54
    slot_alpha = 180

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
    global room_portals, current_portal, portal_spawn_at_ms
    global room_field_weapons, room_shop_items, room_drone_rooms
    global room_acquire_type, room_entry_dir_cache
    global field_weapons, shop_items
    room_portals.clear()
    current_portal = None; portal_spawn_at_ms = None

    visited_f_rooms.clear()

    try:
        room_field_weapons.clear()
        room_shop_items.clear()
        room_drone_rooms.clear()
        room_acquire_type.clear()
        room_entry_dir_cache.clear()
    except NameError:
        pass
    try:
        field_weapons.clear()
        shop_items.clear()
    except NameError:
        pass

    import config
    stage_order = list(STAGE_DATA.keys())
    idx = stage_order.index(config.CURRENT_STAGE)

    if idx >= len(stage_order) - 1:
        print("[DEBUG] 마지막 스테이지입니다. 더 이상 진행할 수 없습니다.")
        return

    next_stage = stage_order[idx + 1]
    config.CURRENT_STAGE = next_stage
    from sound_manager import play_bgm_for_stage
    play_bgm_for_stage(next_stage)
    try:
        trigger_stage_banner(f"스테이지 {next_stage}")
    except Exception:
        pass
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
                global next_room_enter_sound
                next_room_enter_sound = "portal_enter"
                change_room(None)
                return

def _collect_all_dropped_items_instant():
    # 방 이동 직전 즉시 정산: 필드의 체력/탄약 오브를 모두 획득 처리
    global player_hp, ammo_gauge, player_hp_max, ammo_gauge_max
    import config
    gained_hp = 0
    gained_ammo = 0
    for item in list(getattr(config, "dropped_items", [])):
        if getattr(item, "item_type", None) == "health":
            gained_hp += getattr(item, "value", 0)
        elif getattr(item, "item_type", None) == "ammo":
            gained_ammo += getattr(item, "value", 0)
    if gained_hp or gained_ammo:
        player_hp = min(player_hp_max, player_hp + gained_hp)
        ammo_gauge = min(ammo_gauge_max, ammo_gauge + gained_ammo)
    # 모두 제거
    config.dropped_items.clear()

def change_room(direction):
    # 방 전환 처리
    global current_room_pos, CURRENT_MAP, world_instance, world_x, world_y, enemies, changing_room, effective_bg_width, effective_bg_height, current_boss, field_weapons, shop_items, current_portal, background_image, next_room_enter_sound, boss_intro_shown_this_entry, shop_items, room_acquire_type
    
    current_portal = None
    _collect_all_dropped_items_instant()
    try:
        room_field_weapons[tuple(current_room_pos)] = list(field_weapons)
    except Exception:
        pass
    WIDTH, HEIGHT = world.get_map_dimensions()
    changing_room = True
    background_image = _apply_stage_theme_images()

    if direction is None:
        new_x, new_y = current_room_pos
        dx, dy = 0, 0
        spawn_direction = None
    else:
        dx, dy = DIRECTION_OFFSET[direction]
        new_x = current_room_pos[0] + dx
        new_y = current_room_pos[1] + dy
        spawn_direction = SPAWN_FROM_OPPOSITE[direction]
        room_entry_dir_cache[(new_x, new_y)] = spawn_direction

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
        theme = config.STAGE_THEME.get(config.CURRENT_STAGE, "map1")
        if theme == "map2":
            fight_pool = S2_FIGHT_MAPS
        elif theme == "map3":
            fight_pool = S3_FIGHT_MAPS
        else:
            fight_pool = S1_FIGHT_MAPS

        if room_key not in visited_f_rooms:
            fight_map_index = random.randint(0, len(fight_pool) - 1)
            visited_f_rooms[room_key] = {
                "fight_map_index": fight_map_index,
                "cleared": False,
                "enemy_types": []
            }
        fight_map_index = visited_f_rooms[room_key].get("fight_map_index", random.randint(0, len(fight_pool) - 1))
        CURRENT_MAP = fight_pool[fight_map_index]

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
        base_boss_map = BOSS_MAPS[stage_boss_index]
        if config.STAGE_THEME.get(config.CURRENT_STAGE, "map1") == "map2":
            for info in CURRENT_MAP.get("enemy_infos", []):
                info["enemy_type"] = "Enemy2"

        # 보스방이 이미 클리어(9)면 적 제거/전투 비활성화 + 포탈 표시
        if world.room_states[new_y][new_x] == 9:
            CURRENT_MAP = {
                "obstacles": base_boss_map["obstacles"],
                "enemy_infos": [],
                "crop_rect": base_boss_map["crop_rect"]
            }
            config.combat_state = False
            config.combat_enabled = False
        else:
            CURRENT_MAP = base_boss_map
            config.combat_state = False
            # ▶ 전투 “돌입” 순간에 연출을 띄울 것이므로 여기서는 전투를 허용해 둔다.
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

    room_key = (new_x, new_y)
    shop_items = []
    if new_room_type != 'A':
        field_weapons.clear()
        field_weapons.extend(room_field_weapons.get(room_key, []))

    if new_room_type == 'A':
        if room_key not in room_acquire_type:
            room_acquire_type[room_key] = random.randint(4, 4)  # 2: 무기방, 3: 상점방, 4: 드론방
        acquire_index = room_acquire_type[room_key]
        CURRENT_MAP = MAPS[acquire_index]
        config.combat_state = False
        config.combat_enabled = False

        world.reveal_neighbors(new_x, new_y, grid)

        room_key = (new_x, new_y)

        if acquire_index == 2:
            if room_key not in room_field_weapons:
                center_x = new_world.effective_bg_width / 2
                center_y = new_world.effective_bg_height / 2
                spacing = 150 * PLAYER_VIEW_SCALE

                stage_weights = config.STAGE_DATA[config.CURRENT_STAGE]["weapon_tier_weights"]
                tier_to_weapons = {}
                for weapon_class in WEAPON_CLASSES:
                    tier = getattr(weapon_class, "TIER", 1)
                    if tier in stage_weights:
                        tier_to_weapons.setdefault(tier, []).append(weapon_class)
                selected_weapons = []
                attempt_count = 0
                while len(selected_weapons) < 2 and attempt_count < 10:
                    tiers = list(stage_weights.keys())
                    weights = list(stage_weights.values())
                    chosen_tier = random.choices(tiers, weights=weights, k=1)[0]
                    candidates = [w for w in tier_to_weapons[chosen_tier] if w not in selected_weapons]
                    if candidates:
                        weapon_class = random.choice(candidates)
                        selected_weapons.append(weapon_class)
                    attempt_count += 1
                weapons_in_room = []
                for i, weapon_class in enumerate(selected_weapons):
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
            shop_items = []
        elif acquire_index == 3:
            if room_key not in room_shop_items:
                center_x = new_world.effective_bg_width / 2
                center_y = new_world.effective_bg_height / 2
                spacing = 170 * PLAYER_VIEW_SCALE

                stage_weights = config.STAGE_DATA[config.CURRENT_STAGE]["weapon_tier_weights"]
                tier_to_weapons = {}
                for weapon_class in WEAPON_CLASSES:
                    tier = getattr(weapon_class, "TIER", 1)
                    if tier in stage_weights:
                        tier_to_weapons.setdefault(tier, []).append(weapon_class)
                selected_weapons = []
                attempt_count = 0
                while len(selected_weapons) < 3 and attempt_count < 12:
                    tiers = list(stage_weights.keys())
                    weights = list(stage_weights.values())
                    chosen_tier = random.choices(tiers, weights=weights, k=1)[0]
                    candidates = [w for w in tier_to_weapons[chosen_tier] if w not in selected_weapons]
                    if candidates:
                        weapon_class = random.choice(candidates)
                        selected_weapons.append(weapon_class)
                    attempt_count += 1
                items_in_room = []
                for i, weapon_class in enumerate(selected_weapons):
                    price = config.TIER_PRICES.get(getattr(weapon_class, "TIER", 1), 40)
                    price = int(round(price * config.get_stage_price_mult()))
                    shop_item = ShopItem(
                        weapon_class,
                        price,
                        center_x + (i - 1) * spacing,
                        center_y
                    )
                    items_in_room.append(shop_item)
                room_shop_items[room_key] = items_in_room

            shop_items = room_shop_items[room_key]
            field_weapons.clear()
        elif acquire_index == 4:
            room_drone_rooms[room_key] = True
            shop_items = []

            center_x = new_world.effective_bg_width / 2
            center_y = new_world.effective_bg_height / 2
            drone_offset = int(100 * PLAYER_VIEW_SCALE)
            weapon_offset = int(130 * PLAYER_VIEW_SCALE)

            r = int(28 * PLAYER_VIEW_SCALE)
            collider_surface = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            colliders = [Collider("circle", (r, r), r, False)]
            obstacle_manager.static_obstacles.append(
                Obstacle(
                    collider_surface,
                    center_x - r,
                    center_y - drone_offset - r,
                    colliders,
                    image_filename="drone_collider"
                )
            )

            if room_key not in room_field_weapons:
                stage_weights = config.STAGE_DATA[config.CURRENT_STAGE]["weapon_tier_weights"]
                tier_to_weapons = {}
                for weapon_class in WEAPON_CLASSES:
                    tier = getattr(weapon_class, "TIER", 1)
                    if tier in stage_weights:
                        tier_to_weapons.setdefault(tier, []).append(weapon_class)
                tiers = list(stage_weights.keys())
                weights = list(stage_weights.values())
                chosen_tier = random.choices(tiers, weights=weights, k=1)[0]
                weapon_class = random.choice(tier_to_weapons[chosen_tier])
                fw = FieldWeapon(weapon_class, center_x, center_y + weapon_offset, weapon_assets, sounds)
                room_field_weapons[room_key] = [fw]

            field_weapons.clear()
            field_weapons.extend(room_field_weapons.get(room_key, []))
        else:
            field_weapons.clear()
            shop_items = []

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

    if new_room_type == 'E' and world.room_states[new_y][new_x] == 9:
        room_key = (new_x, new_y)
        if room_portals.get(room_key, False):
            center_x = world_instance.effective_bg_width / 2
            center_y = world_instance.effective_bg_height / 2
            try:
                img = images["portal"]
                current_portal = Portal(center_x, center_y, img)
            except KeyError:
                current_portal = None

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
    config.blood_effects.clear()
    config.dropped_items.clear()
    config.global_enemy_bullets.clear()
    config.effects.clear()
    if hasattr(config, "active_mines"):
        config.active_mines.clear()
    for enemy in enemies:
        if hasattr(enemy, "scattered_bullets"):
            enemy.scattered_bullets.clear()
        if hasattr(enemy, "stop_sounds_on_remove"):
            enemy.stop_sounds_on_remove()

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
                    if enemy_type.lower().startswith("boss"):
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

    if not any(str(e_info.get("enemy_type", "")).lower().startswith("boss") for e_info in CURRENT_MAP.get("enemy_infos", [])):
        current_boss = None

    config.all_enemies = enemies

    if len(CURRENT_MAP["enemy_infos"]) == 0:
        config.combat_state = False
        config.combat_enabled = False
    else:
        config.combat_state = False
        config.combat_enabled = True

    spawn_room_npcs()

    if next_room_enter_sound is not None:
        key = next_room_enter_sound if next_room_enter_sound in sounds else "room_move"
        sounds[key].play()
    next_room_enter_sound = "room_move"
    boss_intro_shown_this_entry = False
    print(f"[DEBUG] Entered room at ({new_x}, {new_y}), room_state: {world.room_states[new_y][new_x]}")

    pygame.time.set_timer(pygame.USEREVENT + 1, 200)

def increment_kill_count():
    # 처치 수 증가
    global kill_count
    kill_count += 1

def _ease_in_out_cubic(u: float) -> float:
    # 보스 연출: 이징/보간 함수
    if u < 0: u = 0
    if u > 1: u = 1
    return 3*(u**2) - 2*(u**3)

def _progress_with_pause_timebased(elapsed_ms: int, approach_ms: int, pause_ms: int, exit_ms: int, p=0.45, q=0.55) -> float:
    # 시간 기반 중앙 정지 연출: 접근(빠름) → 중앙(길게) → 이탈(빠름)
    t = max(0, elapsed_ms)
    if t <= approach_ms:
        u = t / float(approach_ms) if approach_ms > 0 else 1.0
        return _ease_in_out_cubic(u) * p
    t -= approach_ms
    if t <= pause_ms:
        u = t / float(pause_ms) if pause_ms > 0 else 1.0
        return p + u * (q - p)
    t -= pause_ms
    u = t / float(exit_ms) if exit_ms > 0 else 1.0
    return q + _ease_in_out_cubic(u) * (1.0 - q)

def _lerp(a, b, t):
    return a + (b - a) * t

def _render_multiline(font, text, color):
    lines = text.split("\n")
    surfs = [font.render(line, True, color) for line in lines]
    width = max(s.get_width() for s in surfs) if surfs else 0
    height = sum(s.get_height() for s in surfs)
    block = pygame.Surface((width, height), pygame.SRCALPHA)
    y = 0
    for s in surfs:
        block.blit(s, (0, y)); y += s.get_height()
    return block

def _start_boss_intro():
    # 커튼 전환이 끝난 다음 프레임에 호출되어, 3초간 텍스트 슬라이드 연출을 시작.
    global boss_intro_active, boss_intro_start_ms, boss_intro_pending
    global _boss_left_surf, _boss_right_block, _boss_right_block_rect
    boss_intro_pending = False
    boss_intro_active = True
    boss_intro_start_ms = pygame.time.get_ticks()
    left_title = "보스 등장!"
    _boss_left_surf = TITLE_FONT.render(left_title, True, (245, 245, 245))
    header = _render_multiline(KOREAN_FONT_BOLD_20, f"{config.CURRENT_STAGE}", (240, 240, 240))
    tip_text = BOSS_DESC.get(config.CURRENT_STAGE, "데이터 없음.\n패턴을 관찰하세요.")
    tip_block = _render_multiline(KOREAN_FONT_18, tip_text, (220, 220, 220))
    w = max(header.get_width(), tip_block.get_width())
    h = header.get_height() + 8 + tip_block.get_height()
    _boss_right_block = pygame.Surface((w, h), pygame.SRCALPHA)
    _boss_right_block.blit(header, (0, 0))
    _boss_right_block.blit(tip_block, (0, header.get_height() + 8))
    _boss_right_block_rect = _boss_right_block.get_rect()

def _draw_boss_intro(screen):
    # 3초 동안 양쪽에서 텍스트가 지나가는 연출을 그림. 게임 업데이트는 멈춘 상태.
    now = pygame.time.get_ticks()
    t = now - boss_intro_start_ms
    u = min(1.0, t / boss_intro_duration)
    k = _progress_with_pause_timebased(
        t, boss_intro_approach_ms, boss_intro_pause_ms, boss_intro_exit_ms,
        p=0.495, q=0.505
    )

    L = _boss_left_surf.get_width()
    left_x0 = -L - 50
    left_x1 = SCREEN_WIDTH + 50
    left_y = int(SCREEN_HEIGHT * 0.25)
    left_x = int(_lerp(left_x0, left_x1, k))

    pulse_scale = 1.0
    if boss_intro_approach_ms <= t < boss_intro_approach_ms + BOSS_PULSE_MS:
        w = (t - boss_intro_approach_ms) / float(BOSS_PULSE_MS)
        pulse_scale = 1.0 + 0.06 * math.sin(math.pi * w)

    left_surf_to_draw = _boss_left_surf
    if abs(pulse_scale - 1.0) > 1e-3:
        lw, lh = _boss_left_surf.get_size()
        sw, sh = max(1, int(lw * pulse_scale)), max(1, int(lh * pulse_scale))
        left_surf_to_draw = pygame.transform.smoothscale(_boss_left_surf, (sw, sh))
        screen.blit(left_surf_to_draw, (left_x, left_y - (sh - lh) // 2))
    else:
        screen.blit(left_surf_to_draw, (left_x, left_y))

    in_pause = (boss_intro_approach_ms <= t < boss_intro_approach_ms + boss_intro_pause_ms)
    if in_pause:
        tw, th = left_surf_to_draw.get_size()
        text_rect = pygame.Rect(left_x, left_y, tw, th)
        cx, cy = text_rect.centerx, text_rect.centery
        blink = (math.sin(now * 0.012) + 1.0) * 0.5
        a = int(70 + 40 * blink)
        mw, mh = 18, 14
        left_tri = pygame.Surface((mw, mh), pygame.SRCALPHA)
        pygame.draw.polygon(left_tri, (240, 240, 240, a), [(mw, mh // 2), (0, 0), (0, mh)])
        right_tri = pygame.Surface((mw, mh), pygame.SRCALPHA)
        pygame.draw.polygon(right_tri, (240, 240, 240, a), [(0, mh // 2), (mw, 0), (mw, mh)])
        screen.blit(left_tri,  (text_rect.left  - mw - 10, cy - mh // 2))
        screen.blit(right_tri, (text_rect.right + 10,      cy - mh // 2))

    R = _boss_right_block.get_width()
    right_x0 = SCREEN_WIDTH + 50
    right_x1 = -R - 50
    right_y = int(SCREEN_HEIGHT * 0.58 - _boss_right_block.get_height() // 2)
    right_x = int(_lerp(right_x0, right_x1, k))
    screen.blit(_boss_right_block, (right_x, right_y))

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
        pygame.event.pump()
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
        pygame.event.pump()
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
        pygame.event.pump()
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
    bg_pos = (start_x - background_margin, start_y - background_margin)
    screen.blit(background_surface, bg_pos)

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

    return pygame.Rect(
        bg_pos[0],
        bg_pos[1],
        total_width + background_margin * 2,
        total_height + background_margin * 2
    )

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

    bg_surface = pygame.Surface((bar_width + 6, bar_height + 4), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, (255, 255, 255, 160), (0, 0, bar_width + 6, bar_height + 4), border_radius=border_radius + 2)
    screen.blit(bg_surface, (x - 3, y - 2))

    smoothing_speed = 0.5
    interpolated_hp = last_boss_hp_visual + (boss.hp - last_boss_hp_visual) * smoothing_speed

    ratio = max(0.0, interpolated_hp / boss.max_hp)

    if ratio >= 0.75:
        color = (0, 200, 0)
    elif ratio >= 0.50:
        color = (200, 200, 0)
    elif ratio >= 0.25:
        color = (255, 165, 0)
    else:
        color = (200, 0, 0)

    filled_width = int(bar_width * ratio)
    pygame.draw.rect(screen, color, (x, y, filled_width, bar_height), border_radius=border_radius)

    text_surface = KOREAN_FONT_18.render(f"보스 HP: {int(boss.hp)}/{boss.max_hp}", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y + bar_height // 2))
    screen.blit(text_surface, text_rect)

    return interpolated_hp

def draw_hp_bar_remodeled(surface, current_hp, max_hp, pos, size, last_hp_drawn):
    x, y = pos
    width, height = size
    border_radius = height // 3

    smoothing_speed = 0.5
    interpolated_hp = last_hp_drawn + (current_hp - last_hp_drawn) * smoothing_speed
    ratio = max(0.0, interpolated_hp / max_hp)
    if ratio > 0.5:
        color = (0, 180, 0)
    elif ratio > 0.25:
        color = (200, 200, 0)
    else:
        color = (180, 0, 0)

    value_text = f"{int(current_hp)}/{int(max_hp)}"
    text_w, text_h = KOREAN_FONT_BOLD_18.size(value_text)

    icon = config.images.get("health_up")
    if icon:
        icon_w, icon_h = icon.get_width(), icon.get_height()
        scale_icon_w = int(icon_w * 1.3)
        scale_icon_h = int(icon_h * 1.3)
        icon_scaled = pygame.transform.smoothscale(icon, (scale_icon_w, scale_icon_h))
    else:
        scale_icon_w = scale_icon_h = 0
        icon_scaled = None

    pad_left = 3
    pad_right = 8
    gap_text = 10
    gap_icon = 6
    extra_w = gap_text + text_w + ((gap_icon + scale_icon_w) if icon_scaled else 0) + pad_right

    bg_surface = pygame.Surface((width + 6 + extra_w, height + 4), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, (255, 255, 255, 160),
                     (0, 0, width + 6 + extra_w, height + 4),
                     border_radius=border_radius + 2)
    surface.blit(bg_surface, (x - pad_left, y - 2))

    filled_width = int(width * ratio)
    pygame.draw.rect(surface, color, (x, y, filled_width, height), border_radius=border_radius)

    value_surf = KOREAN_FONT_BOLD_18.render(value_text, True, color)
    value_rect = value_surf.get_rect()
    text_x = x + width + gap_text
    text_y = y + height // 2 - value_rect.height // 2
    surface.blit(value_surf, (text_x, text_y))
    if icon_scaled:
        icon_x = text_x + value_rect.width + gap_icon
        icon_y = y + height // 2 - scale_icon_h // 2
        surface.blit(icon_scaled, (icon_x, icon_y))

    return interpolated_hp

def draw_ammo_bar_remodeled(surface, current_ammo, max_ammo, pos, size, last_ammo_drawn):
    x, y = pos
    width, height = size
    border_radius = height // 3

    smoothing_speed = 0.5
    interpolated_ammo = last_ammo_drawn + (current_ammo - last_ammo_drawn) * smoothing_speed

    ratio = max(0, interpolated_ammo / max_ammo)
    filled_width = int(width * ratio)
    bar_color = (255, 150, 0)

    value_text = f"{int(current_ammo)}/{int(max_ammo)}"
    text_w, text_h = KOREAN_FONT_BOLD_18.size(value_text)
    icon = config.images.get("ammo_gauge_up")
    icon_w = icon.get_width() if icon else 0
    icon_h = icon.get_height() if icon else 0
    scale_icon_w = int(icon_w * 1.3)
    scale_icon_h = int(icon_h * 1.3)
    icon_scaled = pygame.transform.smoothscale(icon, (scale_icon_w, scale_icon_h)) if icon else None

    pad_left = 3
    pad_right = 8
    gap_text = 10
    gap_icon = 6
    extra_w = gap_text + text_w + ((gap_icon + scale_icon_w) if icon_scaled else 0) + pad_right

    bg_surface = pygame.Surface((width + 6 + extra_w, height + 4), pygame.SRCALPHA)
    pygame.draw.rect(bg_surface, (255, 255, 255, 160), (0, 0, width + 6 + extra_w, height + 4), border_radius=border_radius + 2)
    surface.blit(bg_surface, (x - pad_left, y - 2))

    pygame.draw.rect(surface, bar_color, (x, y, filled_width, height), border_radius=border_radius)

    value_surf = KOREAN_FONT_BOLD_18.render(value_text, True, bar_color)
    value_rect = value_surf.get_rect()
    text_x = x + width + gap_text
    text_y = y + height // 2 - value_rect.height // 2
    surface.blit(value_surf, (text_x, text_y))
    if icon_scaled:
        icon_x = text_x + value_rect.width + gap_icon
        icon_y = y + height // 2 - scale_icon_h // 2
        surface.blit(icon_scaled, (icon_x, icon_y))

    return interpolated_ammo

def draw_npc_interact_hint(screen, center_x, anchor_top_y, lines=("대화하기", "(Space)")):
    font = KOREAN_FONT_BOLD_20
    pad_x, pad_y = 8, 6
    radius = 6
    bg_alpha = 160
    line_gap = 4

    c1 = (255, 255, 255)
    c2 = (200, 200, 255)
    if len(lines) >= 2:
        surf1 = font.render(lines[0], True, c1)
        surf2 = font.render(lines[1], True, c2)
        text_w = max(surf1.get_width(), surf2.get_width())
        text_h = surf1.get_height() + surf2.get_height() + line_gap
    else:
        surf1 = font.render(lines[0], True, c1)
        surf2 = None
        text_w = surf1.get_width()
        text_h = surf1.get_height()

    box_w = text_w + pad_x * 2
    box_h = text_h + pad_y * 2 + (pad_y if surf2 else 0)

    box_x = int(center_x - box_w // 2)
    box_y = int(anchor_top_y - box_h - 10)

    bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    pygame.draw.rect(bg, (0, 0, 0, bg_alpha), bg.get_rect(), border_radius=radius)
    screen.blit(bg, (box_x, box_y))

    y = box_y + pad_y
    screen.blit(surf1, (box_x + (box_w - surf1.get_width()) // 2, y))
    if surf2:
        y += surf1.get_height() + line_gap
        screen.blit(surf2, (box_x + (box_w - surf2.get_width()) // 2, y))
        
def trigger_combat_start():
    # 방 내부 진입이 확정된 시점에서 즉시 배너
    combat_banner_fx["mode"] = "start"
    combat_banner_fx["t"] = 0.0
    combat_banner_fx["t"] = 0.0
    enemy_counter_fx["state"] = "in"
    enemy_counter_fx["t"] = 0.0

def trigger_combat_end():
    # 배너: 종료, 라벨: 페이드 아웃
    import config, pygame
    config.auto_collect_ready_at = pygame.time.get_ticks() + 500
    config.auto_collect_fired = False
    combat_banner_fx["mode"] = "end"
    combat_banner_fx["t"] = 0.0
    enemy_counter_fx["state"] = "out"
    enemy_counter_fx["t"] = 0.0
    for npc in npcs:
        tname = type(npc).__name__
        if tname == "SoldierNPC":
            if config.CURRENT_STAGE == "1-1":
                npc.dialogue = soldier1_after_dialogue
            elif config.CURRENT_STAGE == "1-3":
                npc.dialogue = soldier2_after_dialogue
            elif config.CURRENT_STAGE == "2-2":
                npc.dialogue = soldier3_after_dialogue
        elif tname == "DoctorNFNPC" and config.CURRENT_STAGE == "1-2":
            npc.dialogue = doctorNF12_after_dialogue
        elif tname == "ScientistNPC":
            if config.CURRENT_STAGE == "2-1":
                npc.dialogue = scientist2_after_dialogue
            elif config.CURRENT_STAGE == "2-3":
                npc.dialogue = scientist3_after_dialogue

def trigger_stage_banner(text):
    stage_banner_fx["text"] = text
    stage_banner_fx["t"] = 0.0

def draw_combat_indicators(screen, delta_ms, minimap_rect=None):
    # 상단 배너 업데이트/그리기
    if combat_banner_fx["mode"] is not None:
        combat_banner_fx["t"] += delta_ms
        t = combat_banner_fx["t"]
        dur = combat_banner_fx["duration"]
        progress = min(1.0, max(0.0, t / dur))
        if combat_banner_fx["mode"] == "start":
            draw_combat_banner(screen, "전투 개시", "start", progress)
        else:
            draw_combat_banner(screen, "전투 종료", "end", progress)
        if t >= dur:
            combat_banner_fx["mode"] = None
            combat_banner_fx["t"] = 0.0
    
    if stage_banner_fx["text"] is not None:
        stage_banner_fx["t"] += delta_ms
        t = stage_banner_fx["t"]
        dur = stage_banner_fx["duration"]
        stage_progress = 1.0 if dur <= 0 else min(1.0, max(0.0, t / dur))
        draw_combat_banner(screen, stage_banner_fx["text"], "end", stage_progress)
        if t >= dur:
            stage_banner_fx["text"] = None
            stage_banner_fx["t"] = 0.0

    # 우상단 남은 적 라벨
    try:
        remaining = sum(1 for e in enemies if getattr(e, "alive", False))
    except Exception:
        remaining = None
    st = enemy_counter_fx["state"]
    if st is None:
        return
    if st == "in":
        enemy_counter_fx["t"] += delta_ms
        sp = min(1.0, enemy_counter_fx["t"] / enemy_counter_fx["slide_in"])
        draw_enemy_counter(screen, remaining, slide_progress=sp, alpha=255, anchor_rect=minimap_rect, margin_y=8)
        if sp >= 1.0:
            enemy_counter_fx["state"] = "hold"
            enemy_counter_fx["t"] = 0.0
    elif st == "hold":
        draw_enemy_counter(screen, remaining, slide_progress=1.0, alpha=255, anchor_rect=minimap_rect, margin_y=8)
    elif st == "out":
        enemy_counter_fx["t"] += delta_ms
        fade = max(0, 255 - int(255 * (enemy_counter_fx["t"] / enemy_counter_fx["fade_out"])))
        draw_enemy_counter(screen, remaining, slide_progress=1.0, alpha=fade, anchor_rect=minimap_rect, margin_y=8)
        if fade <= 0:
            enemy_counter_fx["state"] = None
            enemy_counter_fx["t"] = 0.0

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

spawn_room_npcs()

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

    if getattr(config, "game_state", 1) != config.GAME_STATE_PLAYING:
        for e in events:
            if e.type == pygame.QUIT:
                running = False
        pygame.mouse.set_visible(True)
        screen.fill((0,0,0))
        logo_bottom = _draw_title(screen)

        if config.game_state == config.GAME_STATE_MENU:
            from sound_manager import play_bgm_main
            play_bgm_main()
            cx = SCREEN_WIDTH//2; base_y = 400; gap = 72
            mouse_pos = pygame.mouse.get_pos()

            # 기본 버튼 렌더 (모달이 떠 있을 때도 배경처럼 보이게 그리되, 상호작용은 막음)
            hovered = -1 if _menu_modal else -1
            for i in range(len(MENU_BUTTONS)):
                _menu_scales[i] = _lerp(_menu_scales[i], 1.08 if (_menu_hover==i and not _menu_modal) else 1.0, 0.18)
            rects = []
            for i, btn in enumerate(MENU_BUTTONS):
                cy = base_y + i*gap
                rect = _draw_button(screen, btn["label"], (cx, cy), False, _menu_scales[i])
                rects.append(rect)
                if not _menu_modal and rect.collidepoint(mouse_pos): hovered = i
            if not _menu_modal and hovered != -1 and hovered != _menu_hover:
                sounds["button_select"].play()
            _menu_hover = hovered if not _menu_modal else -1

            # 모달 입력/렌더링
            if _menu_modal:
                if _menu_modal["type"] == "confirm_quit":
                    yes_rect, no_rect = _draw_menu_confirm_quit(screen)
                    for e in events:
                        if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_n):
                            sounds["button_click"].play(); _menu_modal = None
                        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                            if yes_rect.collidepoint(mouse_pos):
                                sounds["button_click"].play()
                                running = False
                            elif no_rect.collidepoint(mouse_pos):
                                sounds["button_click"].play()
                                _menu_modal = None
                elif _menu_modal["type"] == "panel":
                    if _menu_modal["name"] == "howto":
                        close_rect = _draw_menu_panel(screen, "조작법", HOWTO_LINES[2:])  # 제목 줄 제외
                    else:
                        close_rect = _draw_menu_panel(screen, "크레딧", CREDITS_LINES[2:])
                    for e in events:
                        if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
                            sounds["button_click"].play(); _menu_modal = None
                        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and close_rect.collidepoint(mouse_pos):
                            sounds["button_click"].play(); _menu_modal = None
            else:
                # 모달이 없을 때만 메뉴 상호작용
                for e in events:
                    if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and _menu_hover != -1:
                        sounds["button_click"].play()
                        bid = MENU_BUTTONS[_menu_hover]["id"]
                        if bid == "start":
                            # 메뉴 화면을 캡처해 두고 전환 예약
                            start_transition_old_surface = screen.copy()
                            init_new_game()
                            config.game_state = config.GAME_STATE_PLAYING
                            pygame.mouse.set_visible(False)
                            start_transition_pending = True
                            from sound_manager import play_bgm_for_stage
                            play_bgm_for_stage(config.CURRENT_STAGE)
                        elif bid == "howto":
                            _menu_modal = {"type":"panel","name":"howto"}
                        elif bid == "credits":
                            _menu_modal = {"type":"panel","name":"credits"}
                        elif bid == "quit":
                            _menu_modal = {"type":"confirm_quit"}

        elif config.game_state in (config.GAME_STATE_HOWTO, config.GAME_STATE_CREDITS):
            # (이전 방식 화면 전환은 더 이상 안 쓰지만, 남겨진 상태로 진입해도
            #  사용자 경험을 해치지 않도록 메뉴 팝업과 동일하게 처리)
            target = "howto" if config.game_state == config.GAME_STATE_HOWTO else "credits"
            _menu_modal = {"type":"panel","name": target}
            config.game_state = config.GAME_STATE_MENU

        pygame.display.flip()
        clock.tick(60)
        continue

    if (mouse_left_released_after_dialogue
        or mouse_left_released_after_pause
        or mouse_left_released_after_transition):
        b = pygame.mouse.get_pressed()
        if not (b[0] or b[2]):
            mouse_left_released_after_dialogue = False
            mouse_left_released_after_pause = False
            mouse_left_released_after_transition = False

    for event in events:
        # 이벤트 처리
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.USEREVENT + 1:
            changing_room = False
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
        elif event.type == pygame.KEYDOWN:
            if player_dead or boss_intro_active:
                continue
            if event.key == pygame.K_w:
                move_up = True
            elif event.key == pygame.K_s:
                move_down = True
            elif event.key == pygame.K_a:
                move_left = True
            elif event.key == pygame.K_d:
                move_right = True
            elif event.key == pygame.K_SPACE and not dialogue_manager.active:
                if current_portal is not None:
                    player_cx = world_x + player_rect.centerx
                    player_cy = world_y + player_rect.centery
                    if current_portal.is_player_near(player_cx, player_cy):
                        old_surface = screen.copy()
                        def go_next_stage():
                            advance_to_next_stage()
                            render_game_frame()
                        swipe_curtain_transition(
                            screen, old_surface, go_next_stage, direction="up", duration=0.5
                        )
                        mouse_left_released_after_transition = True
                player_cx = world_x + player_rect.centerx
                player_cy = world_y + player_rect.centery
                for npc in npcs:
                    if npc.is_player_near(player_cx, player_cy):
                        _pending_dialogue = npc.dialogue
                        _pending_dialogue_effect_cb = apply_effect
                        _pending_dialogue_close_cb = on_dialogue_close
                        dialogue_capture_request = True 
                        mouse_left_released_after_dialogue = True
                        pygame.mouse.set_visible(False)
                        break
                player_world_x = world_x + player_rect.centerx * PLAYER_VIEW_SCALE
                player_world_y = world_y + player_rect.centery * PLAYER_VIEW_SCALE
                try_pickup_weapon()
            elif event.key == pygame.K_TAB:
                paused = not paused
                if paused:
                    pygame.mouse.set_visible(True)
                    tab_menu_selected = 0
                    selected_tab = 0
                    for b in bullets:
                        if isinstance(b, ExplosionEffectPersistent):
                            b.pause()
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
                    mouse_left_released_after_pause = True
                    screen.set_clip(None)
                    render_game_frame()
                    pygame.display.flip()
            elif event.key == pygame.K_ESCAPE and not dialogue_manager.active:
                if not pause_menu_active:
                    pause_request = True
                else:
                    pause_menu_active = False
                    confirm_quit_active = False
                    pygame.mouse.set_visible(False)
                    pause_frozen_frame = None
                    for b in bullets:
                        if isinstance(b, ExplosionEffectPersistent):
                            b.resume()
                    screen.set_clip(None)
                    render_game_frame()
                    pygame.display.flip()

                    for b in bullets:
                        if isinstance(b, ExplosionEffectPersistent):
                            b.resume()
                    mouse_left_released_after_pause = True
                    pause_frozen_frame = None
                    render_game_frame()
                    pygame.display.flip()
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                slot = event.key - pygame.K_1
                if (not getattr(melee, "active", False)) and 0 <= slot < len(weapons) and current_weapon_index != slot:
                    sounds["swap_gun"].play()
                    if hasattr(weapons[current_weapon_index], "on_weapon_switch"):
                        weapons[current_weapon_index].on_weapon_switch()
                    changing_weapon = True
                    change_weapon_target = slot
                    change_animation_timer = 0.0
                    previous_distance = current_distance
                    target_distance = weapons[slot].distance_from_center
            elif event.key == pygame.K_v:
                # 무기 교체 중엔 근접 불허
                melee.try_start(is_switching_weapon=changing_weapon)
            elif event.key == pygame.K_q:
                print("[DEBUG] Q pressed: Killing all enemies instantly (dev cheat)")
                cx, cy = current_room_pos
                for enemy in enemies[:]:
                    if enemy.alive:
                        enemy.hit(9999, config.blood_effects)  # 강제로 사망시킴
                        enemies.remove(enemy)
                room_key = (cx, cy)

                if grid[cy][cx] == 'E':
                    room_portals[room_key] = True
                    portal_spawn_at_ms = pygame.time.get_ticks() + 500
                    print("[DEBUG] Boss room cleared via cheat. Portal will spawn in 0.5s.")

                if room_key in visited_f_rooms:
                    visited_f_rooms[room_key]["cleared"] = True

                world.update_room_state_after_combat(cy, cx)

                config.combat_state = False
                config.combat_enabled = False
                trigger_combat_end()

                for wall in combat_walls:
                    if wall in obstacle_manager.combat_obstacles:
                        obstacle_manager.combat_obstacles.remove(wall)
                combat_walls.clear()

                for info in combat_walls_info:
                    info["state"] = "hiding"
                    info["target_pos"] = info["start_pos"]
        elif event.type == pygame.KEYUP:
            if player_dead or boss_intro_active:
                continue
            if event.key == pygame.K_w:
                move_up = False
            elif event.key == pygame.K_s:
                move_down = False
            elif event.key == pygame.K_a:
                move_left = False
            elif event.key == pygame.K_d:
                move_right = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 사망 상태: 회색 페이드/블랙 전환 동안 클릭 무시
            if player_dead or boss_intro_active:
                if (pygame.time.get_ticks() - death_started_ms) >= (death_gray_duration + death_black_delay):
                    if event.button == 1:
                        if _go_retry_rect and _go_retry_rect.collidepoint(event.pos):
                            sounds["button_click"].play()
                            _retry_requested = True
                        elif _go_exit_rect and _go_exit_rect.collidepoint(event.pos):
                            sounds["button_click"].play()
                            _exit_requested = True
                continue
            # 일시정지 메뉴 또는 대화 중에는 게임용 마우스 플래그를 건드리지 않는다
            if pause_menu_active or dialogue_manager.active:
                pass
            else:
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
            if player_dead or boss_intro_active:
                continue
            if pause_menu_active or dialogue_manager.active:
                pass
            else:
                if event.button == 1:
                    mouse_left_button_down = False
                elif event.button == 3:
                    mouse_right_button_down = False
                    
    if player_dead:
        move_left = move_right = move_up = move_down = False

    if dialogue_manager.active:
        if dialogue_frozen_frame is not None:
            screen.blit(dialogue_frozen_frame, (0, 0))
        else:
            render_game_frame()
        dialogue_manager.update(events)
        dialogue_manager.set_hud_status(player_hp, player_hp_max, ammo_gauge, ammo_gauge_max)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        dialogue_manager.draw(screen)
        pygame.display.flip()
        clock.tick(60)
        continue

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
            ui_tab_rects = draw_status_tab(
                screen,
                player_hp, player_hp_max,
                ammo_gauge, ammo_gauge_max,
                selected_tab, sounds,
                kill_count,
                len(weapons)
            )
        pygame.display.flip()
        clock.tick(60)
        continue

    if pause_menu_active:
        if not pygame.mouse.get_visible():
            pygame.mouse.set_visible(True)
        if pause_frozen_frame is not None:
            screen.blit(pause_frozen_frame, (0,0))
        else:
            screen.fill((0,0,0))
            world_instance.draw_full(
                screen, world_x, world_y, shake_offset_x, shake_offset_y,
                combat_walls_info, obstacle_manager, expansion
            )
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,160))
        screen.blit(overlay, (0,0))

        cx, base_y, gap = SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 10, 80
        mouse_pos = pygame.mouse.get_pos()
        hovered = -1
        btn_rects = []
        for i, btn in enumerate(pause_buttons):
            target = 1.08 if pause_menu_hover == i else 1.0
            pause_scales[i] = _lerp(pause_scales[i], target, 0.15)
        for i, btn in enumerate(pause_buttons):
            cy = base_y + i*gap
            rect = _draw_button(screen, btn["label"], (cx, cy), False, pause_scales[i])
            btn_rects.append(rect)
            if rect.collidepoint(mouse_pos): hovered = i
        if hovered != -1 and hovered != pause_menu_hover:
            sounds["button_select"].play()
        pause_menu_hover = hovered

        _pause_title_surf = TITLE_FONT.render("일시정지", True, (240, 240, 240))
        _pause_title_surf = pygame.transform.smoothscale(_pause_title_surf, (int(_pause_title_surf.get_width()*1.8), int(_pause_title_surf.get_height()*1.8)))
        screen.blit(_pause_title_surf, ((SCREEN_WIDTH - _pause_title_surf.get_width()) // 2, 120))

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if confirm_quit_active:
                    pass
                elif pause_menu_hover != -1:
                    sounds["button_click"].play()
                    bid = pause_buttons[pause_menu_hover]["id"]
                    if bid == "resume":
                        pause_menu_active = False
                        pygame.mouse.set_visible(False)
                        for b in bullets:
                            if isinstance(b, ExplosionEffectPersistent):
                                b.resume()
                        mouse_left_released_after_pause = True
                        pause_frozen_frame = None
                        render_game_frame()
                        pygame.display.flip()
                    elif bid == "quit":
                        confirm_quit_active = True
                        confirm_hover = -1
                        confirm_left_released = False

        if confirm_quit_active:
            popup_w, popup_h = 520, 220
            popup = pygame.Surface((popup_w, popup_h), pygame.SRCALPHA)
            pygame.draw.rect(popup, (18,18,18,240), (0,0,popup_w,popup_h), border_radius=16)
            pygame.draw.rect(popup, (200,200,200,90), (0,0,popup_w,popup_h), width=2, border_radius=18)

            warn = SUB_FONT.render("현재 진행상황이 모두 초기화됩니다!", True, (255, 80, 80))
            popup.blit(warn, ((popup_w-warn.get_width())//2, 32))

            yes_rect = _draw_button(popup, "예",   (popup_w//2 - 100, popup_h - 60), False, confirm_scales[0])
            no_rect  = _draw_button(popup, "아니오",(popup_w//2 + 100, popup_h - 60), False, confirm_scales[1])
            pr = popup.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(popup, pr.topleft)

            mouse_pos_local = (mouse_pos[0]-pr.left, mouse_pos[1]-pr.top)
            h = -1
            if yes_rect.collidepoint(mouse_pos_local): h = 0
            elif no_rect.collidepoint(mouse_pos_local): h = 1
            if h != -1 and h != confirm_hover:
                sounds["button_select"].play()
            confirm_hover = h
            for i in range(2):
                confirm_scales[i] = _lerp(confirm_scales[i], 1.08 if i==confirm_hover else 1.0, 0.16)

            for e in events:
                if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                    confirm_left_released = True
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if not confirm_left_released:
                        continue
                    if confirm_hover == 0:  # 예
                        sounds["button_click"].play()
                        old = screen.copy()
                        def go_menu():
                            init_new_game()
                            import config as _c
                            _c.game_state = _c.GAME_STATE_MENU
                            pygame.mouse.set_visible(True)
                        swipe_curtain_transition(screen, old, go_menu, direction="up", duration=0.5)
                        pause_menu_active = False
                        confirm_quit_active = False
                        pause_frozen_frame = None
                    elif confirm_hover == 1:  # 아니오
                        sounds["button_click"].play()
                        confirm_quit_active = False

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
    if not player_dead:
        if not boss_intro_active:
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

    melee.update(enemies, config.blood_effects)

    for scatter in scattered_bullets[:]:
        scatter.update()
        if scatter.alpha <= 0:
            scattered_bullets.remove(scatter)

    for effect in config.effects[:]:
        if hasattr(effect, "update"):
            effect.update()
        if getattr(effect, "finished", False):
            config.effects.remove(effect)
        if hasattr(effect, "alive") and not effect.alive:
            config.effects.remove(effect)

    now = pygame.time.get_ticks()
    for dot in config.active_dots[:]:
        if now >= dot["end_time"]:
            config.active_dots.remove(dot)
        else:
            # 초당 피해
            if now % 1000 < 16:  # 약 1초 간격
                config.damage_player(dot["damage"])

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

    now_ms = pygame.time.get_ticks()
    if now_ms < getattr(config, "slow_until_ms", 0):
        max_speed *= getattr(config, "move_slow_factor", 1.0)
    else:
        if hasattr(config, "move_slow_factor"):
            config.move_slow_factor = 1.0

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

    kvx = getattr(config, "knockback_impulse_x", 0.0)
    kvy = getattr(config, "knockback_impulse_y", 0.0)
    if kvx or kvy:
        world_vx += kvx
        world_vy += kvy
        config.knockback_impulse_x *= getattr(config, "KNOCKBACK_DECAY", 0.88)
        config.knockback_impulse_y *= getattr(config, "KNOCKBACK_DECAY", 0.88)
        if abs(config.knockback_impulse_x) < 0.01:
            config.knockback_impulse_x = 0.0
        if abs(config.knockback_impulse_y) < 0.01:
            config.knockback_impulse_y = 0.0

    test_world_x = world_x + world_vx
    test_world_y = world_y

    player_center_world_x = world_x + player_rect.centerx
    player_center_world_y = world_y + player_rect.centery

    if config.combat_enabled and not config.combat_state and not boss_intro_active:
        # 전투 시작 조건 체크
        if (0 <= player_center_world_x <= effective_bg_width and
            0 <= player_center_world_y <= effective_bg_height):
            cy, cx = current_room_pos[1], current_room_pos[0]
            is_boss_room = (grid[cy][cx] == 'E' and world.room_states[cy][cx] != 9)
            if is_boss_room and not boss_intro_shown_this_entry:
                old_surface = screen.copy()
                def _to_black():
                    screen.fill((0,0,0))
                swipe_curtain_transition(screen, old_surface, _to_black, direction="right", duration=0.5)
                _start_boss_intro()
                boss_intro_shown_this_entry = True
                world_vx = 0; world_vy = 0
                move_left = move_right = move_up = move_down = False
            else:
                config.combat_state = True
                trigger_combat_start()
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

    for npc in npcs:
        if hasattr(npc, "collider"):
            penetration = npc.collider.compute_penetration_circle(
                (player_center_world_x, player_center_world_y),
                player_radius,
                (npc.x, npc.y)
            )
            if penetration:
                penetration_total_x += penetration[0]

    for enemy in enemies:
        if not getattr(enemy, "alive", True):
            continue
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

    for npc in npcs:
        if hasattr(npc, "collider"):
            penetration = npc.collider.compute_penetration_circle(
                (player_center_world_x, player_center_world_y),
                player_radius,
                (npc.x, npc.y)
            )
            if penetration:
                penetration_total_y += penetration[1]

    for enemy in enemies:
        if not getattr(enemy, "alive", True):
            continue
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
        # 무기 교체 중에는 발사 입력을 완전히 차단
        effective_left  = mouse_left_button_down  and (not melee.active) and (not changing_weapon)
        effective_right = mouse_right_button_down and (not melee.active) and (not changing_weapon)

        # 대화/일시정지/전환 직후의 클릭잔상 방지
        if (mouse_left_released_after_dialogue
            or mouse_left_released_after_pause
            or mouse_left_released_after_transition):
            effective_left = False
            effective_right = False

        active_weapon = weapon

        if changing_weapon and t >= 0.5:
            active_weapon = weapons[change_weapon_target]

        # 탄약이 모자라면 자동으로 근접으로 전환
        fallback_to_melee = False
        if effective_left and getattr(active_weapon, "can_left_click", False):
            try:
                needed = getattr(active_weapon, "left_click_ammo_cost", 0)
                if active_weapon.get_ammo_gauge() < needed:
                    fallback_to_melee = True
            except Exception:
                pass
        elif effective_right and getattr(active_weapon, "can_right_click", False):
            try:
                needed = getattr(active_weapon, "right_click_ammo_cost", 0)
                if active_weapon.get_ammo_gauge() < needed:
                    fallback_to_melee = True
            except Exception:
                pass

        if fallback_to_melee:
            melee.try_start(is_switching_weapon=changing_weapon)
        else:
            # 선택한 무기만 입력 처리, 나머지는 유휴 업데이트
            if changing_weapon:
                active_weapon.on_update(False, False)
            else:
                active_weapon.on_update(effective_left, effective_right)
            for w in weapons:
                if w is not active_weapon:
                    try:
                        w.on_update(False, False)
                    except Exception:
                        pass
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

    if portal_spawn_at_ms is not None:
        now_ms = pygame.time.get_ticks()
        if now_ms >= portal_spawn_at_ms:
            portal_spawn_at_ms = None
            # 현재 방이 보스방이고, 포탈 표시한 적 없을 때만 생성
            cx, cy = current_room_pos
            if grid[cy][cx] == 'E':
                try:
                    center_x = world_instance.effective_bg_width / 2
                    center_y = world_instance.effective_bg_height / 2
                    img = images["portal"]
                    current_portal = Portal(center_x, center_y, img)
                    print("[DEBUG] Portal spawned.")
                except Exception as e:
                    print("[WARN] Portal spawn failed:", e)

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

        if grid[cy][cx] == 'E':
            room_portals[room_key] = True
            # 현재 방에 머무는 중이면 0.5초 뒤 스폰
            portal_spawn_at_ms = pygame.time.get_ticks() + 500
            print("[DEBUG] Boss room cleared. Portal will spawn in 0.5s.")

        config.combat_state = False
        config.combat_enabled = False
        trigger_combat_end()
        print("[DEBUG] Combat END. Player can go back to tunnel.")

        for wall in combat_walls:
            if wall in obstacle_manager.combat_obstacles:
                obstacle_manager.combat_obstacles.remove(wall)
        combat_walls.clear()

        for info in combat_walls_info:
            info["state"] = "hiding"
            info["target_pos"] = info["start_pos"]

    screen.set_clip(None)
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

    if current_portal is not None:
        # dt 계산(회전용)
        dt_seconds = clock.get_time() / 1000.0
        near_portal = current_portal.is_player_near(player_center_x, player_center_y)
        current_portal.update(dt_seconds)
        current_portal.draw(
            screen,
            world_x - shake_offset_x,
            world_y - shake_offset_y,
            player_near=near_portal
        )

    for fw in field_weapons[:]:
        near = fw.is_player_near(player_center_x, player_center_y)
        fw.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y, player_near=near)

    if grid[current_room_pos[1]][current_room_pos[0]] == 'A' and shop_items:
        for shop_item in shop_items:
            if shop_item.purchased:
               continue
            screen_x = shop_item.x - world_x + shake_offset_x
            screen_y = shop_item.y - world_y + shake_offset_y

            weapon_img = weapon_assets[shop_item.weapon_class.__name__.lower()]["front"]
            max_height = 48
            scale_factor = max_height / weapon_img.get_height()
            scaled_width = int(weapon_img.get_width() * scale_factor)
            scaled_height = int(weapon_img.get_height() * scale_factor)
            weapon_img_scaled = pygame.transform.smoothscale(weapon_img, (scaled_width, scaled_height))
            screen.blit(weapon_img_scaled, (screen_x - scaled_width//2, screen_y - scaled_height//2))

            dist = math.hypot(shop_item.x - player_center_x, shop_item.y - player_center_y)
            if dist < 100:
                text_color = (100,255,100) if shop_item.purchased else (160,60,255)
                key = shop_item.weapon_class.__name__.lower()
                weapon_name = weapon_stats.get(key, {}).get("name", key)
                price_text = KOREAN_FONT_BOLD_20.render(f"{shop_item.price}", True, text_color)
                name_text = KOREAN_FONT_BOLD_20.render(f"{weapon_name}", True, text_color)
                info_text = KOREAN_FONT_BOLD_20.render("구매완료" if shop_item.purchased else "구매 (Space)", True, text_color)
                y_cursor = screen_y - scaled_height//2 - price_text.get_height() - name_text.get_height() - 12
                screen.blit(price_text, (screen_x - price_text.get_width()//2, y_cursor))
                screen.blit(name_text, (screen_x - name_text.get_width()//2, y_cursor + price_text.get_height() + 2))
                screen.blit(info_text, (screen_x - info_text.get_width()//2, y_cursor + price_text.get_height() + name_text.get_height() + 6))

                if not shop_item.purchased and keys[pygame.K_SPACE]:
                    if config.player_score >= shop_item.price:
                        config.player_score -= shop_item.price
                        shop_item.purchased = True
                        if len(weapons) < 4:
                            new_weapon = shop_item.weapon_class.create_instance(
                                weapon_assets, sounds, lambda: ammo_gauge,
                                consume_ammo, get_player_world_position
                            )
                            weapons.append(new_weapon)
                            current_weapon_index = len(weapons) - 1
                        else:
                            current_weapon_class = weapons[current_weapon_index].__class__
                            dropped_fw = FieldWeapon(
                                current_weapon_class,
                                player_center_x, player_center_y,
                                weapon_assets, sounds
                            )
                            field_weapons.append(dropped_fw)
                            new_weapon = shop_item.weapon_class.create_instance(
                                weapon_assets, sounds, lambda: ammo_gauge,
                                consume_ammo, get_player_world_position
                            )
                            weapons[current_weapon_index] = new_weapon
                        sounds["swap_gun"].play()
                    else:
                        pass
            else:
                gray = (180,180,180)
                price_text = KOREAN_FONT_BOLD_20.render(f"{shop_item.price}", True, gray)
                screen.blit(price_text, (screen_x - price_text.get_width()//2, screen_y - scaled_height//2 - price_text.get_height() - 4))

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

    for blood in config.blood_effects[:]:
        # 피 이펙트 업데이트
        blood.update()
        if blood.alpha <= 0:
            config.blood_effects.remove(blood)

    for blood in config.blood_effects:
        blood.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)
    
    if not config.combat_state and getattr(config, "auto_collect_ready_at", None) is not None:
        if not getattr(config, "auto_collect_fired", False) and current_time >= config.auto_collect_ready_at:
            for _item in getattr(config, "dropped_items", []):
                if hasattr(_item, "start_magnet"):
                    _item.start_magnet(delay_ms=random.randint(0, 120))
                else:
                    try:
                        _item.state = "magnet"
                        _item.magnet_start_time = current_time
                        _item.magnet_origin = (_item.x, _item.y)
                        _px, _py = get_player_world_position()
                        _item.magnet_target = (_px, _py)
                        _item.magnet_start_dist = math.hypot(_item.x - _px, _item.y - _py)
                    except Exception:
                        pass
            config.auto_collect_fired = True

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

        from entities import GrenadeProjectile
        if isinstance(bullet, GrenadeProjectile):
            if pygame.time.get_ticks() - bullet.start_time < bullet.explosion_delay:
                # 아직 폭발 전이면 충돌 판정 스킵
                bullet.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)
                continue
        
        # Gun19 방패 판정
        from weapon import Gun19
        current_weapon = weapons[current_weapon_index]
        if isinstance(current_weapon, Gun19):
            if current_weapon.try_block_bullet(bullet):
                bullet.to_remove = True
                if bullet in config.global_enemy_bullets:
                    config.global_enemy_bullets.remove(bullet)
                continue

        if check_circle_collision(
            bullet.collider.center,
            bullet.collider.size if isinstance(bullet.collider.size, (int, float)) else 5.0,
            player_center,
            player_radius
        ):
            from entities import HomingMissile
            if isinstance(bullet, HomingMissile):
                bullet.explode()
            elif isinstance(bullet, GrenadeProjectile):
                pass
            else:
                # 일반 탄환 데미지
                damage_player(bullet.damage)
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

    # 빨간색 선 히트박스 보이기 디버그
    # for obs in obstacles_to_check:
    #     for c in obs.colliders:
    #         c.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y, (obs.world_x, obs.world_y))

    if not player_dead:
        for npc in npcs:
            npc.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

        if not dialogue_manager.active and not paused:
            for npc in npcs:
                nx = getattr(npc, "x", getattr(npc, "world_x", None))
                ny = getattr(npc, "y", getattr(npc, "world_y", None))
                img = getattr(npc, "image", None)
                if nx is None or ny is None or img is None:
                    continue

                screen_x = nx - (world_x - shake_offset_x)
                screen_y = ny - (world_y - shake_offset_y)
                top_y = screen_y - img.get_height() // 2

                draw_npc_interact_hint(
                    screen,
                    screen_x,
                    top_y,
                    lines=("대화하기", "(Space)")
                )

    display_w, display_h = screen.get_size()

    # Electric Shock 파티클 (감전 상태일 때만 스폰)
    now_ms = pygame.time.get_ticks()
    if getattr(config, "player_shock_until", 0) > now_ms:
        spawn_shock_particles(player_rect.centerx, player_rect.centery, count=2)
    update_shock_particles()
    draw_shock_particles(screen)

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

    if getattr(config, "slow_until_ms", 0) > now_ms:
        remain = config.slow_until_ms - now_ms
        duration = getattr(config, "slow_duration_ms", 3000) or 3000
        intensity = max(0.0, min(1.0, remain / float(duration)))
        if intensity > 0:
            draw_shock_overlay(screen, intensity)

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
                    if not getattr(bullet, "ignore_enemy_collision", False):
                        damage = getattr(bullet, "damage", 0)
                        enemy.hit(damage, config.blood_effects)
                        if not enemy.alive:
                            enemies.remove(enemy)
                        bullet.to_remove = True
                        hit = True
                        break

        if hit:
            bullet.to_remove = True
            continue

    if not player_dead:
        if weapon and not melee.active:
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
                if hasattr(render_weapon, "draw_overlay"):
                    try:
                        render_weapon.draw_overlay(screen)
                    except Exception:
                        pass
    melee.draw(screen, (world_x - shake_offset_x, world_y - shake_offset_y))
    if not player_dead:
        screen.blit(rotated_player_image, rotated_player_rect.move(shake_offset_x, shake_offset_y))
    
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
        screen.set_clip(None)
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
        for blood in config.blood_effects:
            blood.draw(screen, world_x, world_y)
        for enemy in enemies:
            enemy.draw(screen, world_x, world_y, shake_offset_x, shake_offset_y)

        obstacle_manager.draw_trees(screen, world_x, world_y, player_center_world, enemies)

        now_ms = pygame.time.get_ticks()
        if now_ms < getattr(config, "slow_until_ms", 0):
            spawn_shock_particles(player_rect.centerx, player_rect.centery, count=2)
        update_shock_particles()
        draw_shock_particles(screen)

    if start_transition_pending:
        def _draw_game():
            render_game_frame()
        swipe_curtain_transition(
            screen,
            start_transition_old_surface,
            _draw_game,
            direction="down",
            duration=0.5
        )
        start_transition_pending = False
        mouse_left_released_after_transition = True

    if slide_direction:
        # 방 전환 실행
        def draw_new_room():
            change_room(next_dir)
            render_game_frame()
        old_surface = screen.copy()
        swipe_curtain_transition(screen, old_surface, draw_new_room, direction=slide_direction, duration=0.5)
        mouse_left_released_after_transition = True
        k = pygame.key.get_pressed()
        move_up    = k[pygame.K_w] or k[pygame.K_UP]
        move_down  = k[pygame.K_s] or k[pygame.K_DOWN]
        move_left  = k[pygame.K_a] or k[pygame.K_LEFT]
        move_right = k[pygame.K_d] or k[pygame.K_RIGHT]
        world_vx = 0; world_vy = 0

        now_ms = pygame.time.get_ticks()
        if now_ms < getattr(config, "stunned_until_ms", 0):
            move_left = move_right = move_up = move_down = False

    if not player_dead:
        score_box = pygame.Surface((180, 30), pygame.SRCALPHA)
        pygame.draw.rect(score_box, (255, 255, 255, 120), score_box.get_rect(), border_radius=14)
        score_box_x = 30
        score_box_y = SCREEN_HEIGHT - 120 - 30 + 30
        screen.blit(score_box, (score_box_x, score_box_y))
        score_text = KOREAN_FONT_BOLD_20.render(f"악의 정수: {config.player_score}", True, (63, 0, 153))
        screen.blit(score_text, (score_box_x + 10, score_box_y + 2))

    max_stack = 3
    stack_gap = 24

    if not player_dead:
        for i, entry in enumerate(config.score_gain_texts[:]):
            font = KOREAN_FONT_BOLD_20
            surface = font.render(entry["text"], True, (63, 0, 153))
            surface.set_alpha(entry["alpha"])

            y_offset = i * stack_gap
            draw_y = entry["y"] - y_offset
            screen.blit(surface, (score_box_x + 120, draw_y))

            if entry.get("delay", 0) > 0:
                entry["delay"] -= 1
                continue

            entry["y"] -= 1
            entry["alpha"] -= 5
            entry["lifetime"] -= 1

            if entry["lifetime"] <= 0 or entry["alpha"] <= 0:
                config.score_gain_texts.remove(entry)

    if len(config.score_gain_texts) > max_stack:
        del config.score_gain_texts[0:len(config.score_gain_texts) - max_stack]

    fps = clock.get_fps()
    fps_surface = DEBUG_FONT.render(f"FPS: {fps:.1f}", True, (255, 255, 0))
    screen.blit(fps_surface, (10, 10))

    if not player_dead:
        minimap_rect = draw_minimap(screen, grid, current_room_pos)
        draw_weapon_ui(screen, weapons, current_weapon_index)
        if current_boss and current_boss.alive:
            last_boss_hp_visual = draw_boss_hp_bar(screen, current_boss, last_boss_hp_visual)
        draw_combat_indicators(screen, delta_time, minimap_rect)

    if not player_dead:
        ammo_bar_pos = (30, SCREEN_HEIGHT - 80)
        ammo_bar_size = (400, 20)
        last_ammo_visual = draw_ammo_bar_remodeled(screen, ammo_gauge, ammo_gauge_max, ammo_bar_pos, ammo_bar_size, last_ammo_visual)
        hp_bar_pos = (30, SCREEN_HEIGHT - 50)
        hp_bar_size = (400, 20)
        last_hp_visual = draw_hp_bar_remodeled(screen, player_hp, player_hp_max, hp_bar_pos, hp_bar_size, last_hp_visual)

    if (getattr(config, "game_state", 1) == config.GAME_STATE_PLAYING
        and not pause_menu_active
        and not paused
        and not dialogue_manager.active):

        if dialogue_capture_request:
            dialogue_frozen_frame = screen.copy()
            for b in bullets:
                if isinstance(b, ExplosionEffectPersistent):
                    b.pause()
            dialogue_manager.start(
                _pending_dialogue,
                on_effect_callback=_pending_dialogue_effect_cb,
                close_callback=_pending_dialogue_close_cb,
            )
            _pending_dialogue = None
            _pending_dialogue_effect_cb = None
            _pending_dialogue_close_cb = None
            pygame.mouse.set_visible(False)
            dialogue_capture_request = False
            pygame.display.flip()
            clock.tick(60)
            continue
        if pause_request:
            pause_frozen_frame = screen.copy()
            pause_menu_active = True
            confirm_quit_active = False
            pygame.mouse.set_visible(True)
            pause_request = False
            for b in bullets:
                if isinstance(b, ExplosionEffectPersistent):
                    b.pause()
            pygame.display.flip()
            clock.tick(60)
            continue

    # 사망 연출 & 게임오버 UI
    if player_dead:
        now = pygame.time.get_ticks()
        elapsed = now - death_started_ms
        gray_t = max(0.0, min(1.0, elapsed / float(death_gray_duration)))
        frame = screen.copy()
        _apply_gray_blend_inplace(frame, gray_t, preserve_red=True)
        screen.blit(frame, (0, 0))

        if elapsed >= death_gray_duration + death_black_delay:
            if not gameover_sfx_played:
                try:
                    if "knife_kill" in sounds:
                        sounds["knife_kill"].play()
                except Exception:
                    pass
                gameover_sfx_played = True
            screen.fill((0, 0, 0))
            pygame.mouse.set_visible(True)

            title = TITLE_FONT.render("사망하였습니다.", True, (235, 235, 235))
            sub   = SUB_FONT.render("당신의 운명이 중단되었습니다.", True, (190, 190, 190))
            screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 220))
            screen.blit(sub,   ((SCREEN_WIDTH - sub.get_width()) // 2, 300))

            cx = SCREEN_WIDTH // 2
            base_y = 420
            gap = 80
            mouse_pos = pygame.mouse.get_pos()
            hovered = -1
            for i in range(2):
                _go_scales[i] = _go_scales[i] + (1.08 - _go_scales[i]) * 0.18 if i == _go_hover else _go_scales[i] + (1.00 - _go_scales[i]) * 0.18
            _go_retry_rect = _draw_button(screen, "재시도", (cx, base_y),   False, _go_scales[0])
            _go_exit_rect  = _draw_button(screen, "나가기", (cx, base_y+gap), False, _go_scales[1])
            if _go_retry_rect.collidepoint(mouse_pos): hovered = 0
            if _go_exit_rect .collidepoint(mouse_pos): hovered = 1
            if hovered != -1 and hovered != _go_hover:
                sounds["button_select"].play()
            _go_hover = hovered

            if _retry_requested:
                old_surface = screen.copy()
                init_new_game()
                def _draw_new():
                    render_game_frame()
                swipe_curtain_transition(screen, old_surface, _draw_new, direction="right", duration=0.5)
                pygame.mouse.set_visible(False)
                _retry_requested = False
                _exit_requested = False
                _go_hover = -1
                _go_scales[:] = [1.0, 1.0]
                player_dead = False
                gameover_sfx_played = False
                from sound_manager import play_bgm_for_stage
                play_bgm_for_stage(config.CURRENT_STAGE)
            elif _exit_requested:
                old_surface = screen.copy()
                def _draw_menu():
                    screen.fill((0,0,0))
                    _draw_title(screen)
                config.game_state = config.GAME_STATE_MENU
                swipe_curtain_transition(screen, old_surface, _draw_menu, direction="down", duration=0.5)
                pygame.mouse.set_visible(True)
                _retry_requested = False
                _exit_requested  = False
                _go_hover = -1
                _go_scales[:] = [1.0, 1.0]
                player_dead = False
                gameover_sfx_played = False
    elif boss_intro_active:
        # 연출 동안엔 완전 검정 배경 위에 텍스트만
        screen.fill((0,0,0))
        _draw_boss_intro(screen)
        if pygame.time.get_ticks() - boss_intro_start_ms >= boss_intro_duration:
            boss_intro_active = False
            config.combat_enabled = True
            config.combat_state = True
            trigger_combat_start()
            old_surface = screen.copy()
            def _draw_game():
                render_game_frame()
            swipe_curtain_transition(screen, old_surface, _draw_game, direction="left", duration=0.5)
    else:
        cursor_rect = cursor_image.get_rect(center=(mouse_x, mouse_y))
        screen.blit(cursor_image, cursor_rect)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()