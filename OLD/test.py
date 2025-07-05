import pygame
import math
import os
import random # 탄퍼짐을 위해 random 모듈 추가

# 1. Pygame 초기화
pygame.init()
pygame.font.init()

# 화면 설정
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pygame 캐릭터와 총 제어")

# 2. 이미지 로드 및 플레이어 설정
current_dir = os.path.dirname(__file__)
player_image_path = os.path.join(current_dir, "Asset", "image", "player.png")
gun_image_path_1 = os.path.join(current_dir, "Asset", "image", "Testgun.png") # 1번 총 이미지
gun_image_path_2 = os.path.join(current_dir, "Asset", "image", "Testgun2.png") # 2번 총 이미지
bullet_image_path = os.path.join(current_dir, "Asset", "image", "Bullet.png") # 총알 이미지 경로

try:
    original_player_image = pygame.image.load(player_image_path).convert_alpha()
except pygame.error as e:
    print(f"오류: 플레이어 이미지 로드 실패 - {e}")
    pygame.quit()
    exit()

try:
    original_gun_image_1 = pygame.image.load(gun_image_path_1).convert_alpha()
except pygame.error as e:
    print(f"오류: 1번 총 이미지 로드 실패 - {e}")
    pygame.quit()
    exit()

try:
    original_gun_image_2 = pygame.image.load(gun_image_path_2).convert_alpha()
except pygame.error as e:
    print(f"오류: 2번 총 이미지 로드 실패 - {e}")
    pygame.quit()
    exit()

try:
    original_bullet_image = pygame.image.load(bullet_image_path).convert_alpha()
except pygame.error as e:
    print(f"오류: 총알 이미지 로드 실패 - {e}")
    pygame.quit()
    exit()

# 크기 조절
player_size = 50
original_player_image = pygame.transform.scale(original_player_image, (player_size, player_size))

gun_size = (50, 40)  # 총 이미지 크기 (두 총 모두 동일하게 적용)
original_gun_image_1 = pygame.transform.scale(original_gun_image_1, gun_size)
original_gun_image_2 = pygame.transform.scale(original_gun_image_2, gun_size)

bullet_size = (5, 10) # 총알 이미지 크기 설정 (요청에 따라 변경)
original_bullet_image = pygame.transform.scale(original_bullet_image, bullet_size)

# 플레이어 초기 위치
player_rect = original_player_image.get_rect(center=(screen_width // 2, screen_height // 2))

# 이동 및 속도 변수
player_vx = 0.0
player_vy = 0.0

normal_max_speed = 5.0
sprint_max_speed = 7.5
max_speed = normal_max_speed # 이 변수는 Shift 키에 의해 변경되는 '기본' 최대 속도입니다.

acceleration_rate = 0.5
deceleration_rate = 0.7

# 폰트 설정 (디버그용)
debug_font = pygame.font.SysFont('malgungothic', 24)

# 이동 상태 변수
move_left = False
move_right = False
move_up = False
move_down = False

# 총알 관련 변수
bullets = [] # 발사된 총알들을 저장할 리스트
last_shot_time = 0 # 마지막 총알 발사 시간 (밀리초)

# 마우스 버튼 상태 변수
mouse_left_button_down = False # 마우스 왼쪽 버튼이 눌렸는지 여부 (자동 발사용)
mouse_right_button_down = False # 마우스 오른쪽 버튼이 눌렸는지 여부 (2번 총 조준용)

# 현재 선택된 총 (1 또는 2)
current_weapon = 1

# 총알 클래스 정의
class Bullet:
    def __init__(self, x, y, target_x, target_y, spread_angle_degrees, speed=15):
        self.image = original_bullet_image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

        # 마우스 위치와 총알 발사 위치 사이의 각도 계산
        angle_to_mouse_radians = math.atan2(target_y - y, target_x - x)
        
        # 탄퍼짐 적용: -spread_angle_degrees/2 부터 +spread_angle_degrees/2 사이의 랜덤 각도 추가
        spread_radians = math.radians(random.uniform(-spread_angle_degrees / 2, spread_angle_degrees / 2))
        final_angle_radians = angle_to_mouse_radians + spread_radians

        # 최종 각도를 이용해 총알의 속도 벡터 계산
        self.vx = self.speed * math.cos(final_angle_radians)
        self.vy = self.speed * math.sin(final_angle_radians)

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

    def draw(self, screen):
        # 총알 이미지 회전 (총알이 향하는 방향으로 회전)
        # atan2의 결과는 -pi에서 pi 사이이므로, degrees로 변환 후 -90을 더해 이미지를 올바르게 정렬
        angle_degrees = math.degrees(math.atan2(self.vy, self.vx))
        rotated_bullet_image = pygame.transform.rotate(self.image, -angle_degrees - 90)
        rotated_bullet_rect = rotated_bullet_image.get_rect(center=self.rect.center)
        screen.blit(rotated_bullet_image, rotated_bullet_rect)

    def is_offscreen(self, screen_width, screen_height):
        # 총알이 화면 밖으로 나갔는지 확인
        return (self.rect.right < 0 or self.rect.left > screen_width or
                self.rect.bottom < 0 or self.rect.top > screen_height)

clock = pygame.time.Clock()
running = True

while running:
    current_time = pygame.time.get_ticks() # 현재 시간 (밀리초) 가져오기

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                move_up = True
            elif event.key == pygame.K_s:
                move_down = True
            elif event.key == pygame.K_a:
                move_left = True
            elif event.key == pygame.K_d:
                move_right = True
            elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                max_speed = sprint_max_speed # Shift 누르면 스프린트 속도
            elif event.key == pygame.K_1: # 1번 키를 누르면 1번 총으로 변경
                current_weapon = 1
            elif event.key == pygame.K_2: # 2번 키를 누르면 2번 총으로 변경
                current_weapon = 2
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                move_up = False
            elif event.key == pygame.K_s:
                move_down = False
            elif event.key == pygame.K_a:
                move_left = False
            elif event.key == pygame.K_d:
                move_right = False
            elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                max_speed = normal_max_speed # Shift 떼면 일반 속도
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # 마우스 왼쪽 버튼
                if current_weapon == 1: # 1번 총: 클릭 시 한 발 발사
                    if current_time - last_shot_time > 500: # 0.5초 쿨타임
                        new_bullet = Bullet(player_rect.centerx, player_rect.centery, mouse_x, mouse_y, 10) # 중간 탄퍼짐 (10도)
                        bullets.append(new_bullet)
                        last_shot_time = current_time
                elif current_weapon == 2: # 2번 총: 왼쪽 버튼 누름 상태 시작 (자동 발사용)
                    mouse_left_button_down = True
            elif event.button == 3: # 마우스 오른쪽 버튼
                mouse_right_button_down = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: # 마우스 왼쪽 버튼 떼기
                mouse_left_button_down = False
            elif event.button == 3: # 마우스 오른쪽 버튼 떼기
                mouse_right_button_down = False

    # 가속 및 감속 처리
    if move_up:
        player_vy -= acceleration_rate
    if move_down:
        player_vy += acceleration_rate
    if move_left:
        player_vx -= acceleration_rate
    if move_right:
        player_vx += acceleration_rate

    if not (move_left or move_right):
        if player_vx > 0:
            player_vx = max(0.0, player_vx - deceleration_rate)
        elif player_vx < 0:
            player_vx = min(0.0, player_vx + deceleration_rate)
    if not (move_up or move_down):
        if player_vy > 0:
            player_vy = max(0.0, player_vy - deceleration_rate)
        elif player_vy < 0:
            player_vy = min(0.0, player_vy + deceleration_rate)

    # --- 속도 페널티 로직 ---
    # 현재 프레임에서 적용될 속도 배율
    penalty_multiplier = 1.0
    is_shooting_or_aiming_with_gun2 = False # 2번 총으로 발사 또는 조준 중인지 여부

    if current_weapon == 2:
        if mouse_left_button_down: # 2번 총으로 자동 발사 중
            penalty_multiplier *= 0.7 # 현재 속도의 30% 감소 (남은 속도 70%)
            is_shooting_or_aiming_with_gun2 = True
        if mouse_right_button_down: # 2번 총으로 조준 중
            penalty_multiplier *= 0.8 # 현재 속도의 20% 감소 (남은 속도 80%)
            is_shooting_or_aiming_with_gun2 = True

    # 현재 속도에 페널티 적용
    player_vx *= penalty_multiplier
    player_vy *= penalty_multiplier

    # --- 달리기 취소 로직 ---
    # 2번 총으로 발사 또는 조준 중이라면 달리기(스프린트) 취소
    if is_shooting_or_aiming_with_gun2:
        max_speed = normal_max_speed # Shift 키로 설정된 max_speed를 normal_max_speed로 강제 변경

    # 최종 최대 속도를 적용하여 플레이어 속도 제한
    # 여기서 max_speed는 Shift 키 상태와 달리기 취소 로직에 의해 결정된 값입니다.
    player_vx = max(-max_speed, min(max_speed, player_vx))
    player_vy = max(-max_speed, min(max_speed, player_vy))

    player_rect.x += player_vx
    player_rect.y += player_vy

    # 화면 경계 제한
    player_rect.left = max(0, player_rect.left)
    player_rect.top = max(0, player_rect.top)
    player_rect.right = min(screen_width, player_rect.right)
    player_rect.bottom = min(screen_height, player_rect.bottom)

    # 마우스 위치 및 각도 계산
    mouse_x, mouse_y = pygame.mouse.get_pos()
    player_center_x, player_center_y = player_rect.center

    dx = mouse_x - player_center_x
    dy = mouse_y - player_center_y

    angle_radians = math.atan2(dy, dx)
    angle_degrees = math.degrees(angle_radians)

    # 캐릭터 이미지 회전
    rotated_player_image = pygame.transform.rotate(original_player_image, -angle_degrees)
    rotated_player_rect = rotated_player_image.get_rect(center=player_rect.center)

    # --- 총 위치 및 회전 계산 ---
    # 현재 선택된 총 이미지 결정
    if current_weapon == 1:
        current_gun_image = original_gun_image_1
    else: # current_weapon == 2
        current_gun_image = original_gun_image_2

    # 캐릭터 크기 (회전 전 원본 이미지 기준)
    player_width, player_height = original_player_image.get_size()

    # 캐릭터의 로컬 좌표계에서 총 부착점 (캐릭터 중심이 (0,0)이라고 가정)
    local_attach_x = player_width / 2 - 25
    local_attach_y = -25 # -5 픽셀만큼 위로 이동. 필요에 따라 -10, 0, 5 등으로 조절

    # 캐릭터의 회전 각도 (라디안, Pygame의 rotate 함수 방향에 맞춤)
    char_rotation_rad = math.radians(-angle_degrees)

    # 캐릭터 회전에 따른 총 부착점의 월드 좌표 계산 (캐릭터 중심 기준)
    rotated_attach_x = local_attach_x * math.cos(char_rotation_rad) - local_attach_y * math.sin(char_rotation_rad)
    # 새로운친구님의 의도에 따라 변경된 부분
    rotated_attach_y = local_attach_x * math.sin(char_rotation_rad) - local_attach_y * math.cos(char_rotation_rad)

    # 총을 캐릭터 바깥쪽으로 밀어낼 방향 벡터 (캐릭터 중심에서 부착점까지의 벡터)
    outward_vec_x = rotated_attach_x
    outward_vec_y = rotated_attach_y

    # 벡터 정규화 (길이 1로 만듦)
    outward_vec_length = math.hypot(outward_vec_x, outward_vec_y)
    if outward_vec_length == 0: # 0으로 나누는 오류 방지
        outward_vec_length = 1
    normalized_outward_x = outward_vec_x / outward_vec_length
    normalized_outward_y = outward_vec_y / outward_vec_length

    # 총을 캐릭터 가장자리에서 바깥쪽으로 밀어낼 거리
    distance_from_edge = 20 # 15 픽셀만큼 바깥으로 이동. 필요에 따라 조절

    # 최종 총 위치 계산: 캐릭터 중심 + 회전된 부착점 + 바깥으로 밀어낸 거리
    gun_pos_x = player_center_x + rotated_attach_x + normalized_outward_x * distance_from_edge
    gun_pos_y = player_center_y + rotated_attach_y + normalized_outward_y * distance_from_edge

    # 총 이미지 회전 (캐릭터와 동일한 각도)
    rotated_gun_image = pygame.transform.rotate(current_gun_image, -angle_degrees - 90)
    rotated_gun_rect = rotated_gun_image.get_rect(center=(gun_pos_x, gun_pos_y))
    # ------------------------------------

    # 총알 발사 로직 (2번 총 자동 발사)
    if current_weapon == 2 and mouse_left_button_down: # 2번 총이 선택되었고 왼쪽 마우스 버튼이 눌려있을 때
        active_shot_cooldown = 0
        active_spread_angle = 0

        if mouse_right_button_down: # 오른쪽 마우스 버튼도 눌려있으면 (조준 모드)
            active_shot_cooldown = 300 # 0.3초 쿨타임
            active_spread_angle = 3 # 현저히 적은 탄퍼짐 (3도)
        else: # 오른쪽 마우스 버튼이 안 눌려있으면 (일반 자동 발사)
            active_shot_cooldown = 200 # 0.2초 쿨타임
            active_spread_angle = 30 # 꽤 큰 탄퍼짐 (30도)

        if current_time - last_shot_time > active_shot_cooldown:
            new_bullet = Bullet(player_center_x, player_center_y, mouse_x, mouse_y, active_spread_angle)
            bullets.append(new_bullet)
            last_shot_time = current_time

    # 화면 그리기
    screen.fill((255, 255, 255)) # 흰색 배경

    # 총알 업데이트 및 그리기
    for bullet in bullets[:]: 
        bullet.update()
        if bullet.is_offscreen(screen_width, screen_height):
            bullets.remove(bullet) # 화면 밖으로 나간 총알 제거
        else:
            bullet.draw(screen) # 총알 그리기

    screen.blit(rotated_player_image, rotated_player_rect) # 캐릭터 그리기
    screen.blit(rotated_gun_image, rotated_gun_rect) # 총 그리기

    # 디버그용 속도 표시
    current_speed_magnitude = math.sqrt(player_vx**2 + player_vy**2)
    speed_text = f"Speed: {current_speed_magnitude:.2f} (Max Cap: {max_speed:.1f})" # 표시되는 최대 속도도 변경
    text_surface = debug_font.render(speed_text, True, (0, 0, 0))
    screen.blit(text_surface, (10, 10))

    # 현재 총 표시 (디버그용)
    weapon_text = f"Weapon: {current_weapon}"
    weapon_surface = debug_font.render(weapon_text, True, (0, 0, 0))
    screen.blit(weapon_surface, (10, 40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()


"""
기말고사 끝나고 해야할것.
1.먼저 뛸때 총쏘면 그 뛰는게 사라지잖아? 근데 총 쏘거나 조준하는게 풀릴때 그때 뛰고 있었으면 마저 뛰게 하기(즉, shift키를 누르고 있었으면 마저 뛰기)
2.캐릭터 디자인 정하고 총 디자인 확립하기
3.코드 정리 좀 시키기
"""