import pygame

pygame.init()

TAB_NAMES = ["내 상태", "무기1", "무기2", "무기3", "무기4"]

KOREAN_FONT_PATH = "Asset/Font/DungGeunMo.ttf"
TAB_FONT = pygame.font.Font(KOREAN_FONT_PATH, 32)
TAB_WIDTH = 160
TAB_HEIGHT = 40
TAB_MARGIN = 10

def draw_tab_menu(screen, selected_tab, weapons, current_weapon_index):
    screen_width, screen_height = screen.get_size()
    base_x = (screen_width - (TAB_WIDTH * 5 + TAB_MARGIN * 4)) // 2
    tab_rects = []

    for i, name in enumerate(TAB_NAMES):
        rect = pygame.Rect(base_x + i * (TAB_WIDTH + TAB_MARGIN), 20, TAB_WIDTH, TAB_HEIGHT)
        color = (100, 100, 100)
        pygame.draw.rect(screen, color, rect)
        if i == selected_tab:
            pygame.draw.rect(screen, (255, 255, 255), rect, 3)
        text_surface = TAB_FONT.render(name, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)
        tab_rects.append(rect)

    if selected_tab == 0:
        center_text = "내 상태"
        center_surface = TAB_FONT.render(center_text, True, (255, 255, 255))
        center_rect = center_surface.get_rect(center=screen.get_rect().center)
        screen.blit(center_surface, center_rect)
    else:
        weapon_index = selected_tab - 1
        if 0 <= weapon_index < len(weapons):
            weapon = weapons[weapon_index]
            img = weapon.front_image
            max_img_w, max_img_h = 500, 500
            img_w, img_h = img.get_size()
            scale = min(max_img_w / img_w, max_img_h / img_h, 2.0)
            draw_w, draw_h = int(img_w * scale), int(img_h * scale)
            img_surface = pygame.transform.smoothscale(img, (draw_w, draw_h))

            img_pos_x = 50
            img_pos_y = 80

            screen.blit(img_surface, (img_pos_x, img_pos_y))

            name_surface = TAB_FONT.render(weapon.name, True, (255, 255, 255))
            name_rect = name_surface.get_rect(
                center=(img_pos_x + draw_w // 2, img_pos_y + draw_h + 36)
            )
            screen.blit(name_surface, name_rect)
        else:
            empty_text = "(비어있음)"
            empty_surface = TAB_FONT.render(empty_text, True, (150, 150, 150))
            empty_rect = empty_surface.get_rect(center=screen.get_rect().center)
            screen.blit(empty_surface, empty_rect)

    return tab_rects

def handle_tab_click(pos, tab_rects):
    for i, rect in enumerate(tab_rects):
        if rect.collidepoint(pos):
            return i
    return None
