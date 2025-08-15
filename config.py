import os
import pygame

# 플레이어 시야 스케일 (1.0 = 기본 시야)
PLAYER_VIEW_SCALE = 0.9

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750

# 게임 메뉴
GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_HOWTO = 2
GAME_STATE_CREDITS = 3
game_state = 1

# 배경 크기
BG_WIDTH = int(1600 * PLAYER_VIEW_SCALE)
BG_HEIGHT = int(1200 * PLAYER_VIEW_SCALE)

# 경로
BASE_DIR = os.path.dirname(__file__)
ASSET_DIR = os.path.join(BASE_DIR, "Asset")

# 속도
NORMAL_MAX_SPEED = 6
SPRINT_MAX_SPEED = 30 #9 디버그

# 사운드 설정
WALK_VOLUME = 0.5

STAGE_DATA = {
    "1-1": {
        "boss_map": 0,
        "enemy_rank_range": (1, 3),
        "min_f_rooms": 5,
        "max_f_rooms": 6,
        "acquire_rooms": 2,
        "weapon_tier_weights": {1: 58, 2: 28, 3: 14}
    },
    "1-2": {
        "boss_map": 1,
        "enemy_rank_range": (1, 4),
        "min_f_rooms": 5,
        "max_f_rooms": 6,
        "acquire_rooms": 2,
        "weapon_tier_weights": {1: 55, 2: 33, 3: 12}
    },
    "1-3": {
        "boss_map": 2,
        "enemy_rank_range": (2, 5),
        "min_f_rooms": 6,
        "max_f_rooms": 7,
        "acquire_rooms": 3,
        "weapon_tier_weights": {1: 42, 2: 38, 3: 18, 4: 2}
    },
    "2-1": {
        "boss_map": 0,
        "enemy_rank_range": (2, 5),
        "min_f_rooms": 5,
        "max_f_rooms": 6,
        "acquire_rooms": 2,
        "weapon_tier_weights": {1: 22, 2: 52, 3: 22, 4: 4}
    },
    "2-2": {
        "boss_map": 1,
        "enemy_rank_range": (3, 6),
        "min_f_rooms": 6,
        "max_f_rooms": 7,
        "acquire_rooms": 2,
        "weapon_tier_weights": {1: 12, 2: 50, 3: 32, 4: 6}
    },
    "2-3": {
        "boss_map": 2,
        "enemy_rank_range": (3, 6),
        "min_f_rooms": 6,
        "max_f_rooms": 8,
        "acquire_rooms": 3,
        "weapon_tier_weights": {1: 8, 2: 45, 3: 38, 4: 9}
    },
    "3-1": {
        "boss_map": 0,
        "enemy_rank_range": (4, 7),
        "min_f_rooms": 6,
        "max_f_rooms": 8,
        "acquire_rooms": 3,
        "weapon_tier_weights": {1: 4, 2: 32, 3: 46, 4: 15, 5: 3}
    },
    "3-2": {
        "boss_map": 1,
        "enemy_rank_range": (5, 8),
        "min_f_rooms": 7,
        "max_f_rooms": 8,
        "acquire_rooms": 3,
        "weapon_tier_weights": {1: 1, 2: 22, 3: 46, 4: 24, 5: 7}
    },
    "3-3": {
        "boss_map": 2,
        "enemy_rank_range": (6, 9),
        "min_f_rooms": 8,
        "max_f_rooms": 9,
        "acquire_rooms": 4,
        "weapon_tier_weights": {1: 0, 2: 12, 3: 38, 4: 33, 5: 17}
    },
}
CURRENT_STAGE = "1-3"

STAGE_PRICE_MULT = {
    "1-1": 1.00,
    "1-2": 1.15,
    "1-3": 1.30,
    "2-1": 1.45,
    "2-2": 1.60,
    "2-3": 1.80,
    "3-1": 2.00,
    "3-2": 2.25,
    "3-3": 2.50,
}

def get_stage_price_mult(stage=None):
    s = stage or CURRENT_STAGE
    return STAGE_PRICE_MULT.get(s, 1.0)

# 1회 업그레이드 증가량
DRONE_HP_MAX_STEP = 20
DRONE_AMMO_MAX_STEP = 20
# 시작 비용(악의 정수), 업그레이드할수록 성장률로 증가
DRONE_HP_UP_BASE_COST = 30
DRONE_AMMO_UP_BASE_COST = 30
DRONE_COST_GROWTH = 1.35
# 누적 업그레이드 횟수(런타임 저장용)
drone_hp_up_count = 0
drone_ammo_up_count = 0

STAGE_THEME = {
    "1-1": "map1", "1-2": "map1", "1-3": "map1",
    "2-1": "map2", "2-2": "map2", "2-3": "map2",
    "3-1": "map3", "3-2": "map3", "3-3": "map3",
}

TIER_PRICES = {
    1: 20,
    2: 40,
    3: 60,
    4: 85,
    5: 100
}

combat_state = False
combat_enabled = True
images = None
player_score = 10000 # 디버그, 원래는 0

ESSENCE_COST_PER_HP = 0.30
ESSENCE_COST_PER_AMMO = 0.20

MERCHANT_COOLDOWN_MS = 180

global_enemy_bullets = []
all_enemies = []
blood_effects = []
dropped_items = []
score_gain_texts = []
effects = []
active_mines = []

# 감전 디버프
stunned_until_ms = 0
slow_until_ms = 0
move_slow_factor = 1.0
slow_started_ms = 0
slow_duration_ms = 0
shock_particles = []
next_shock_spawn_ms = 0

knockback_impulse_x = 0.0
knockback_impulse_y = 0.0
KNOCKBACK_DECAY = 0.88

def apply_knockback(dx, dy):
    # 내부적으로 속도형 임펄스로 누적 후 main.py에서 프레임별 감쇠 적용.
    global knockback_impulse_x, knockback_impulse_y

    knockback_impulse_x += dx / 18.0
    knockback_impulse_y += dy / 18.0