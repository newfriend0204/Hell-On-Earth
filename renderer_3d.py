import pygame
import math
import os
import time
from config import OBJ_PATH

def multiply_matrix_vector(matrix, vector):
    result = [0, 0, 0, 0]
    for i in range(4):
        for j in range(4):
            result[i] += matrix[i][j] * vector[j]
    return result

def multiply_matrices(matrix1, matrix2):
    result_matrix = [[0.0 for _ in range(4)] for _ in range(4)]
    for i in range(4):
        for j in range(4):
            for k in range(4):
                result_matrix[i][j] += matrix1[i][k] * matrix2[k][j]
    return result_matrix

def identity_matrix():
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ]

def rotate_x_matrix(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, c, -s, 0.0],
        [0.0, s, c, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ]

def rotate_y_matrix(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        [c, 0.0, s, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-s, 0.0, c, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ]

def translate_matrix(dx, dy, dz):
    return [
        [1.0, 0.0, 0.0, dx],
        [0.0, 1.0, 0.0, dy],
        [0.0, 0.0, 1.0, dz],
        [0.0, 0.0, 0.0, 1.0]
    ]

def perspective_projection_matrix(fov, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov / 2))
    return [
        [f / aspect, 0.0, 0.0, 0.0],
        [0.0, f, 0.0, 0.0],
        [0.0, 0.0, (far + near) / (near - far), (2 * far * near) / (near - far)],
        [0.0, 0.0, -1.0, 0.0]
    ]

def load_obj(filename):
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
        print(f"OBJ 파일을 찾을 수 없습니다: {filename}")
        return [], []
    except Exception as e:
        print(f"OBJ 파싱 중 오류: {e}")
        return [], []

class Renderer3D:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()

        self.vertices, self.faces = load_obj(OBJ_PATH)

        self.zoom_level = -0.01
        self.min_zoom = -5.0
        self.max_zoom = -0.01
        self.zoom_speed = 1

        self.rotation_angle_x = math.radians(180)
        self.rotation_angle_y = math.radians(180)

        self.target_angle_x = math.radians(180)
        self.target_angle_y = math.radians(180)

        self.slow_rotation_speed = 0.2

        self.dragging = False
        self.last_mouse_pos = (0, 0)
        self.last_drag_time = 0.0

        self.inertia_x_speed = 0.0
        self.inertia_y_speed = 0.0
        self.friction = 0.9

        self.projection_matrix = perspective_projection_matrix(
            90,
            self.width / self.height,
            0.01,
            1000.0
        )

        self.font = pygame.font.SysFont('malgungothic', 24)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.dragging = True
                    self.last_mouse_pos = event.pos
                    self.inertia_x_speed = 0.0
                    self.inertia_y_speed = 0.0
                    self.last_drag_time = time.time()
                elif event.button == 4:
                    self.zoom_level = min(self.zoom_level + self.zoom_speed, self.max_zoom)
                elif event.button == 5:
                    self.zoom_level = max(self.zoom_level - self.zoom_speed, self.min_zoom)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    current_mouse_pos = event.pos
                    dx = current_mouse_pos[0] - self.last_mouse_pos[0]
                    dy = current_mouse_pos[1] - self.last_mouse_pos[1]

                    self.rotation_angle_y += dx * 0.005
                    self.rotation_angle_x -= dy * 0.005

                    self.inertia_x_speed = dx * 0.005
                    self.inertia_y_speed = -dy * 0.005

                    self.last_mouse_pos = current_mouse_pos
                    self.last_drag_time = time.time()

    def render_model(self, clock):
        current_time = time.time()

        if not self.dragging:
            if (current_time - self.last_drag_time) > 2.0:
                self.rotation_angle_x += (self.target_angle_x - self.rotation_angle_x) * 0.02
                self.rotation_angle_y += (self.target_angle_y - self.rotation_angle_y) * 0.02

                # 자동 회전은 이때만 적용
                self.rotation_angle_y += self.slow_rotation_speed
            else:
                self.rotation_angle_x += self.inertia_y_speed
                self.rotation_angle_y += self.inertia_x_speed

                self.inertia_x_speed *= self.friction
                self.inertia_y_speed *= self.friction

        model_matrix = identity_matrix()
        model_matrix = multiply_matrices(rotate_x_matrix(self.rotation_angle_x), model_matrix)
        model_matrix = multiply_matrices(rotate_y_matrix(self.rotation_angle_y), model_matrix)
        model_matrix = multiply_matrices(translate_matrix(0, 0, 3), model_matrix)

        view_matrix = translate_matrix(0, 0, -self.zoom_level)
        pv_matrix = multiply_matrices(self.projection_matrix, view_matrix)
        final_transform = multiply_matrices(pv_matrix, model_matrix)

        transformed_vertices = []
        for v in self.vertices:
            tv = multiply_matrix_vector(final_transform, v)
            if tv[3] != 0:
                x = tv[0] / tv[3]
                y = tv[1] / tv[3]
                screen_x = int((x + 1) * self.width / 2)
                screen_y = int((-y + 1) * self.height / 2)
                transformed_vertices.append((screen_x, screen_y))
            else:
                transformed_vertices.append(None)

        self.screen.fill((0, 0, 0))

        for face in self.faces:
            points = []
            for index in face:
                if 0 <= index < len(transformed_vertices) and transformed_vertices[index]:
                    points.append(transformed_vertices[index])
                else:
                    points = []
                    break
            if len(points) >= 2:
                pygame.draw.lines(self.screen, (0, 0, 255), True, points, 1)

        fps_text = self.font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
        self.screen.blit(fps_text, (10, 10))

        pygame.display.flip()

    def reset_view(self):
        self.zoom_level = -0.01
        self.rotation_angle_x = math.radians(180)
        self.rotation_angle_y = math.radians(180)
        self.inertia_x_speed = 0.0
        self.inertia_y_speed = 0.0
        self.last_drag_time = 0.0  # ← 핵심!
