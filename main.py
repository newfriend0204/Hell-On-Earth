import pygame
import math
import random
from config import *
from asset_manager import load_images
from sound_manager import load_sounds
from entities import Bullet, ScatteredBullet
from renderer_3d import Renderer3D

pygame.init()
pygame.font.init()
pygame.mixer.init()

DEBUG_FONT = pygame.font.SysFont('malgungothic', 24)

pygame.mouse.set_visible(False)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame 캐릭터와 총 제어")

images = load_images()
sounds = load_sounds()

original_player_image = images["player"]
original_gun_image_1 = images["gun1"]
original_gun_image_2 = images["gun2"]
original_bullet_image = images["bullet"]
cursor_image = images["cursor"]
background_image = images["background"]
background_rect = background_image.get_rect()

player_rect = original_player_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

gun_canvas_size = original_gun_image_1.get_size()
gun_canvas = pygame.Surface(gun_canvas_size, pygame.SRCALPHA)
gun_offset_x = 0
gun_offset_y = 0
gun_speed = 3

world_x = 0
world_y = 0
world_vx = 0
world_vy = 0

acceleration_rate = 0.5
deceleration_rate = 0.7

move_left = move_right = move_up = move_down = False

normal_max_speed = NORMAL_MAX_SPEED
sprint_max_speed = SPRINT_MAX_SPEED
max_speed = normal_max_speed
allow_sprint = True

current_weapon = 1
bullets = []
scattered_bullets = []
last_shot_time = 0

mouse_left_button_down = False
mouse_right_button_down = False

recoil_offset = 0
recoil_velocity = 0

shake_offset_x = 0
shake_offset_y = 0
shake_timer = 0
shake_magnitude = 2

walk_timer = 0
walk_delay = 500

paused = False

renderer = Renderer3D(screen)

clock = pygame.time.Clock()
running = True

while running:
    current_time = pygame.time.get_ticks()

    events = pygame.event.get()

    for event in events:
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
            elif event.key == pygame.K_TAB:
                paused = not paused
                if paused:
                    pygame.mouse.set_visible(True)
                    renderer.reset_view()
                else:
                    pygame.mouse.set_visible(False)
            elif event.key == pygame.K_1:
                current_weapon = 1
            elif event.key == pygame.K_2:
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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_left_button_down = True
            elif event.button == 3:
                mouse_right_button_down = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_left_button_down = False
            elif event.button == 3:
                mouse_right_button_down = False

    if paused:
        renderer.handle_events(events)
        renderer.render_model(clock)
        clock.tick(60)
        continue

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        if allow_sprint:
            max_speed = sprint_max_speed
    else:
        max_speed = normal_max_speed

    if keys[pygame.K_UP]:
        gun_offset_y -= gun_speed
    if keys[pygame.K_DOWN]:
        gun_offset_y += gun_speed
    if keys[pygame.K_LEFT]:
        gun_offset_x -= gun_speed
    if keys[pygame.K_RIGHT]:
        gun_offset_x += gun_speed

    gun_offset_x = max(0, min(gun_canvas_size[0] - original_gun_image_1.get_width(), gun_offset_x))
    gun_offset_y = max(0, min(gun_canvas_size[1] - original_gun_image_1.get_height(), gun_offset_y))

    gun_canvas.fill((0, 0, 0, 0))
    gun_canvas.blit(original_gun_image_1, (gun_offset_x, gun_offset_y))

    if move_up:
        world_vy -= acceleration_rate
    if move_down:
        world_vy += acceleration_rate
    if move_left:
        world_vx -= acceleration_rate
    if move_right:
        world_vx += acceleration_rate

    if not (move_left or move_right):
        world_vx = math.copysign(max(0.0, abs(world_vx) - deceleration_rate), world_vx)
    if not (move_up or move_down):
        world_vy = math.copysign(max(0.0, abs(world_vy) - deceleration_rate), world_vy)

    world_vx = max(-max_speed, min(max_speed, world_vx))
    world_vy = max(-max_speed, min(max_speed, world_vy))

    world_x += world_vx
    world_y += world_vy

    half_screen_width = SCREEN_WIDTH // 2
    half_screen_height = SCREEN_HEIGHT // 2

    world_x = max(-half_screen_width, min(background_rect.width - half_screen_width, world_x))
    world_y = max(-half_screen_height, min(background_rect.height - half_screen_height, world_y))

    speed = math.sqrt(world_vx ** 2 + world_vy ** 2)

    if speed > 0:
        base_delay = max(400, int(500 / speed))
        if max_speed == sprint_max_speed:
            walk_delay = int(base_delay / 1.5)
        else:
            walk_delay = base_delay

        if current_time - walk_timer > walk_delay:
            sounds["walk"].play()
            walk_timer = current_time

    recoil_velocity += 1.5
    recoil_offset += recoil_velocity
    if recoil_offset > 0:
        recoil_offset = 0
        recoil_velocity = 0

    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x - player_rect.centerx
    dy = mouse_y - player_rect.centery
    angle_radians = math.atan2(dy, dx)
    angle_degrees = math.degrees(angle_radians)

    rotated_player_image = pygame.transform.rotate(original_player_image, -angle_degrees + 90)
    rotated_player_rect = rotated_player_image.get_rect(center=player_rect.center)

    current_gun_image = gun_canvas if current_weapon == 1 else original_gun_image_2

    direction_x = math.cos(angle_radians)
    direction_y = math.sin(angle_radians)
    distance_from_center = 50 + recoil_offset

    gun_pos_x = player_rect.centerx + direction_x * distance_from_center
    gun_pos_y = player_rect.centery + direction_y * distance_from_center
    rotated_gun_image = pygame.transform.rotate(current_gun_image, -angle_degrees + 90)
    rotated_gun_rect = rotated_gun_image.get_rect(center=(gun_pos_x, gun_pos_y))

    if current_weapon == 1 and mouse_left_button_down:
        if current_time - last_shot_time > 500:
            sounds["gun1_fire"].play()
            recoil_velocity = -7

            allow_sprint = False
            max_speed = normal_max_speed

            spawn_offset = 30
            bullet_world_x = world_x + player_rect.centerx + direction_x * spawn_offset
            bullet_world_y = world_y + player_rect.centery + direction_y * spawn_offset
            target_world_x = world_x + mouse_x
            target_world_y = world_y + mouse_y

            new_bullet = Bullet(
                bullet_world_x,
                bullet_world_y,
                target_world_x,
                target_world_y,
                10,
                original_bullet_image
            )
            bullets.append(new_bullet)

            shake_timer = 10

            eject_angle = angle_radians + math.radians(90 + random.uniform(-15, 15))
            eject_speed = 1
            vx = math.cos(eject_angle) * eject_speed
            vy = math.sin(eject_angle) * eject_speed

            scatter_x = bullet_world_x
            scatter_y = bullet_world_y

            scattered_bullets.append(ScatteredBullet(scatter_x, scatter_y, vx, vy, original_bullet_image))

            last_shot_time = current_time
    else:
        if recoil_offset == 0 and not mouse_left_button_down:
            allow_sprint = True
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                max_speed = sprint_max_speed
            else:
                max_speed = normal_max_speed

    if shake_timer > 0:
        shake_offset_x = random.randint(-shake_magnitude, shake_magnitude)
        shake_offset_y = random.randint(-shake_magnitude, shake_magnitude)
        shake_timer -= 1
    else:
        shake_offset_x = 0
        shake_offset_y = 0

    screen.fill((0, 0, 0))
    screen.blit(background_image, (-world_x + shake_offset_x, -world_y + shake_offset_y))

    for scatter in scattered_bullets[:]:
        scatter.update()
        if scatter.alpha <= 0:
            scattered_bullets.remove(scatter)
        else:
            scatter.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    screen.blit(rotated_gun_image, rotated_gun_rect.move(shake_offset_x, shake_offset_y))
    screen.blit(rotated_player_image, rotated_player_rect.move(shake_offset_x, shake_offset_y))

    for bullet in bullets[:]:
        bullet.update()
        if bullet.is_offscreen(SCREEN_WIDTH, SCREEN_HEIGHT, world_x, world_y):
            bullets.remove(bullet)
        else:
            bullet.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    speed_text = f"Speed: {speed:.2f}"
    text_surface = DEBUG_FONT.render(speed_text, True, (255, 255, 255))
    screen.blit(text_surface, (10, 10))

    weapon_text = f"Weapon: {current_weapon}"
    weapon_surface = DEBUG_FONT.render(weapon_text, True, (255, 255, 255))
    screen.blit(weapon_surface, (10, 40))

    cursor_rect = cursor_image.get_rect(center=(mouse_x, mouse_y))
    screen.blit(cursor_image, cursor_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
