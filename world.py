# world.py

import pygame
import math

class World:
    def __init__(self, background_image, crop_rect, PLAYER_VIEW_SCALE, BG_WIDTH, BG_HEIGHT):
        self.background_image = background_image
        self.PLAYER_VIEW_SCALE = PLAYER_VIEW_SCALE
        self.BG_WIDTH = BG_WIDTH
        self.BG_HEIGHT = BG_HEIGHT

        # crop_surface 생성
        self.crop_surface, self.effective_bg_width, self.effective_bg_height = \
            self.create_crop_surface(crop_rect)

        # tunnel surfaces
        self.horizontal_tunnel_surface = None
        self.vertical_tunnel_surface = None

    def create_crop_surface(self, crop_rect):
        if crop_rect:
            x_ratio = crop_rect.get("x_ratio", 1.0)
            y_ratio = crop_rect.get("y_ratio", 1.0)

            crop_width = int(self.BG_WIDTH * x_ratio)
            crop_height = int(self.BG_HEIGHT * y_ratio)

            if x_ratio <= 1.0 and y_ratio <= 1.0:
                crop_surface = self.background_image.subsurface(
                    pygame.Rect(0, 0, crop_width, crop_height)
                ).copy()
            else:
                crop_surface = pygame.Surface((crop_width, crop_height))
                for ty in range(math.ceil(y_ratio)):
                    for tx in range(math.ceil(x_ratio)):
                        crop_surface.blit(
                            self.background_image,
                            (tx * self.BG_WIDTH, ty * self.BG_HEIGHT)
                        )
            return crop_surface, crop_width, crop_height
        else:
            scaled = pygame.transform.smoothscale(
                self.background_image,
                (
                    int(self.background_image.get_width() * self.PLAYER_VIEW_SCALE),
                    int(self.background_image.get_height() * self.PLAYER_VIEW_SCALE)
                )
            )
            return scaled, scaled.get_width(), scaled.get_height()

    def generate_tunnels(self, hole_width, hole_height, left_wall_width, top_wall_height, tunnel_length):
        tile_width = self.background_image.get_width()
        tile_height = self.background_image.get_height()

        # horizontal
        horizontal_surface = pygame.Surface((tunnel_length, hole_height), pygame.SRCALPHA)
        tiles_needed = math.ceil(tunnel_length / tile_width)
        for i in range(tiles_needed):
            horizontal_surface.blit(
                self.background_image,
                (i * tile_width, 0),
                area=pygame.Rect(0, top_wall_height, tile_width, hole_height)
            )

        # vertical
        vertical_surface = pygame.Surface((hole_width, tunnel_length), pygame.SRCALPHA)
        tiles_needed = math.ceil(tunnel_length / tile_height)
        for i in range(tiles_needed):
            vertical_surface.blit(
                self.background_image,
                (0, i * tile_height),
                area=pygame.Rect(left_wall_width, 0, hole_width, tile_height)
            )

        self.horizontal_tunnel_surface = horizontal_surface
        self.vertical_tunnel_surface = vertical_surface

    def draw(self, screen, world_x, world_y, shake_offset_x, shake_offset_y,
             tunnel_length, hole_width, hole_height,
             left_wall_width, top_wall_height):
        
        # 중앙 기준 blit 좌표 계산
        center_x = (tunnel_length // 2) - (hole_width // 2)
        center_y = (tunnel_length // 2) - (hole_height // 2)

        if self.horizontal_tunnel_surface:
            screen.blit(
                self.horizontal_tunnel_surface,
                (
                    -center_x - world_x + shake_offset_x,
                    top_wall_height - world_y + shake_offset_y
                )
            )

        if self.vertical_tunnel_surface:
            screen.blit(
                self.vertical_tunnel_surface,
                (
                    left_wall_width - world_x + shake_offset_x,
                    -center_y - world_y + shake_offset_y
                )
            )

        screen.blit(
            self.crop_surface,
            (-world_x + shake_offset_x, -world_y + shake_offset_y)
        )
