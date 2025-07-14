import pygame
from config import SCREEN_HEIGHT, SCREEN_WIDTH
import math
from entities import Obstacle
from collider import Collider

class World:
    def __init__(
        self,
        background_image,
        crop_rect,
        PLAYER_VIEW_SCALE,
        BG_WIDTH,
        BG_HEIGHT,
        hole_width,
        hole_height,
        left_wall_width,
        top_wall_height,
        tunnel_length
    ):
        self.background_image = background_image
        self.PLAYER_VIEW_SCALE = PLAYER_VIEW_SCALE
        self.BG_WIDTH = BG_WIDTH
        self.BG_HEIGHT = BG_HEIGHT

        self.hole_width = hole_width
        self.hole_height = hole_height
        self.left_wall_width = left_wall_width
        self.top_wall_height = top_wall_height
        self.tunnel_length = tunnel_length

        self.crop_surface, self.effective_bg_width, self.effective_bg_height = \
            self.create_crop_surface(crop_rect)

        self.horizontal_tunnel_surface = self.create_horizontal_tunnel()
        self.vertical_tunnel_surface = self.create_vertical_tunnel()

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

    def create_horizontal_tunnel(self):
        tile_width = self.background_image.get_width()
        tunnel_surface = pygame.Surface((self.tunnel_length, self.hole_height), pygame.SRCALPHA)

        tiles_needed = math.ceil(self.tunnel_length / tile_width)
        for i in range(tiles_needed):
            tunnel_surface.blit(
                self.background_image,
                (i * tile_width, 0),
                area=pygame.Rect(0, self.top_wall_height, tile_width, self.hole_height)
            )
        return tunnel_surface

    def create_vertical_tunnel(self):
        tile_height = self.background_image.get_height()
        tunnel_surface = pygame.Surface((self.hole_width, self.tunnel_length), pygame.SRCALPHA)

        tiles_needed = math.ceil(self.tunnel_length / tile_height)
        for i in range(tiles_needed):
            tunnel_surface.blit(
                self.background_image,
                (0, i * tile_height),
                area=pygame.Rect(self.left_wall_width, 0, self.hole_width, tile_height)
            )
        return tunnel_surface

    def draw(self, screen, world_x, world_y, shake_offset_x, shake_offset_y):
        center_x = (self.tunnel_length // 2) - (self.hole_width // 2)
        center_y = (self.tunnel_length // 2) - (self.hole_height // 2)

        screen.blit(
            self.horizontal_tunnel_surface,
            (
                -center_x - world_x + shake_offset_x,
                self.top_wall_height - world_y + shake_offset_y
            )
        )

        screen.blit(
            self.vertical_tunnel_surface,
            (
                self.left_wall_width - world_x + shake_offset_x,
                -center_y - world_y + shake_offset_y
            )
        )

        screen.blit(
            self.crop_surface,
            (-world_x + shake_offset_x, -world_y + shake_offset_y)
        )

    def get_initial_position(self):
        return (
            (self.crop_surface.get_width() // 2) - (SCREEN_WIDTH // 2),
            (self.crop_surface.get_height() // 2) - (SCREEN_HEIGHT // 2)
        )
    
    def get_spawn_point(self, direction, margin=0):
        if direction == "north":
            x = self.effective_bg_width / 2
            y = -self.tunnel_length + self.PLAYER_VIEW_SCALE * 10 + margin
        elif direction == "south":
            x = self.effective_bg_width / 2
            y = self.effective_bg_height + self.PLAYER_VIEW_SCALE * 10 + margin
        elif direction == "west":
            x = -self.tunnel_length + self.PLAYER_VIEW_SCALE * 10 + margin
            y = self.effective_bg_height / 2
        elif direction == "east":
            x = self.effective_bg_width + self.PLAYER_VIEW_SCALE * 10 + margin
            y = self.effective_bg_height / 2
        else:
            x = self.effective_bg_width / 2
            y = self.effective_bg_height / 2
        return (x, y)

    def generate_walls(self, map_width, map_height, wall_thickness, 
                    hole_width, hole_height,
                    left_wall_width, right_wall_width, 
                    top_wall_height, bottom_wall_height,
                    north_hole_open, south_hole_open,
                    west_hole_open, east_hole_open,
                    expansion, invisible_wall_filename="invisible_wall", extra_wall_size=2000):

        walls = []
        extra_wall_size *= self.PLAYER_VIEW_SCALE

        def rect_obstacle(size, world_x, world_y):
            surface = pygame.Surface(size, pygame.SRCALPHA)
            collider = Collider(
                shape="rectangle",
                center=(size[0]/2, size[1]/2),
                size=size,
                bullet_passable=False
            )
            return Obstacle(
                surface,
                world_x=world_x,
                world_y=world_y,
                colliders=[collider],
                image_filename=invisible_wall_filename,
            )

        walls.append(rect_obstacle((left_wall_width, wall_thickness), 0, -wall_thickness))
        walls.append(rect_obstacle((right_wall_width, wall_thickness), map_width - right_wall_width, -wall_thickness))
        if not north_hole_open:
            walls.append(
                rect_obstacle(
                    (hole_width, wall_thickness + extra_wall_size),
                    left_wall_width,
                    -wall_thickness - extra_wall_size
                )
            )
        walls.append(rect_obstacle((left_wall_width, wall_thickness), 0, map_height))
        walls.append(rect_obstacle((right_wall_width, wall_thickness), map_width - right_wall_width, map_height))
        if not south_hole_open:
            walls.append(
                rect_obstacle(
                    (hole_width, wall_thickness + extra_wall_size),
                    left_wall_width,
                    map_height
                )
            )
        walls.append(rect_obstacle((wall_thickness, top_wall_height), -wall_thickness, 0))
        walls.append(rect_obstacle((wall_thickness, bottom_wall_height), -wall_thickness, map_height - bottom_wall_height))
        if not west_hole_open:
            walls.append(
                rect_obstacle(
                    (wall_thickness + extra_wall_size, hole_height),
                    -wall_thickness - extra_wall_size,
                    top_wall_height
                )
            )
        walls.append(rect_obstacle((wall_thickness, top_wall_height), map_width, 0))
        walls.append(rect_obstacle((wall_thickness, bottom_wall_height), map_width, map_height - bottom_wall_height))
        if not east_hole_open:
            walls.append(
                rect_obstacle(
                    (wall_thickness + extra_wall_size, hole_height),
                    map_width,
                    top_wall_height
                )
            )

        walls.append(rect_obstacle((left_wall_width, expansion), 0, -wall_thickness - expansion))
        walls.append(rect_obstacle((right_wall_width, expansion), map_width - right_wall_width, -wall_thickness - expansion))
        walls.append(rect_obstacle((left_wall_width, expansion), 0, map_height + wall_thickness))
        walls.append(rect_obstacle((right_wall_width, expansion), map_width - right_wall_width, map_height + wall_thickness))
        walls.append(rect_obstacle((expansion, top_wall_height), -wall_thickness - expansion, 0))
        walls.append(rect_obstacle((expansion, bottom_wall_height), -wall_thickness - expansion, map_height - bottom_wall_height))
        walls.append(rect_obstacle((expansion, top_wall_height), map_width + wall_thickness, 0))
        walls.append(rect_obstacle((expansion, bottom_wall_height), map_width + wall_thickness, map_height - bottom_wall_height))

        return walls