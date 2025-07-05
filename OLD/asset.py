import pygame
import os

# Pygame 초기화
pygame.init()

# 화면 설정
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("이미지 크기 및 위치 조절 예제")

# --- 이미지 파일 경로 설정 ---
current_dir = os.path.dirname(__file__)
preview_image_path = os.path.join(current_dir, "Asset", "preview.png")
previewgun_image_path = os.path.join(current_dir, "Asset", "previewgunhand.png")

# --- 이미지 불러오기 (원본 크기 확인용) ---
# 이 단계에서 이미지를 먼저 불러와 원본 크기를 확인합니다.
try:
    original_preview_image = pygame.image.load(preview_image_path).convert_alpha()
    original_preview_width, original_preview_height = original_preview_image.get_size()

    original_previewgun_image = pygame.image.load(previewgun_image_path).convert_alpha()
    original_previewgun_width, original_previewgun_height = original_previewgun_image.get_size()

except pygame.error as e:
    print(f"이미지를 불러오는 데 실패했습니다: {e}")
    print(f"경로 확인: {preview_image_path} 또는 {previewgun_image_path}")
    pygame.quit()
    exit()

# --- 이미지 크기 조절 값 설정 ---
# 이 값들을 직접 변경하여 이미지 크기를 조절할 수 있습니다.
# 0으로 설정하면 원본 크기를 유지합니다.
# 비율 유지를 원하면, 한쪽 값만 (예: 너비만) 설정하고 다른 쪽은 0으로 둔 후,
# 아래 주석 처리된 '비율 유지 코드'를 사용하세요.

# preview.png 크기
# 원본 크기: (가로: {original_preview_width}, 세로: {original_preview_height})
preview_new_width = 75 # 원하는 너비 설정
preview_new_height = int(original_preview_height * (preview_new_width / original_preview_width)) # 높이 자동 계산

# previewgun.png 크기
# 원본 크기: (가로: {original_previewgun_width}, 세로: {original_previewgun_height})
previewgun_new_width = 30 # 원하는 너비 설정
previewgun_new_height = int(original_previewgun_height * (previewgun_new_width / original_previewgun_width)) # 높이 자동 계산


# --- 이미지 위치 조절 값 설정 ---
# 이 값들을 직접 변경하여 이미지 위치를 조절할 수 있습니다.
# 양수는 오른쪽/아래로, 음수는 왼쪽/위로 이동합니다.

# preview.png (화면 정중앙 기준 오프셋)
preview_offset_x = 0
preview_offset_y = 0

# previewgun.png (화면 정중앙 기준 오프셋)
previewgun_offset_x = 10
previewgun_offset_y = -55 # 이전 요청에 따라 기본값으로 -50 설정

# --- 이미지 크기 조절 및 최종 Rect 설정 ---

# preview.png 크기 조절 및 상하 반전
if preview_new_width == 0 or preview_new_height == 0: # 0으로 설정 시 원본 크기 유지
    preview_image = original_preview_image
else:
    preview_image = pygame.transform.scale(original_preview_image, (preview_new_width, preview_new_height))

# --- 여기에서 preview.png를 상하 반전합니다. ---
preview_image = pygame.transform.flip(preview_image, False, True) # False: 가로 반전 안함, True: 세로 반전 함

preview_rect = preview_image.get_rect()
preview_rect.center = (screen_width // 2 + preview_offset_x, screen_height // 2 + preview_offset_y)

# previewgun.png 크기 조절
if previewgun_new_width == 0 or previewgun_new_height == 0: # 0으로 설정 시 원본 크기 유지
    previewgun_image = original_previewgun_image
else:
    previewgun_image = pygame.transform.scale(original_previewgun_image, (previewgun_new_width, previewgun_new_height))
previewgun_rect = previewgun_image.get_rect()
previewgun_rect.center = (screen_width // 2 + previewgun_offset_x, screen_height // 2 + previewgun_offset_y)


# 게임 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 배경을 흰색으로 채웁니다.
    screen.fill((255, 255, 255))

    # 이미지를 화면에 그립니다.
    # previewgun_image를 먼저 그려서 아래에 깔고,
    # 그 위에 preview_image를 그려서 위에 보이도록 합니다.
    screen.blit(previewgun_image, previewgun_rect)
    screen.blit(preview_image, preview_rect)

    # 화면 업데이트
    pygame.display.flip()

# Pygame 종료
pygame.quit()