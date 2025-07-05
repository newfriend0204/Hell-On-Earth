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
    """X축 회전 행렬"""
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, c, -s, 0.0],
        [0.0, s, c, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ]

def rotate_y_matrix(angle):
    """Y축 회전 행렬"""
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        [c, 0.0, s, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-s, 0.0, c, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ]

def rotate_z_matrix(angle):
    """Z축 회전 행렬"""
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        [c, -s, 0.0, 0.0],
        [s, c, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
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

def perspective_projection_matrix(fov, aspect, near, far):
    """원근 투영 행렬"""
    f = 1.0 / math.tan(math.radians(fov / 2))
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
                    for p in parts[1:]:
                        face_indices.append(int(p.split('/')[0]) - 1)
                    faces.append(face_indices)
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
pygame.display.set_caption("Pygame Simple 3D Renderer")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# --- 3D 모델 로드 ---
# 'M18_Smoke_Grenade.obj' 파일로 변경하여 사용한다고 가정합니다.
vertices, faces = load_obj('Summer_Project/example.obj')

if not vertices:
    pygame.quit()
    exit()

# --- 3D 렌더링 설정 ---
# 카메라 위치 (Z축으로 뒤로 물러나 모델이 보이게)
# 줌 레벨로 관리하여 스크롤로 조정합니다.
zoom_level = -250 # 초기 줌 레벨 (이 값을 조절하여 초기 모델 크기 설정)
min_zoom = -500 # 최대 멀리 줌 아웃 (더 큰 음수 값)
max_zoom = -10 # 최대 가까이 줌 인 (0에 가까운 음수 값)
zoom_speed = 10 # 스크롤 한 번에 변하는 줌 속도

fov = 90
aspect_ratio = WIDTH / HEIGHT
near_plane = 0.1
far_plane = 1000.0 # far_plane을 더 크게 설정하여 멀리 있는 모델도 보이도록

projection_matrix = perspective_projection_matrix(fov, aspect_ratio, near_plane, far_plane)

rotation_angle_x = 0
rotation_angle_y = 0

# 마우스 드래그 및 관성 관련 변수
dragging = False
last_mouse_x, last_mouse_y = 0, 0
inertia_x_speed = 0.0
inertia_y_speed = 0.0
rotation_sensitivity = 0.005 # 마우스 움직임 대비 회전 민감도
friction = 0.92 # 관성 감쇠율 (1에 가까울수록 오래 움직임)

# --- 메인 게임 루프 ---
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: # ESC 키로 종료
                running = False
        
        # 마우스 버튼 누름 (드래그 시작 또는 줌)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # 마우스 왼쪽 버튼
                dragging = True
                last_mouse_x, last_mouse_y = event.pos
                inertia_x_speed = 0.0 # 드래그 시작 시 관성 초기화
                inertia_y_speed = 0.0
            elif event.button == 4: # 마우스 휠 위로 (줌 인)
                zoom_level = min(zoom_level + zoom_speed, max_zoom)
            elif event.button == 5: # 마우스 휠 아래로 (줌 아웃)
                zoom_level = max(zoom_level - zoom_speed, min_zoom)

        # 마우스 버튼 뗌 (드래그 종료)
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: # 마우스 왼쪽 버튼
                dragging = False
                # 관성 속도 계산 (마지막 움직임 속도 반영)
                # 이전에 MOUSEMOTION에서 계산된 dx, dy를 사용하거나,
                # 현재 마우스 위치와 마지막 위치 차이를 이용할 수 있습니다.
                # 여기서는 MOUSEMOTION에서 speed를 직접 업데이트하도록 합니다.
                pass # MOUSEMOTION에서 inertia_x_speed, inertia_y_speed를 업데이트하므로 여기서는 처리하지 않습니다.

        # 마우스 움직임 (드래그 중)
        if event.type == pygame.MOUSEMOTION:
            if dragging:
                current_mouse_x, current_mouse_y = event.pos
                dx = current_mouse_x - last_mouse_x
                dy = current_mouse_y - last_mouse_y

                rotation_angle_y += dx * rotation_sensitivity
                rotation_angle_x += dy * rotation_sensitivity

                # 드래그 중에도 관성 속도를 계속 업데이트하여 놓았을 때의 속도를 정확히 반영
                inertia_x_speed = dx * rotation_sensitivity
                inertia_y_speed = dy * rotation_sensitivity

                last_mouse_x, last_mouse_y = current_mouse_x, current_mouse_y

    # 관성 적용 (드래그 중이 아닐 때)
    if not dragging:
        if abs(inertia_x_speed) > 0.0001: # 아주 작은 값은 무시
            rotation_angle_y += inertia_x_speed
            inertia_x_speed *= friction # 마찰 적용
        else:
            inertia_x_speed = 0.0 # 멈춤

        if abs(inertia_y_speed) > 0.0001:
            rotation_angle_x += inertia_y_speed
            inertia_y_speed *= friction
        else:
            inertia_y_speed = 0.0

    screen.fill(BLACK)

    # 모델 변환 행렬 (회전 + 이동)
    model_matrix = identity_matrix()
    model_matrix = multiply_matrices(rotate_x_matrix(rotation_angle_x), model_matrix)
    model_matrix = multiply_matrices(rotate_y_matrix(rotation_angle_y), model_matrix)
    # 모델을 카메라 앞으로 이동시키는 역할 (초기 위치 조정)
    model_matrix = multiply_matrices(translate_matrix(0, 0, 3), model_matrix) 

    # 뷰 변환 행렬 (카메라를 원점으로 이동)
    # camera_pos[2] 대신 zoom_level을 사용합니다.
    view_matrix = translate_matrix(0, 0, -zoom_level) # 카메라 Z 위치를 zoom_level로 설정

    # 최종 변환 행렬: 투영 * 뷰 * 모델
    pv_matrix = multiply_matrices(projection_matrix, view_matrix)
    final_transform_matrix = multiply_matrices(pv_matrix, model_matrix)

    transformed_vertices = []
    for v in vertices:
        transformed_v = multiply_matrix_vector(final_transform_matrix, v)

        if transformed_v[3] != 0:
            x = transformed_v[0] / transformed_v[3]
            y = transformed_v[1] / transformed_v[3]

            screen_x = int((x + 1) * WIDTH / 2)
            screen_y = int((-y + 1) * HEIGHT / 2)

            transformed_vertices.append((screen_x, screen_y))
        else:
            transformed_vertices.append(None)

    # 면 그리기 (와이어프레임)
    for face in faces:
        points_to_draw = []
        for index in face:
            if 0 <= index < len(transformed_vertices) and transformed_vertices[index] is not None:
                points_to_draw.append(transformed_vertices[index])
            else:
                points_to_draw = []
                break
        
        if len(points_to_draw) >= 2:
            pygame.draw.lines(screen, BLUE, True, points_to_draw, 1)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()