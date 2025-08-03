import os
import pygame

# 플레이어 시야 스케일 (1.0 = 기본 시야)
PLAYER_VIEW_SCALE = 0.9

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750

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
GUN1_VOLUME = 1.0
GUN2_VOLUME = 1.0
GUN3_VOLUME = 1.0

STAGE_DATA = {
    "1-1": {
        "boss_map": 0,  # BOSS_MAPS[0] == BOSS_MAP_1
        "enemy_rank_range": (1, 3),
        "min_f_rooms": 5,
        "max_f_rooms": 6,
        "acquire_rooms": 2
    },
    "1-2": {
        "boss_map": 1,
        "enemy_rank_range": (1, 4),
        "min_f_rooms": 5,
        "max_f_rooms": 6,
        "acquire_rooms": 2
    },
    "1-3": {
        "boss_map": 2,
        "enemy_rank_range": (2, 5),
        "min_f_rooms": 6,
        "max_f_rooms": 7,
        "acquire_rooms": 3
    }
}
CURRENT_STAGE = "1-1"

combat_state = False
combat_enabled = True
images = None

global_enemy_bullets = []
all_enemies = []
blood_effects = []
dropped_items = []
effects = []

# Gun1, Gun2, Gun3 zoom level 초기값
GUN1_ZOOM_LEVEL = -1.0
GUN2_ZOOM_LEVEL = -300.0
GUN3_ZOOM_LEVEL = -7.0

# Gun1 zoom limits
GUN1_MIN_ZOOM = -5.0
GUN1_MAX_ZOOM = -0.001

# Gun2 zoom limits
GUN2_MIN_ZOOM = -500.0
GUN2_MAX_ZOOM = -250.0

# Gun3 zoom limits
GUN3_MIN_ZOOM = -20.0
GUN3_MAX_ZOOM = -4.0

# 무기별 zoom 비율 (10%로 설정)
GUN1_ZOOM_RATIO = 0.10
GUN2_ZOOM_RATIO = 0.10
GUN3_ZOOM_RATIO = 0.10

# 폰트
pygame.font.init()
DEBUG_FONT = pygame.font.SysFont('malgungothic', 24)

# OBJ 경로
OBJ_PATHS = {
    1: os.path.join(ASSET_DIR, "3DObject", "Gun13DObject.obj"),
    2: os.path.join(ASSET_DIR, "3DObject", "Gun23DObject.obj"),
    3: os.path.join(ASSET_DIR, "3DObject", "Gun33DObject.obj"),
}
