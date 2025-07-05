import os

# 화면 크기
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# 배경 크기
BG_WIDTH = 1600
BG_HEIGHT = 1200

# 경로
BASE_DIR = os.path.dirname(__file__)
ASSET_DIR = os.path.join(BASE_DIR, "Asset")
OBJ_PATH = os.path.join(BASE_DIR, "Asset", "3DObject", "Gun13DObject.obj")

# 속도
NORMAL_MAX_SPEED = 5.0
SPRINT_MAX_SPEED = 7.5

# 사운드 설정
WALK_VOLUME = 0.5
GUN1_VOLUME = 1.0
