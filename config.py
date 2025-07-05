import os
import pygame

# 화면 크기
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

SCALE_FACTOR = 0.7

# 배경 크기
BG_WIDTH = 1600
BG_HEIGHT = 1200

# 경로
BASE_DIR = os.path.dirname(__file__)
ASSET_DIR = os.path.join(BASE_DIR, "Asset")

# 속도
NORMAL_MAX_SPEED = 5.0
SPRINT_MAX_SPEED = 7.5

# 사운드 설정
WALK_VOLUME = 0.5
GUN1_VOLUME = 1.0
GUN2_VOLUME = 1.0

# Gun1, Gun2 설정
GUN1_FIRE_DELAY = 400
GUN2_FIRE_DELAY = 150

GUN1_RECOIL = 7
GUN2_RECOIL = 8

GUN1_SPEED_PENALTY = 0.05
GUN2_SPEED_PENALTY = 0.10

GUN1_DISTANCE_FROM_CENTER = 50
GUN2_DISTANCE_FROM_CENTER = 63

# Gun1, Gun2 zoom level 초기값
GUN1_ZOOM_LEVEL = -1.0
GUN2_ZOOM_LEVEL = -300.0

# Gun1 zoom limits
GUN1_MIN_ZOOM = -5.0
GUN1_MAX_ZOOM = -0.5

# Gun2 zoom limits
GUN2_MIN_ZOOM = -500.0
GUN2_MAX_ZOOM = -250.0

# 무기별 zoom 비율 (10%로 설정)
GUN1_ZOOM_RATIO = 0.10
GUN2_ZOOM_RATIO = 0.10

# 폰트
pygame.font.init()
DEBUG_FONT = pygame.font.SysFont('malgungothic', 24)

# OBJ 경로
OBJ_PATHS = {
    1: os.path.join(ASSET_DIR, "3DObject", "Gun13DObject.obj"),
    2: os.path.join(ASSET_DIR, "3DObject", "Gun23DObject.obj"),
}
