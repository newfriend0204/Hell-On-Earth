import pygame
import math
import random
from config import *
from asset_manager import load_images
from sound_manager import load_sounds
from entities import Bullet, ScatteredBullet, ScatteredBlood
from renderer_3d import Renderer3D
from obstacle_manager import ObstacleManager
from ai import Enemy

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
    max_scale=2.0,
    num_obstacles_range=(5, 8)
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

player_hp = 300
player_hp_max = 300

damage_flash_alpha = 0
damage_flash_fade_speed = 5

blood_effects = []

kill_count = 0

def increment_kill_count():
    global kill_count
    kill_count += 1

# ✅ 함수 선언을 Enemy 생성보다 위로 올림
def check_circle_collision(center1, radius1, center2, radius2):
    dx = center1[0] - center2[0]
    dy = center1[1] - center2[1]
    dist_sq = dx * dx + dy * dy
    r_sum = radius1 + radius2
    return dist_sq <= r_sum * r_sum

def check_ellipse_circle_collision(circle_center, circle_radius, ellipse_center, rx, ry):
    dx = circle_center[0] - ellipse_center[0]
    dy = circle_center[1] - ellipse_center[1]
    test = (dx ** 2) / ((rx + circle_radius) ** 2) + \
           (dy ** 2) / ((ry + circle_radius) ** 2)
    return test <= 1.0

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
        clock.tick(1 / step_delay)

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
        clock.tick(1 / step_delay)

def get_player_center_world(world_x, world_y):
    return (
        world_x + player_rect.centerx,
        world_y + player_rect.centery
    )

enemies = []
enemy_positions = [
    (BG_WIDTH // 2 - 100, 100),
    (BG_WIDTH // 2, 100),
    (BG_WIDTH // 2 + 100, 100),
    (BG_WIDTH // 2 - 100, 175),
    (BG_WIDTH // 2, 175),
    (BG_WIDTH // 2 + 100, 175),
    (BG_WIDTH // 2 - 100, 250),
    (BG_WIDTH // 2, 250),
    (BG_WIDTH // 2 + 100, 250),
]

for pos in enemy_positions:
    enemy = Enemy(
    world_x=pos[0],
    world_y=pos[1],
    image=images["enemy"],
    gun_image=images["gun1"],
    bullet_image=images["enemy_bullet"],
    sounds=sounds,
    get_player_center_world_fn=get_player_center_world,
    obstacle_manager=obstacle_manager,
    check_circle_collision_fn=check_circle_collision,
    check_ellipse_circle_collision_fn=check_ellipse_circle_collision,
    player_bullet_image=images["bullet"],
    kill_callback=increment_kill_count
    )
    enemies.append(enemy)

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

    delta_time = clock.get_time()
    player_center = (world_x + player_rect.centerx, world_y + player_rect.centery)
    for enemy in enemies:
        enemy.update(
            dt=delta_time,
            world_x=world_x,
            world_y=world_y,
            player_rect=player_rect,
            enemies=enemies
        )

     # 적의 탄환이 플레이어에 명중 시
    for enemy in enemies:
        for bullet in enemy.bullets[:]:
            bullet.update(obstacle_manager)
            if bullet.is_offscreen(SCREEN_WIDTH, SCREEN_HEIGHT, world_x, world_y):
                bullet.to_remove = True
                continue
            if check_circle_collision(
                bullet.collider.center,
                bullet.collider.size if isinstance(bullet.collider.size, (int, float)) else 5.0,
                player_center,
                player_radius
            ):
                player_hp -= 20
                damage_flash_alpha = 255
                shake_timer = 15      # 흔들리는 프레임 수 (조절 가능)
                shake_magnitude = 5   # 흔들림 세기 (조절 가능)
                bullet.to_remove = True
                continue

    # 탄피 업데이트 (탄피가 배경 위, 나머지 위로 오도록)
    for scatter in scattered_bullets[:]:
        scatter.update()
        if scatter.alpha <= 0:
            scattered_bullets.remove(scatter)

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

    # X축 충돌 검사
    test_world_x = world_x + world_vx
    test_world_y = world_y

    player_center_world_x = test_world_x + player_rect.centerx
    player_center_world_y = test_world_y + player_rect.centery

    player_hit = False

    for obs in obstacle_manager.placed_obstacles:
        for c in obs.colliders:
            collider_world_center = (
                obs.world_x + c.center[0],
                obs.world_y + c.center[1]
            )
            if c.shape == "circle":
                collider_radius = c.size
                if check_circle_collision(
                    (player_center_world_x, player_center_world_y),
                    player_radius,
                    collider_world_center,
                    collider_radius
                ):
                    player_hit = True
                    break
            elif c.shape == "ellipse":
                rx, ry = c.size
                if check_ellipse_circle_collision(
                    (player_center_world_x, player_center_world_y),
                    player_radius,
                    collider_world_center,
                    rx,
                    ry
                ):
                    player_hit = True
                    break
            elif c.shape == "rectangle":
                w, h = c.size
                collider_radius = math.sqrt((w/2)**2 + (h/2)**2)
                if check_circle_collision(
                    (player_center_world_x, player_center_world_y),
                    player_radius,
                    collider_world_center,
                    collider_radius
                ):
                    player_hit = True
                    break
        if player_hit:
            break

    if not player_hit:
        # 적과 충돌 검사
        collided_with_enemy = False
        player_center_world = (
            test_world_x + player_rect.centerx,
            world_y + player_rect.centery
        )
        for enemy in enemies:
            if check_circle_collision(
                player_center_world,
                player_radius,
                (enemy.world_x, enemy.world_y),
                enemy.radius
            ):
                collided_with_enemy = True
                break
        if not collided_with_enemy:
            world_x = test_world_x
        else:
            world_vx = 0
    else:
        world_vx = 0

    # Y축 충돌 검사
    test_world_x = world_x
    test_world_y = world_y + world_vy

    player_center_world_x = test_world_x + player_rect.centerx
    player_center_world_y = test_world_y + player_rect.centery

    player_hit = False

    for obs in obstacle_manager.placed_obstacles:
        for c in obs.colliders:
            collider_world_center = (
                obs.world_x + c.center[0],
                obs.world_y + c.center[1]
            )
            if c.shape == "circle":
                collider_radius = c.size
                if check_circle_collision(
                    (player_center_world_x, player_center_world_y),
                    player_radius,
                    collider_world_center,
                    collider_radius
                ):
                    player_hit = True
                    break
            elif c.shape == "ellipse":
                rx, ry = c.size
                if check_ellipse_circle_collision(
                    (player_center_world_x, player_center_world_y),
                    player_radius,
                    collider_world_center,
                    rx,
                    ry
                ):
                    player_hit = True
                    break
            elif c.shape == "rectangle":
                w, h = c.size
                collider_radius = math.sqrt((w/2)**2 + (h/2)**2)
                if check_circle_collision(
                    (player_center_world_x, player_center_world_y),
                    player_radius,
                    collider_world_center,
                    collider_radius
                ):
                    player_hit = True
                    break
        if player_hit:
            break

    if not player_hit:
        collided_with_enemy = False
        player_center_world = (
            world_x + player_rect.centerx,
            test_world_y + player_rect.centery
        )
        for enemy in enemies:
            if check_circle_collision(
                player_center_world,
                player_radius,
                (enemy.world_x, enemy.world_y),
                enemy.radius
            ):
                collided_with_enemy = True
                break
        if not collided_with_enemy:
            world_y = test_world_y
        else:
            world_vy = 0
    else:
        world_vy = 0
    
    # ✅ 추가: bullet 장애물 충돌 검사
    for bullet in bullets[:]:
        bullet.update(obstacle_manager)
        collided = False
        for obs in obstacle_manager.placed_obstacles:
            for c in obs.colliders:
                if c.bullet_passable:
                    continue
                if c.check_collision_circle(bullet.collider.center, bullet.collider.size):
                    collided = True
                    break
            if collided:
                break
        if collided:
            bullet.to_remove = True
            continue

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
    else:
        fire_delay = GUN2_FIRE_DELAY
        recoil_strength = GUN2_RECOIL
        fire_sound = sounds["gun2_fire"]

    if mouse_left_button_down and not changing_weapon:
        if current_time - last_shot_time > fire_delay:
            fire_sound.play()

            recoil_offset = 0
            recoil_velocity = -recoil_strength

            allow_sprint = False
            recoil_in_progress = True

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
                original_bullet_image,
                speed=10,
                max_distance=1500
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

    bullets = [b for b in bullets if not getattr(b, "to_remove", False)]
    enemy.bullets = [b for b in enemy.bullets if not getattr(b, "to_remove", False)]
    screen.fill((0, 0, 0))
    screen.blit(background_image, (-world_x + shake_offset_x, -world_y + shake_offset_y))

    for scatter in scattered_bullets[:]:
        scatter.update()
        if scatter.alpha <= 0:
            scattered_bullets.remove(scatter)
        else:
            scatter.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    for enemy in enemies:
        for scatter in enemy.scattered_bullets[:]:
            scatter.update()
            if scatter.alpha <= 0:
                enemy.scattered_bullets.remove(scatter)
            else:
                scatter.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    for blood in blood_effects[:]:
        blood.update()
        if blood.alpha <= 0:
            blood_effects.remove(blood)

    for blood in blood_effects:
        blood.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    obstacle_manager.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    for enemy in enemies:
        enemy.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    # ✅ 추가: HP 바 출력
    hp_bar_width = 300
    hp_bar_height = 30
    hp_bar_x = SCREEN_WIDTH // 2 - hp_bar_width // 2
    hp_bar_y = SCREEN_HEIGHT - 60
    hp_ratio = max(0, player_hp / player_hp_max)
    current_width = int(hp_bar_width * hp_ratio)
    pygame.draw.rect(screen, (80, 80, 80), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (hp_bar_x, hp_bar_y, current_width, hp_bar_height))
    hp_text = DEBUG_FONT.render(f"HP: {player_hp}", True, (255, 255, 255))
    screen.blit(hp_text, (hp_bar_x + hp_bar_width + 10, hp_bar_y))

    # ✅ 추가: damage flash effect
    if damage_flash_alpha > 0:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        border_thickness = 40

        for i in range(border_thickness):
            alpha = int(damage_flash_alpha * (1 - i / border_thickness))
            color = (255, 0, 0, alpha)

            # 위쪽
            overlay.fill(color, rect=(i, i, SCREEN_WIDTH - i * 2, 1))
            # 아래쪽
            overlay.fill(color, rect=(i, SCREEN_HEIGHT - i - 1, SCREEN_WIDTH - i * 2, 1))
            # 왼쪽
            overlay.fill(color, rect=(i, i, 1, SCREEN_HEIGHT - i * 2))
            # 오른쪽
            overlay.fill(color, rect=(SCREEN_WIDTH - i - 1, i, 1, SCREEN_HEIGHT - i * 2))

        screen.blit(overlay, (0, 0))
        damage_flash_alpha = max(0, damage_flash_alpha - damage_flash_fade_speed)


    for bullet in bullets[:]:
        bullet.update(obstacle_manager)
        if getattr(bullet, "to_remove", False):
            bullet.to_remove = True
            continue

        bullet_center_world = bullet.collider.center

        bullet_radius = 5.0  # 안전 기본값

        if bullet.collider:
            if bullet.collider.shape == "circle":
                if isinstance(bullet.collider.size, tuple):
                    bullet_radius = float(bullet.collider.size[0])
                else:
                    bullet_radius = float(bullet.collider.size)
            elif bullet.collider.shape == "ellipse":
                bullet_radius = float(max(bullet.collider.size))
            elif bullet.collider.shape == "rectangle":
                w, h = bullet.collider.size
                bullet_radius = max(math.sqrt((w / 2) ** 2 + (h / 2) ** 2), 5.0)

        hit = False
        for enemy in enemies[:]:
            enemy_center_world = (enemy.world_x, enemy.world_y)
            if check_circle_collision(
                bullet_center_world,
                bullet_radius,
                enemy_center_world,
                enemy.radius
            ):
                damage = 30 if current_weapon == 1 else 20
                enemy.hit(damage, blood_effects)
                if not enemy.alive:
                    enemies.remove(enemy)
                    blood_effects.append(
                        ScatteredBlood(enemy.world_x, enemy.world_y)
                    )
                bullet.to_remove = True
                break

        if hit:
            bullet.to_remove = True
            continue

        if bullet.is_offscreen(SCREEN_WIDTH, SCREEN_HEIGHT, world_x, world_y):
            bullet.to_remove = True
            continue

        bullet.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    screen.blit(rotated_gun_image, rotated_gun_rect.move(shake_offset_x, shake_offset_y))
    screen.blit(rotated_player_image, rotated_player_rect.move(shake_offset_x, shake_offset_y))

    speed = math.sqrt(world_vx ** 2 + world_vy ** 2)
    text_surface = DEBUG_FONT.render(f"Speed: {speed:.2f}", True, (255, 255, 255))
    screen.blit(text_surface, (10, 10))

    weapon_surface = DEBUG_FONT.render(f"Weapon: {current_weapon}", True, (255, 255, 255))
    screen.blit(weapon_surface, (10, 40))

    kill_surface = DEBUG_FONT.render(f"Kills: {kill_count}", True, (255, 255, 255))
    screen.blit(kill_surface, (10, 70))

    cursor_rect = cursor_image.get_rect(center=(mouse_x, mouse_y))
    screen.blit(cursor_image, cursor_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
