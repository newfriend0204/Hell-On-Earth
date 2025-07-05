import pygame
import math
import random
from config import *
from asset_manager import load_images
from sound_manager import load_sounds
from entities import Bullet, ScatteredBullet
from renderer_3d import Renderer3D
from obstacle_manager import ObstacleManager

pygame.init()
pygame.font.init()
pygame.mixer.init()

DEBUG_FONT = pygame.font.SysFont('malgungothic', 24)

pygame.mouse.set_visible(False)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hell On Earth")

images = load_images()
sounds = load_sounds()

original_player_image = images["player"]
original_gun_image_1 = images["gun1"]
original_gun_image_2 = images["gun2"]
original_bullet_image = images["bullet"]
cursor_image = images["cursor"]
background_image = images["background"]
background_rect = background_image.get_rect()

obstacle_manager = ObstacleManager(
    obstacle_images=images["obstacles"],
    obstacle_masks=images["obstacle_masks"],
    map_width=BG_WIDTH,
    map_height=BG_HEIGHT,
    min_scale=1.3,
    max_scale=2.0
)

world_x = (BG_WIDTH // 2) - (SCREEN_WIDTH // 2)
world_y = max(0, BG_HEIGHT - (SCREEN_HEIGHT // 2))

player_rect = original_player_image.get_rect(
    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
)

gun_canvas_size = original_gun_image_1.get_size()
gun_canvas = pygame.Surface(gun_canvas_size, pygame.SRCALPHA)

world_vx = 0
world_vy = 0

acceleration_rate = 0.5
deceleration_rate = 0.7

move_left = move_right = move_up = move_down = False

normal_max_speed = NORMAL_MAX_SPEED
sprint_max_speed = SPRINT_MAX_SPEED
max_speed = normal_max_speed
allow_sprint = True
recoil_in_progress = False

changing_weapon = False
change_weapon_target = None
change_animation_time = 0.25
change_animation_timer = 0.0
previous_distance = 0
target_distance = 0
current_distance = 0

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
fade_in_after_resume = False

renderer = Renderer3D(screen)

clock = pygame.time.Clock()
running = True

player_radius = 30

def fade_out(screen, duration, step_delay):
    overlay = pygame.Surface(screen.get_size())
    overlay.fill((0, 0, 0))
    steps = int(duration / step_delay)
    clock = pygame.time.Clock()
    for i in range(steps + 1):
        alpha = int(255 * (i / steps))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(1/step_delay)

def fade_in(screen, duration, step_delay):
    overlay = pygame.Surface(screen.get_size())
    overlay.fill((0, 0, 0))
    steps = int(duration / step_delay)
    clock = pygame.time.Clock()
    for i in range(steps + 1):
        alpha = int(255 * (1 - i / steps))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(1/step_delay)

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
                fade_out(screen, duration=0.3, step_delay=0.01)
                paused = not paused
                if paused:
                    pygame.mouse.set_visible(True)
                    obj_file = "Gun13DObject.obj" if current_weapon == 1 else "Gun23DObject.obj"
                    zoom = GUN1_ZOOM_LEVEL if current_weapon == 1 else GUN2_ZOOM_LEVEL
                    renderer.load_new_obj(obj_file, zoom_level=zoom)
                    renderer.reset_view()
                    fade_in(screen, duration=0.3, step_delay=0.01)
                else:
                    pygame.mouse.set_visible(False)
                    fade_in_after_resume = True
            elif event.key == pygame.K_1:
                if current_weapon != 1 and not changing_weapon:
                    changing_weapon = True
                    change_weapon_target = 1
                    change_animation_timer = 0.0
                    previous_distance = current_distance
                    target_distance = GUN1_DISTANCE_FROM_CENTER
            elif event.key == pygame.K_2:
                if current_weapon != 2 and not changing_weapon:
                    changing_weapon = True
                    change_weapon_target = 2
                    change_animation_timer = 0.0
                    previous_distance = current_distance
                    target_distance = GUN2_DISTANCE_FROM_CENTER
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
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_left_button_down = False

    if paused:
        renderer.handle_events(events)
        renderer.render_model(clock)
        clock.tick(60)
        continue

    if fade_in_after_resume:
        screen.fill((0, 0, 0))
        pygame.display.flip()
        fade_in(screen, duration=0.3, step_delay=0.01)
        fade_in_after_resume = False

    prev_world_x = world_x
    prev_world_y = world_y

    if current_weapon == 1:
        distance_from_center = GUN1_DISTANCE_FROM_CENTER
    else:
        distance_from_center = GUN2_DISTANCE_FROM_CENTER

    if changing_weapon:
        change_animation_timer += clock.get_time() / 1000.0
        t = min(change_animation_timer / change_animation_time, 1.0)
        if t < 0.5:
            current_distance = (1.0 - (t / 0.5)) * previous_distance
        else:
            if current_weapon != change_weapon_target:
                current_weapon = change_weapon_target
            current_distance = ((t - 0.5) / 0.5) * target_distance
        if t >= 1.0:
            changing_weapon = False
            current_distance = target_distance
    else:
        current_distance = distance_from_center

    keys = pygame.key.get_pressed()

    if recoil_in_progress or mouse_left_button_down:
        max_speed = normal_max_speed
    else:
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            if allow_sprint:
                max_speed = sprint_max_speed
        else:
            max_speed = normal_max_speed

    if current_weapon == 1:
        max_speed *= (1 - GUN1_SPEED_PENALTY)
    elif current_weapon == 2:
        max_speed *= (1 - GUN2_SPEED_PENALTY)

    if move_left:
        world_vx -= acceleration_rate
    elif move_right:
        world_vx += acceleration_rate
    else:
        if world_vx > 0:
            world_vx = max(0.0, world_vx - deceleration_rate)
        elif world_vx < 0:
            world_vx = min(0.0, world_vx + deceleration_rate)

    if move_up:
        world_vy -= acceleration_rate
    elif move_down:
        world_vy += acceleration_rate
    else:
        if world_vy > 0:
            world_vy = max(0.0, world_vy - deceleration_rate)
        elif world_vy < 0:
            world_vy = min(0.0, world_vy + deceleration_rate)

    world_vx = max(-max_speed, min(max_speed, world_vx))
    world_vy = max(-max_speed, min(max_speed, world_vy))

    # ------------------------------
    # 축별 이동 충돌 검사
    # ------------------------------

    # X축
    test_world_x = world_x + world_vx
    test_world_y = world_y

    player_center_world_x = test_world_x + player_rect.centerx
    player_center_world_y = test_world_y + player_rect.centery

    if not obstacle_manager.check_collision_circle(
        (player_center_world_x, player_center_world_y),
        player_radius
    ):
        world_x = test_world_x
    else:
        world_vx = 0

    # Y축
    test_world_x = world_x
    test_world_y = world_y + world_vy

    player_center_world_x = test_world_x + player_rect.centerx
    player_center_world_y = test_world_y + player_rect.centery

    if not obstacle_manager.check_collision_circle(
        (player_center_world_x, player_center_world_y),
        player_radius
    ):
        world_y = test_world_y
    else:
        world_vy = 0

    half_screen_width = SCREEN_WIDTH // 2
    half_screen_height = SCREEN_HEIGHT // 2

    world_x = max(-half_screen_width, min(background_rect.width - half_screen_width, world_x))
    world_y = max(-half_screen_height, min(background_rect.height - half_screen_height, world_y))

    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x - player_rect.centerx
    dy = mouse_y - player_rect.centery
    angle_radians = math.atan2(dy, dx)
    angle_degrees = math.degrees(angle_radians)

    rotated_player_image = pygame.transform.rotate(original_player_image, -angle_degrees + 90)
    rotated_player_rect = rotated_player_image.get_rect(center=player_rect.center)

    current_gun_image = original_gun_image_1 if current_weapon == 1 else original_gun_image_2

    gun_pos_x = player_rect.centerx + math.cos(angle_radians) * (current_distance + recoil_offset)
    gun_pos_y = player_rect.centery + math.sin(angle_radians) * (current_distance + recoil_offset)
    rotated_gun_image = pygame.transform.rotate(current_gun_image, -angle_degrees + 90)
    rotated_gun_rect = rotated_gun_image.get_rect(center=(gun_pos_x, gun_pos_y))

    if current_weapon == 1:
        fire_delay = GUN1_FIRE_DELAY
        recoil_strength = GUN1_RECOIL
        fire_sound = sounds["gun1_fire"]
    elif current_weapon == 2:
        fire_delay = GUN2_FIRE_DELAY
        recoil_strength = GUN2_RECOIL
        fire_sound = sounds["gun2_fire"]

    if mouse_left_button_down:
        if current_time - last_shot_time > fire_delay:
            fire_sound.play()

            recoil_offset = 0
            recoil_velocity = -recoil_strength

            allow_sprint = False
            recoil_in_progress = True

            if current_weapon == 1:
                shake_magnitude = 2
            elif current_weapon == 2:
                shake_magnitude = 4

            direction_x = math.cos(angle_radians)
            direction_y = math.sin(angle_radians)

            spawn_offset = 30
            vertical_offset = 6
            offset_angle = angle_radians + math.radians(90)
            offset_dx = math.cos(offset_angle) * vertical_offset
            offset_dy = math.sin(offset_angle) * vertical_offset

            bullet_world_x = world_x + player_rect.centerx + direction_x * spawn_offset + offset_dx
            bullet_world_y = world_y + player_rect.centery + direction_y * spawn_offset + offset_dy
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

    recoil_velocity += 1.5
    recoil_offset += recoil_velocity
    if recoil_offset > 0:
        recoil_offset = 0
        recoil_velocity = 0
        recoil_in_progress = False
        allow_sprint = True

    if shake_timer > 0:
        shake_offset_x = random.randint(-shake_magnitude, shake_magnitude)
        shake_offset_y = random.randint(-shake_magnitude, shake_magnitude)
        shake_timer -= 1
    else:
        shake_offset_x = 0
        shake_offset_y = 0

    # --------------------
    # Draw 순서
    # --------------------

    screen.fill((0, 0, 0))
    screen.blit(background_image, (-world_x + shake_offset_x, -world_y + shake_offset_y))

    obstacle_manager.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    for scatter in scattered_bullets[:]:
        scatter.update()
        if scatter.alpha <= 0:
            scattered_bullets.remove(scatter)
        else:
            scatter.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    for bullet in bullets[:]:
        bullet.update()
        if bullet.is_offscreen(SCREEN_WIDTH, SCREEN_HEIGHT, world_x, world_y):
            bullets.remove(bullet)
        else:
            bullet.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    screen.blit(rotated_player_image, rotated_player_rect.move(shake_offset_x, shake_offset_y))
    screen.blit(rotated_gun_image, rotated_gun_rect.move(shake_offset_x, shake_offset_y))

    # 플레이어 collider outline
    pygame.draw.circle(
        screen,
        (255, 0, 0),
        (player_rect.centerx + shake_offset_x,
         player_rect.centery + shake_offset_y),
        player_radius,
        2
    )

    speed = math.sqrt(world_vx ** 2 + world_vy ** 2)
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
