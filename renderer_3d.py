import pygame
import math
import os
import time
from config import *
from math_utils import *
from obj_loader import load_obj

class Renderer3D:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()

        self.vertices, self.faces = load_obj(OBJ_PATHS[1])

        self.zoom_level = -1.0
        self.min_zoom = -10.0
        self.max_zoom = -0.5

        self.rotation_angle_x = math.radians(180)
        self.rotation_angle_y = math.radians(180)

        self.target_angle_x = math.radians(180)
        self.target_angle_y = math.radians(180)

        self.slow_rotation_speed = 0.2

        self.dragging = False
        self.last_mouse_pos = (0, 0)
        self.last_drag_time = time.time()

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

        self.zoom_ratio = 0.10

    def load_new_obj(self, obj_filename, zoom_level=None):
        obj_path = os.path.join(ASSET_DIR, "3DObject", obj_filename)
        self.vertices, self.faces = load_obj(obj_path)

        # 무기별 zoom limit 및 zoom_ratio 설정
        if obj_filename == "Gun13DObject.obj":
            self.min_zoom = GUN1_MIN_ZOOM
            self.max_zoom = GUN1_MAX_ZOOM
            self.zoom_ratio = GUN1_ZOOM_RATIO
        elif obj_filename == "Gun23DObject.obj":
            self.min_zoom = GUN2_MIN_ZOOM
            self.max_zoom = GUN2_MAX_ZOOM
            self.zoom_ratio = GUN2_ZOOM_RATIO
        elif obj_filename == "Gun33DObject.obj":    # ✅ gun3 추가
            self.min_zoom = GUN3_MIN_ZOOM
            self.max_zoom = GUN3_MAX_ZOOM
            self.zoom_ratio = GUN3_ZOOM_RATIO

        if zoom_level is not None:
            self.zoom_level = zoom_level
            if self.zoom_level < self.min_zoom:
                self.zoom_level = self.min_zoom
            if self.zoom_level > self.max_zoom:
                self.zoom_level = self.max_zoom

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.dragging = True
                    self.last_mouse_pos = event.pos
                    self.inertia_x_speed = 0.0
                    self.inertia_y_speed = 0.0
                    self.last_drag_time = time.time()
                elif event.button == 4 or event.button == 5:
                    zoom_range = self.max_zoom - self.min_zoom
                    zoom_step = zoom_range * self.zoom_ratio

                    if event.button == 4:
                        self.zoom_level = min(self.zoom_level + zoom_step, self.max_zoom)
                    elif event.button == 5:
                        self.zoom_level = max(self.zoom_level - zoom_step, self.min_zoom)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    current_mouse_pos = event.pos
                    dx = current_mouse_pos[0] - self.last_mouse_pos[0]
                    dy = current_mouse_pos[1] - self.last_mouse_pos[1]

                    dy = -dy   # ← 모든 무기에 대해 y 반전

                    self.rotation_angle_y += dx * 0.005
                    self.rotation_angle_x -= dy * 0.005

                    self.inertia_x_speed = dx * 0.005
                    self.inertia_y_speed = -dy * 0.005

                    self.last_mouse_pos = current_mouse_pos
                    self.last_drag_time = time.time()

    def render_model(self, clock):
        current_time = time.time()

        if not self.vertices or not self.faces:
            self.screen.fill((0, 0, 0))
            text = self.font.render("No 3D Model Loaded", True, (255, 255, 255))
            self.screen.blit(text, (50, 50))
            pygame.display.flip()
            return

        if not self.dragging:
            if (current_time - self.last_drag_time) > 2.0:
                self.rotation_angle_x += (self.target_angle_x - self.rotation_angle_x) * 0.02
                self.rotation_angle_y += (self.target_angle_y - self.rotation_angle_y) * 0.02
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
                if (
                    0 <= index < len(transformed_vertices)
                    and transformed_vertices[index] is not None
                ):
                    points.append(transformed_vertices[index])
            if len(points) >= 2:
                pygame.draw.lines(self.screen, (0, 0, 255), True, points, 1)

        fps_text = self.font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
        zoom_text = self.font.render(f"Zoom: {self.zoom_level:.2f}", True, (255, 255, 255))

        self.screen.blit(fps_text, (10, 10))
        self.screen.blit(zoom_text, (10, 40))

        pygame.display.flip()

    def reset_view(self):
        self.rotation_angle_x = math.radians(180)
        self.rotation_angle_y = math.radians(180)
        self.inertia_x_speed = 0.0
        self.inertia_y_speed = 0.0
        self.last_drag_time = time.time()
