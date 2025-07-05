import pygame
import math
import os

# --- 수학 유틸리티 함수 (간단한 행렬 및 벡터 연산) ---
def multiply_matrix_vector(matrix, vector):
    """4x4 행렬과 4x1 벡터의 곱셈"""
    result = [0, 0, 0, 0]
    for i in range(4):
        for j in range(4):
            result[i] += matrix[i][j] * vector[j]
    return result

def multiply_matrices(matrix1, matrix2):
    """4x4 행렬 두 개를 곱셈"""
    result_matrix = [[0.0 for _ in range(4)] for _ in range(4)]
    for i in range(4):
        for j in range(4):
            for k in range(4):
                result_matrix[i][j] += matrix1[i][k] * matrix2[k][j]
    return result_matrix

def identity_matrix():
    """단위 행렬 생성"""
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ]

def rotate_x_matrix(angle):
    """X축 회전 행렬 (pitch)"""
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, c, -s, 0.0],
        [0.0, s, c, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ]

def rotate_y_matrix(angle):
    """Y축 회전 행렬 (yaw)"""
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        [c, 0.0, s, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-s, 0.0, c, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ]

def translate_matrix(dx, dy, dz):
    """이동 행렬"""
    return [
        [1.0, 0.0, 0.0, dx],
        [0.0, 1.0, 0.0, dy],
        [0.0, 0.0, 1.0, dz],
        [0.0, 0.0, 0.0, 1.0]
    ]

def scale_matrix(sx, sy, sz):
    """스케일 행렬"""
    return [
        [sx, 0.0, 0.0, 0.0],
        [0.0, sy, 0.0, 0.0],
        [0.0, 0.0, sz, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ]

def perspective_projection_matrix(fov_angle, aspect, near, far):
    """원근 투영 행렬"""
    f = 1.0 / math.tan(math.radians(fov_angle / 2))
    return [
        [f / aspect, 0.0, 0.0, 0.0],
        [0.0, f, 0.0, 0.0],
        [0.0, 0.0, (far + near) / (near - far), (2 * far * near) / (near - far)],
        [0.0, 0.0, -1.0, 0.0]
    ]

# --- OBJ 파일 로더 ---
def load_obj(filename):
    """OBJ 파일에서 정점과 면 데이터를 로드 (주석 처리 개선)"""
    vertices = []
    faces = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.split('#')[0].strip()
                if not line:
                    continue

                parts = line.split()
                if not parts:
                    continue

                if parts[0] == 'v':
                    vertices.append([float(parts[1]), float(parts[2]), float(parts[3]), 1.0])
                elif parts[0] == 'f':
                    face_indices = []
                    # OBJ 파일의 면 정의는 1-based index이므로 -1 해줌
                    # p.split('/')[0]은 정점 인덱스만 사용 (텍스처, 노멀 무시)
                    for p in parts[1:]:
                        face_indices.append(int(p.split('/')[0]) - 1)
                    # 면을 선으로 그리기 위해, 각 면의 모든 에지를 추가
                    # 예: f 1 2 3 -> (1,2), (2,3), (3,1)
                    for i in range(len(face_indices)):
                        faces.append([face_indices[i], face_indices[(i + 1) % len(face_indices)]])
        print(f"'{filename}' 파일 로드 성공: 정점 {len(vertices)}개, 면(선) {len(faces)}개")
        return vertices, faces
    except FileNotFoundError:
        print(f"오류: '{filename}' 파일을 찾을 수 없습니다. 파일 경로와 이름을 확인해주세요.")
        print(f"현재 작업 디렉토리: {os.getcwd()}")
        return [], []
    except Exception as e:
        print(f"OBJ 파일 파싱 중 오류 발생: {e}")
        return [], []

# --- Pygame 초기화 ---
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame 3D Hexagonal Room with Cuboid and Cube (First-Person)")

# 마우스 커서 숨기기 및 창에 고정
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# 폰트 초기화 (FPS 표시용)
font = pygame.font.Font(None, 36) # 기본 폰트, 크기 36

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255) # 납작한 직육면체 색상
RED = (255, 0, 0)  # 작은 정육면체 색상
GREEN = (0, 255, 0) # 방 색상
YELLOW = (255, 255, 0) # OBJ 모델 색상

# --- 3D 모델 정의 (정육각형 방, 납작한 직육면체, 작은 정육면체) ---
room_vertices = []
room_faces = []

# --- 정육각형 방 정의 ---
room_radius = 10.0
room_height = 8.0
room_y_offset = -room_height / 2 # 방의 중심을 y=0으로 맞추기 위해, 바닥은 room_y_offset에 위치

# 방의 바닥 정점 (y_floor)
floor_start_index = len(room_vertices)
for i in range(6):
    angle = math.radians(60 * i)
    x = room_radius * math.cos(angle)
    z = room_radius * math.sin(angle)
    room_vertices.append([x, room_y_offset, z, 1.0])

# 방의 천장 정점 (y_ceiling)
ceiling_start_index = len(room_vertices)
for i in range(6):
    angle = math.radians(60 * i)
    x = room_radius * math.cos(angle)
    z = room_radius * math.sin(angle)
    room_vertices.append([x, room_y_offset + room_height, z, 1.0])

# 방의 면 정의 (와이어프레임)
# 바닥 (닫힌 루프)
for i in range(6):
    room_faces.append([floor_start_index + i, floor_start_index + (i + 1) % 6])
# 천장 (닫힌 루프)
for i in range(6):
    room_faces.append([ceiling_start_index + i, ceiling_start_index + (i + 1) % 6])
# 벽 (수직선)
for i in range(6):
    room_faces.append([floor_start_index + i, ceiling_start_index + i])


# --- 납작한 직육면체 정의 ---
cuboid_vertices = []
cuboid_faces = []
cuboid_width = 6.0
cuboid_depth = 4.0
cuboid_height = 0.5 # 납작한 높이
cuboid_base_y = room_y_offset # 방 바닥에 위치

cuboid_start_index = len(cuboid_vertices)
# 직육면체 정점 (8개)
# 바닥 (y = cuboid_base_y)
cuboid_vertices.append([-cuboid_width/2, cuboid_base_y, -cuboid_depth/2, 1.0]) # 0
cuboid_vertices.append([ cuboid_width/2, cuboid_base_y, -cuboid_depth/2, 1.0]) # 1
cuboid_vertices.append([ cuboid_width/2, cuboid_base_y,  cuboid_depth/2, 1.0]) # 2
cuboid_vertices.append([-cuboid_width/2, cuboid_base_y,  cuboid_depth/2, 1.0]) # 3
# 상단 (y = cuboid_base_y + cuboid_height)
cuboid_vertices.append([-cuboid_width/2, cuboid_base_y + cuboid_height, -cuboid_depth/2, 1.0]) # 4
cuboid_vertices.append([ cuboid_width/2, cuboid_base_y + cuboid_height, -cuboid_depth/2, 1.0]) # 5
cuboid_vertices.append([ cuboid_width/2, cuboid_base_y + cuboid_height,  cuboid_depth/2, 1.0]) # 6
cuboid_vertices.append([-cuboid_width/2, cuboid_base_y + cuboid_height,  cuboid_depth/2, 1.0]) # 7

# 직육면체 면 정의 (12개 선)
# 바닥
cuboid_faces.append([cuboid_start_index + 0, cuboid_start_index + 1])
cuboid_faces.append([cuboid_start_index + 1, cuboid_start_index + 2])
cuboid_faces.append([cuboid_start_index + 2, cuboid_start_index + 3])
cuboid_faces.append([cuboid_start_index + 3, cuboid_start_index + 0])
# 상단
cuboid_faces.append([cuboid_start_index + 4, cuboid_start_index + 5])
cuboid_faces.append([cuboid_start_index + 5, cuboid_start_index + 6])
cuboid_faces.append([cuboid_start_index + 6, cuboid_start_index + 7])
cuboid_faces.append([cuboid_start_index + 7, cuboid_start_index + 4])
# 옆면 (수직)
cuboid_faces.append([cuboid_start_index + 0, cuboid_start_index + 4])
cuboid_faces.append([cuboid_start_index + 1, cuboid_start_index + 5])
cuboid_faces.append([cuboid_start_index + 2, cuboid_start_index + 6])
cuboid_faces.append([cuboid_start_index + 3, cuboid_start_index + 7])


# --- 작은 정육면체 정의 ---
cube_vertices = []
cube_faces = []
cube_side = 1.5 # 직육면체보다 작게 설정
cube_base_y = cuboid_base_y + cuboid_height # 납작한 직육면체 위에 위치

cube_start_index = len(cube_vertices)
# 정육면체 정점 (8개)
# 바닥 (y = cube_base_y)
cube_vertices.append([-cube_side/2, cube_base_y, -cube_side/2, 1.0]) # 0
cube_vertices.append([ cube_side/2, cube_base_y, -cube_side/2, 1.0]) # 1
cube_vertices.append([ cube_side/2, cube_base_y,  cube_side/2, 1.0]) # 2
cube_vertices.append([-cube_side/2, cube_base_y,  cube_side/2, 1.0]) # 3
# 상단 (y = cube_base_y + cube_side)
cube_vertices.append([-cube_side/2, cube_base_y + cube_side, -cube_side/2, 1.0]) # 4
cube_vertices.append([ cube_side/2, cube_base_y + cube_side, -cube_side/2, 1.0]) # 5
cube_vertices.append([ cube_side/2, cube_base_y + cube_side,  cube_side/2, 1.0]) # 6
cube_vertices.append([-cube_side/2, cube_base_y + cube_side,  cube_side/2, 1.0]) # 7

# 정육면체 면 정의 (12개 선)
# 바닥
cube_faces.append([cube_start_index + 0, cube_start_index + 1])
cube_faces.append([cube_start_index + 1, cube_start_index + 2])
cube_faces.append([cube_start_index + 2, cube_start_index + 3])
cube_faces.append([cube_start_index + 3, cube_start_index + 0])
# 상단
cube_faces.append([cube_start_index + 4, cube_start_index + 5])
cube_faces.append([cube_start_index + 5, cube_start_index + 6])
cube_faces.append([cube_start_index + 6, cube_start_index + 7])
cube_faces.append([cube_start_index + 7, cube_start_index + 4])
# 옆면 (수직)
cube_faces.append([cube_start_index + 0, cube_start_index + 4])
cube_faces.append([cube_start_index + 1, cube_start_index + 5])
cube_faces.append([cube_start_index + 2, cube_start_index + 6])
cube_faces.append([cube_start_index + 3, cube_start_index + 7])


# --- OBJ 모델 로드 ---
obj_model_vertices, obj_model_faces = load_obj('Summer_Project/example.obj')
# OBJ 모델이 로드되지 않았다면 종료
if not obj_model_vertices:
    pygame.quit()
    exit()

# --- 3D 렌더링 설정 ---
# 플레이어(카메라) 초기 위치 및 점프 관련 변수
player_height = 1.7 # 플레이어의 눈높이
ground_level = room_y_offset + player_height # 플레이어가 서 있는 방 바닥의 Y 좌표 (눈높이 기준)

player_pos = [0.0, ground_level, -5.0] # 방 안에 들어갈 수 있도록 z값을 조정, y는 바닥에 맞춤
player_pitch = 0.0 # 상하 시선 (X축 회전)
player_yaw = 0.0   # 좌우 시선 (Y축 회전)

is_jumping = False
vertical_velocity = 0.0
jump_strength = 0.25 # 점프 높이 조절
gravity = 0.012 # 중력 조절

# 시야각(FOV) 설정
fov = 90.0 # 초기 시야각
fov_change_speed = 5.0 # 시야각 조절 속도
min_fov = 30.0 # 최소 시야각
max_fov = 120.0 # 최대 시야각

aspect_ratio = WIDTH / HEIGHT
near_plane = 0.1
far_plane = 100.0

# 초기 투영 행렬 계산
projection_matrix = perspective_projection_matrix(fov, aspect_ratio, near_plane, far_plane)

move_speed = 0.1 # 플레이어 이동 속도
mouse_sensitivity = 0.002 # 마우스 시선 조절 민감도

# OBJ 모델 회전 설정
obj_rotation_angle_y = 0.0
obj_rotation_speed = 0.1 # 회전 속도 조절
obj_scale_factor = 0.02 # OBJ 모델 크기 조절 (필요에 따라 조절)
# OBJ 모델의 중앙 위치 (정육면체 위에 배치)
obj_pos_y = cuboid_base_y + cuboid_height + cube_side + 0.5 # 정육면체 상단 + 약간 위

# --- 메인 게임 루프 ---
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.K_ESCAPE: # ESC 키로 종료
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: # 스페이스바를 눌러 점프
                if not is_jumping: # 땅에 있을 때만 점프 가능
                    is_jumping = True
                    vertical_velocity = jump_strength
            # --- 시야각 조절 ---
            if event.key == pygame.K_q: # FOV 감소 (줌 인)
                fov = max(min_fov, fov - fov_change_speed)
                projection_matrix = perspective_projection_matrix(fov, aspect_ratio, near_plane, far_plane)
            if event.key == pygame.K_e: # FOV 증가 (줌 아웃)
                fov = min(max_fov, fov + fov_change_speed)
                projection_matrix = perspective_projection_matrix(fov, aspect_ratio, near_plane, far_plane)

        if event.type == pygame.MOUSEMOTION:
            # 마우스 움직임에 따라 시선 조절
            dx, dy = event.rel # 상대적인 마우스 움직임
            
            # 마우스 좌우 시선: 마우스 오른쪽 이동 시 player_yaw 증가 (시선 오른쪽)
            player_yaw += dx * mouse_sensitivity
            # 마우스 상하 시선: 마우스를 위로 올리면 시선이 위로, 아래로 내리면 시선이 아래로
            # dy는 마우스를 위로 올리면 음수, 아래로 내리면 양수
            # player_pitch 증가하면 시선 위로, 감소하면 시선 아래로
            player_pitch -= dy * mouse_sensitivity 

            # pitch 값 제한 (위/아래를 너무 많이 보지 않도록)
            player_pitch = max(-math.pi / 2, min(math.pi / 2, player_pitch))
    
    # --- 키 입력 상태 확인 (키가 눌려있는 동안 계속 동작) ---
    keys = pygame.key.get_pressed()

    # 현재 시선 방향에 따른 이동 벡터 계산
    # Yaw는 Y축 회전이므로, XZ 평면에서의 방향을 결정합니다.
    forward_x = math.sin(player_yaw)
    forward_z = math.cos(player_yaw)
    
    # 오른쪽 방향 벡터 (forward 벡터를 90도 시계 방향으로 회전)
    right_x = math.cos(player_yaw)
    right_z = -math.sin(player_yaw)

    if keys[pygame.K_w]: # 앞으로 이동
        player_pos[0] += forward_x * move_speed
        player_pos[2] += forward_z * move_speed
    if keys[pygame.K_s]: # 뒤로 이동
        player_pos[0] -= forward_x * move_speed
        player_pos[2] -= forward_z * move_speed
    if keys[pygame.K_a]: # 왼쪽으로 이동 (스트레이프)
        player_pos[0] -= right_x * move_speed
        player_pos[2] -= right_z * move_speed
    if keys[pygame.K_d]: # 오른쪽으로 이동 (스트레이프)
        player_pos[0] += right_x * move_speed
        player_pos[2] += right_z * move_speed

    # --- 점프 및 중력 처리 ---
    if is_jumping:
        vertical_velocity -= gravity # 중력 적용
        player_pos[1] += vertical_velocity # 수직 위치 업데이트

        # 바닥에 닿았는지 확인
        if player_pos[1] <= ground_level:
            player_pos[1] = ground_level # 바닥에 고정
            vertical_velocity = 0.0 # 속도 초기화
            is_jumping = False # 점프 상태 해제

    screen.fill(BLACK)

    # 뷰 변환 행렬 (카메라의 역변환)
    view_matrix = multiply_matrices(rotate_x_matrix(-player_pitch), rotate_y_matrix(-player_yaw))
    view_matrix = multiply_matrices(view_matrix, translate_matrix(-player_pos[0], -player_pos[1], -player_pos[2]))

    # 최종 변환 행렬: 투영 * 뷰
    pv_matrix = multiply_matrices(projection_matrix, view_matrix)

    # --- 맵 요소 그리기 ---
    # 방 그리기
    transformed_room_vertices = []
    for v in room_vertices:
        transformed_v = multiply_matrix_vector(pv_matrix, v)
        if transformed_v[3] != 0 and transformed_v[2] / transformed_v[3] < far_plane and transformed_v[2] / transformed_v[3] > near_plane:
            x, y = transformed_v[0] / transformed_v[3], transformed_v[1] / transformed_v[3]
            transformed_room_vertices.append((int((x + 1) * WIDTH / 2), int((-y + 1) * HEIGHT / 2)))
        else:
            transformed_room_vertices.append(None)

    for idx1, idx2 in room_faces:
        if transformed_room_vertices[idx1] is not None and transformed_room_vertices[idx2] is not None:
            pygame.draw.line(screen, GREEN, transformed_room_vertices[idx1], transformed_room_vertices[idx2], 1)

    # 납작한 직육면체 그리기
    transformed_cuboid_vertices = []
    for v in cuboid_vertices:
        transformed_v = multiply_matrix_vector(pv_matrix, v)
        if transformed_v[3] != 0 and transformed_v[2] / transformed_v[3] < far_plane and transformed_v[2] / transformed_v[3] > near_plane:
            x, y = transformed_v[0] / transformed_v[3], transformed_v[1] / transformed_v[3]
            transformed_cuboid_vertices.append((int((x + 1) * WIDTH / 2), int((-y + 1) * HEIGHT / 2)))
        else:
            transformed_cuboid_vertices.append(None)

    for idx1, idx2 in cuboid_faces:
        if transformed_cuboid_vertices[idx1] is not None and transformed_cuboid_vertices[idx2] is not None:
            pygame.draw.line(screen, BLUE, transformed_cuboid_vertices[idx1], transformed_cuboid_vertices[idx2], 1)

    # 작은 정육면체 그리기
    transformed_cube_vertices = []
    for v in cube_vertices:
        transformed_v = multiply_matrix_vector(pv_matrix, v)
        if transformed_v[3] != 0 and transformed_v[2] / transformed_v[3] < far_plane and transformed_v[2] / transformed_v[3] > near_plane:
            x, y = transformed_v[0] / transformed_v[3], transformed_v[1] / transformed_v[3]
            transformed_cube_vertices.append((int((x + 1) * WIDTH / 2), int((-y + 1) * HEIGHT / 2)))
        else:
            transformed_cube_vertices.append(None)

    for idx1, idx2 in cube_faces:
        if transformed_cube_vertices[idx1] is not None and transformed_cube_vertices[idx2] is not None:
            pygame.draw.line(screen, RED, transformed_cube_vertices[idx1], transformed_cube_vertices[idx2], 1)

    # --- OBJ 모델 그리기 ---
    obj_rotation_angle_y += obj_rotation_speed # OBJ 모델 회전 각도 업데이트

    # OBJ 모델의 개별 변환 행렬
    obj_model_matrix = identity_matrix()
    obj_model_matrix = multiply_matrices(scale_matrix(obj_scale_factor, obj_scale_factor, obj_scale_factor), obj_model_matrix) # 크기 조정
    obj_model_matrix = multiply_matrices(rotate_y_matrix(obj_rotation_angle_y), obj_model_matrix) # 회전
    obj_model_matrix = multiply_matrices(translate_matrix(0, obj_pos_y, 0), obj_model_matrix) # 위치 이동 (중앙 상단)

    # 최종 OBJ 모델 변환 행렬: 투영 * 뷰 * OBJ_모델_행렬
    final_obj_transform_matrix = multiply_matrices(pv_matrix, obj_model_matrix)

    transformed_obj_vertices = []
    for v in obj_model_vertices:
        transformed_v = multiply_matrix_vector(final_obj_transform_matrix, v)
        if transformed_v[3] != 0 and transformed_v[2] / transformed_v[3] < far_plane and transformed_v[2] / transformed_v[3] > near_plane:
            x, y = transformed_v[0] / transformed_v[3], transformed_v[1] / transformed_v[3]
            transformed_obj_vertices.append((int((x + 1) * WIDTH / 2), int((-y + 1) * HEIGHT / 2)))
        else:
            transformed_obj_vertices.append(None)

    for idx1, idx2 in obj_model_faces:
        if transformed_obj_vertices[idx1] is not None and transformed_obj_vertices[idx2] is not None:
            pygame.draw.line(screen, YELLOW, transformed_obj_vertices[idx1], transformed_obj_vertices[idx2], 1)

    # --- FPS 표시 ---
    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(fps)}", True, WHITE) # 텍스트 렌더링 (안티-앨리어싱, 색상)
    screen.blit(fps_text, (10, 10)) # 화면 왼쪽 상단에 표시

    pygame.display.flip()
    clock.tick(60) # 초당 60프레임으로 제한하여 부드러운 움직임을 유지

pygame.quit()