import pygame
import math
import os
import random

# Pygame 초기화
pygame.init()
pygame.font.init()
pygame.mixer.init()

pygame.mouse.set_visible(False)

# -------------------------------
# 창 모드 (800 x 600)
# -------------------------------
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pygame 캐릭터와 총 제어")

current_dir = os.path.dirname(__file__)

# 사운드 로드
gun1_fire_sound_path = os.path.join(current_dir, "Asset", "Sound", "Gun1Fire.wav")
gun1_fire_sound = pygame.mixer.Sound(gun1_fire_sound_path)

walk_sound_path = os.path.join(current_dir, "Asset", "Sound", "ForestWalk.mp3")
walk_sound = pygame.mixer.Sound(walk_sound_path)
walk_sound.set_volume(0.5)

# 이미지 경로
player_image_path = os.path.join(current_dir, "Asset", "image", "MainCharacter.png")
gun_image_path_1 = os.path.join(current_dir, "Asset", "image", "Gun1.png")
gun_image_path_2 = os.path.join(current_dir, "Asset", "image", "Testgun2.png")
bullet_image_path = os.path.join(current_dir, "Asset", "image", "Bullet.png")
background_image_path = os.path.join(current_dir, "Asset", "image", "TestField.png")
cursor_image_path = os.path.join(current_dir, "Asset", "image", "MouseCursor.png")

# 이미지 로드
original_player_image = pygame.image.load(player_image_path).convert_alpha()
original_gun_image_1 = pygame.image.load(gun_image_path_1).convert_alpha()
original_gun_image_2 = pygame.image.load(gun_image_path_2).convert_alpha()
original_bullet_image = pygame.image.load(bullet_image_path).convert_alpha()
background_image = pygame.image.load(background_image_path).convert()
cursor_image = pygame.image.load(cursor_image_path).convert_alpha()

# TestField를 1600x1200으로 스케일
background_image = pygame.transform.scale(background_image, (1600, 1200))
background_rect = background_image.get_rect()

cursor_image = pygame.transform.scale(cursor_image, (32, 32))

player_size = 90
original_player_image = pygame.transform.scale(original_player_image, (player_size, player_size))

gun_width, gun_height = original_gun_image_1.get_size()
desired_gun_width = 30
scale_factor = desired_gun_width / gun_width
new_gun_size = (int(gun_width * scale_factor), int(gun_height * scale_factor))
original_gun_image_1 = pygame.transform.smoothscale(original_gun_image_1, new_gun_size)
original_gun_image_2 = pygame.transform.smoothscale(original_gun_image_2, new_gun_size)

original_gun_image_1 = pygame.transform.rotate(original_gun_image_1, 180)

bullet_size = (5, 10)
original_bullet_image = pygame.transform.scale(original_bullet_image, bullet_size)

debug_font = pygame.font.SysFont('malgungothic', 24)

world_x = 0
world_y = 0
world_vx = 0
world_vy = 0

acceleration_rate = 0.5
deceleration_rate = 0.7

move_left = False
move_right = False
move_up = False
move_down = False

normal_max_speed = 5.0
sprint_max_speed = 7.5
max_speed = normal_max_speed

allow_sprint = True

current_weapon = 1

bullets = []
scattered_bullets = []
last_shot_time = 0

mouse_left_button_down = False
mouse_right_button_down = False

player_rect = original_player_image.get_rect(center=(screen_width // 2, screen_height // 2))

gun_canvas_size = original_gun_image_1.get_size()
gun_canvas = pygame.Surface(gun_canvas_size, pygame.SRCALPHA)
gun_offset_x = 0
gun_offset_y = 0
gun_speed = 3

# 총 반동 관련 변수
recoil_offset = 0
recoil_velocity = 0

# 화면 흔들림 관련 변수
shake_offset_x = 0
shake_offset_y = 0
shake_timer = 0
shake_magnitude = 2

# 걷기 소리 관련 변수
walk_timer = 0
walk_delay = 500


class Bullet:
    def __init__(self, world_x, world_y, target_world_x, target_world_y, spread_angle_degrees, speed=15):
        scale_factor = 0.4
        new_size = (int(bullet_size[0] * 5 * scale_factor), int(bullet_size[1] * 5 * scale_factor))
        self.original_image = pygame.transform.scale(original_bullet_image, new_size)
        self.world_x = world_x
        self.world_y = world_y
        self.speed = speed
        self.trail = []

        angle_to_target = math.atan2(target_world_y - world_y, target_world_x - world_x)
        spread_radians = math.radians(random.uniform(-spread_angle_degrees / 2, spread_angle_degrees / 2))
        final_angle = angle_to_target + spread_radians

        self.vx = math.cos(final_angle) * speed
        self.vy = math.sin(final_angle) * speed
        self.angle_degrees = math.degrees(final_angle)

    def update(self):
        self.trail.append((self.world_x, self.world_y))
        if len(self.trail) > 30:
            self.trail.pop(0)
        self.world_x += self.vx
        self.world_y += self.vy

    def draw(self, screen, world_x, world_y):
        if len(self.trail) >= 2:
            points = []
            for tx, ty in self.trail:
                screen_x = tx - world_x
                screen_y = ty - world_y
                points.append((screen_x, screen_y))

            alpha_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

            for i in range(len(points) - 1):
                alpha = int(255 * ((i + 1) / len(points)))
                pygame.draw.line(
                    alpha_surface,
                    (255, 255, 255, alpha),
                    points[i],
                    points[i + 1],
                    width=9
                )

            screen.blit(alpha_surface, (0, 0))

        screen_x = self.world_x - world_x
        screen_y = self.world_y - world_y
        rotated_image = pygame.transform.rotate(self.original_image, -self.angle_degrees - 90)
        rect = rotated_image.get_rect(center=(screen_x, screen_y))
        screen.blit(rotated_image, rect)

    def is_offscreen(self, screen_width, screen_height, world_x, world_y):
        screen_x = self.world_x - world_x
        screen_y = self.world_y - world_y
        return (screen_x < -100 or screen_x > screen_width + 100 or screen_y < -100 or screen_y > screen_height + 100)


class ScatteredBullet:
    def __init__(self, x, y, vx, vy):
        self.image_original = original_bullet_image.copy()
        self.image_original = pygame.transform.scale(self.image_original, (3, 7))
        angle = math.degrees(math.atan2(vy, vx))
        self.image_original = pygame.transform.rotate(self.image_original, angle)
        self.image = self.image_original.copy()

        self.pos = [x, y]

        speed_scale = random.uniform(3, 8)
        self.vx = vx * speed_scale
        self.vy = vy * speed_scale

        self.friction = 0.85
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 5000
        self.fade_time = 1000
        self.alpha = 255

        self.rotation_angle = 0
        self.rotation_speed = random.uniform(5, 15) * random.choice([-1, 1])

    def update(self):
        self.pos[0] += self.vx
        self.pos[1] += self.vy
        self.vx *= self.friction
        self.vy *= self.friction

        self.rotation_angle += self.rotation_speed
        self.rotation_speed *= 0.85

        if abs(self.rotation_speed) < 0.05 and self.rotation_speed != 0:
            self.rotation_speed = 0 if random.random() < 0.5 else self.rotation_speed * -1

        self.image = pygame.transform.rotate(self.image_original, self.rotation_angle)

        elapsed = pygame.time.get_ticks() - self.spawn_time
        if elapsed > self.lifetime:
            fade_elapsed = elapsed - self.lifetime
            if fade_elapsed < self.fade_time:
                self.alpha = int(255 * (1 - fade_elapsed / self.fade_time))
                self.image.set_alpha(self.alpha)
            else:
                self.alpha = 0

    def draw(self, screen, world_x, world_y):
        if self.alpha > 0:
            screen_x = self.pos[0] - world_x
            screen_y = self.pos[1] - world_y
            rect = self.image.get_rect(center=(screen_x, screen_y))
            screen.blit(self.image, rect)


clock = pygame.time.Clock()
running = True

while running:
    current_time = pygame.time.get_ticks()

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
        if world_vx > 0:
            world_vx = max(0.0, world_vx - deceleration_rate)
        elif world_vx < 0:
            world_vx = min(0.0, world_vx + deceleration_rate)
    if not (move_up or move_down):
        if world_vy > 0:
            world_vy = max(0.0, world_vy - deceleration_rate)
        elif world_vy < 0:
            world_vy = min(0.0, world_vy + deceleration_rate)

    world_vx = max(-max_speed, min(max_speed, world_vx))
    world_vy = max(-max_speed, min(max_speed, world_vy))

    world_x += world_vx
    world_y += world_vy

    half_screen_width = screen_width // 2
    half_screen_height = screen_height // 2

    world_x = max(-half_screen_width, min(background_rect.width - half_screen_width, world_x))
    world_y = max(-half_screen_height, min(background_rect.height - half_screen_height, world_y))

    speed = math.sqrt(world_vx**2 + world_vy**2)

    if speed > 0:
        base_delay = max(400, int(500 / speed))
        if max_speed == sprint_max_speed:
            walk_delay = int(base_delay / 1.5)
        else:
            walk_delay = base_delay

        if current_time - walk_timer > walk_delay:
            walk_sound.play()
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
    distance_from_center = 40 + recoil_offset

    gun_pos_x = player_rect.centerx + direction_x * distance_from_center
    gun_pos_y = player_rect.centery + direction_y * distance_from_center
    rotated_gun_image = pygame.transform.rotate(current_gun_image, -angle_degrees + 90)
    rotated_gun_rect = rotated_gun_image.get_rect(center=(gun_pos_x, gun_pos_y))

    if current_weapon == 1 and mouse_left_button_down:
        if current_time - last_shot_time > 500:
            gun1_fire_sound.play()
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
                10
            )
            bullets.append(new_bullet)

            shake_timer = 10

            eject_angle = angle_radians + math.radians(90 + random.uniform(-15, 15))
            eject_speed = 1
            vx = math.cos(eject_angle) * eject_speed
            vy = math.sin(eject_angle) * eject_speed

            scatter_x = bullet_world_x
            scatter_y = bullet_world_y

            scattered_bullets.append(ScatteredBullet(scatter_x, scatter_y, vx, vy))

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
        if bullet.is_offscreen(screen_width, screen_height, world_x, world_y):
            bullets.remove(bullet)
        else:
            bullet.draw(screen, world_x - shake_offset_x, world_y - shake_offset_y)

    speed_text = f"Speed: {speed:.2f}"
    text_surface = debug_font.render(speed_text, True, (255, 255, 255))
    screen.blit(text_surface, (10, 10))

    weapon_text = f"Weapon: {current_weapon}"
    weapon_surface = debug_font.render(weapon_text, True, (255, 255, 255))
    screen.blit(weapon_surface, (10, 40))

    cursor_rect = cursor_image.get_rect(center=(mouse_x, mouse_y))
    screen.blit(cursor_image, cursor_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
