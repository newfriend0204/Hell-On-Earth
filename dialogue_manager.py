# dialogue_manager.py

import pygame

class DialogueManager:
    def __init__(self):
        self.active = False
        self.dialogue_data = None
        self.idx = 0
        self.selected_choice = 0
        self.on_effect_callback = None
        self.close_callback = None
        self.dialogue_history = []      # [(speaker, text, anim_y)]  최근 3~4개
        self.history_anim_timer = 0     # 0: 애니메이션 없음, >0: 애니중
        self.HISTORY_ANIM_TIME = 12     # 애니메이션 프레임 (0.2초)

    def start(self, dialogue_data, on_effect_callback=None, close_callback=None):
        self.active = True
        self.dialogue_data = dialogue_data
        self.idx = 0
        self.selected_choice = 0
        self.on_effect_callback = on_effect_callback
        self.close_callback = close_callback
        self.dialogue_history = []   # 대화 시작 시 히스토리 비움
        self.history_anim_timer = 0

    def update(self, event_list):
        if not self.active:
            return

        node = self.dialogue_data[self.idx]

        if node.get("choices"):
            # 선택지 상태
            num_choices = len(node["choices"])
            for event in event_list:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.selected_choice = (self.selected_choice - 1) % num_choices
                    elif event.key == pygame.K_s:
                        self.selected_choice = (self.selected_choice + 1) % num_choices
                    elif event.key == pygame.K_ESCAPE:
                        self.close()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # 좌클릭 → 선택 확정
                    choice = node["choices"][self.selected_choice]
                    # 선택지의 효과(회복 등)는 next node에서 반영
                    if "next" in choice and choice["next"] is not None:
                        self.next_dialogue(choice["next"])
                        self.selected_choice = 0
                        self._apply_effect_if_any()  # 선택지 효과도 지원
                    else:
                        self.close()
        else:
            # 단순 대사(선택지 없음): 좌클릭으로 진행, ESC로 종료
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if "next" in node and node["next"] is not None:
                        self.next_dialogue(node["next"])
                        self.selected_choice = 0
                        self._apply_effect_if_any()
                    else:
                        self.close()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.close()
            
        self.update_history_anim()

    def next_dialogue(self, next_idx=None):
            # 이전 대화 저장 (현재 node)
            node = self.dialogue_data[self.idx]
            self.dialogue_history.append({
                "speaker": node.get("speaker", ""),
                "text": node.get("text", ""),
                "anim_y": 0
            })
            if len(self.dialogue_history) > 3:
                self.dialogue_history.pop(0)
            self.history_anim_timer = self.HISTORY_ANIM_TIME
            # 인덱스 이동
            if next_idx is not None:
                self.idx = next_idx

    def update_history_anim(self):
        if self.history_anim_timer > 0:
            for entry in self.dialogue_history:
                entry["anim_y"] -= 6   # 한 프레임에 6픽셀씩 위로
            self.history_anim_timer -= 1

    def draw(self, screen, ui_draw_func):
        if not self.active:
            return
        node = self.dialogue_data[self.idx]
        # draw 함수가 history를 인자로 받도록!
        ui_draw_func(screen, node, self.selected_choice, self.dialogue_history)

    def _apply_effect_if_any(self):
        """
        HP/탄약 회복 등 효과 적용(콜백으로 메인에 전달)
        """
        node = self.dialogue_data[self.idx]
        effect = node.get("effect")
        if effect and self.on_effect_callback:
            self.on_effect_callback(effect)

    def close(self):
        """
        대화 강제 종료(ESC, 마지막 대사, main에서 콜백 등)
        """
        self.active = False
        self.dialogue_data = None
        self.idx = 0
        self.selected_choice = 0
        if self.close_callback:
            self.close_callback()
