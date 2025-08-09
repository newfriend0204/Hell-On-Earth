import pygame
import ui

class DialogueManager:
    def __init__(self):
        self.active = False
        self.dialogue_data = None
        self.idx = 0
        self.selected_choice = 0
        self.on_effect_callback = None
        self.close_callback = None
        self.dialogue_history = []
        self.history_anim_timer = 0 
        self.HISTORY_ANIM_TIME = 12
        self.history_queue = []
        self.override_text = None
        self.override_speaker = None
        self._hud_status = None

    def set_hud_status(self, hp, hp_max, ammo, ammo_max):
        # 대화 중 좌하단에 띄울 필드 상태값 전달
        self._hud_status = (hp, hp_max, ammo, ammo_max)

    def start(self, dialogue_data, on_effect_callback=None, close_callback=None):
        self.active = True
        self.dialogue_data = dialogue_data
        self.idx = 0
        self.selected_choice = 0
        self.on_effect_callback = on_effect_callback
        self.close_callback = close_callback
        self.dialogue_history = []
        self.history_anim_timer = 0
        self.history_queue = []
        self.override_text = None
        self.override_speaker = None

    def update(self, event_list):
        if not self.active:
            self._drain_history_queue()
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
                    choice = node["choices"][self.selected_choice]
                    if "next" in choice and choice["next"] is not None:
                        self.next_dialogue(choice["next"])
                        self.selected_choice = 0
                        self._apply_effect_if_any()
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
        
        self._drain_history_queue()
        self.update_history_anim()

    def enqueue_history_line(self, speaker, text):
        if not text:
            return
        self.history_queue.append((speaker or "", text))

    def _drain_history_queue(self):
        # 대기중인 줄을 모두 히스토리에 편입
        while self.history_queue:
            speaker, text = self.history_queue.pop(0)
            self.dialogue_history.append({
                "speaker": speaker,
                "text": text,
                "anim_y": 0,
            })
            if len(self.dialogue_history) > 3:
                self.dialogue_history.pop(0)
            self.history_anim_timer = self.HISTORY_ANIM_TIME

    def next_dialogue(self, next_idx=None):
        if self.override_text:
            self.enqueue_history_line(self.override_speaker or "", self.override_text)
            self.override_text = None
            self.override_speaker = None

        node = self.dialogue_data[self.idx]
        text_to_push = node.get("text", "")
        if text_to_push:
            self.enqueue_history_line(node.get("speaker", ""), text_to_push)

        if next_idx is not None:
            self.idx = next_idx

    def update_history_anim(self):
        if self.history_anim_timer > 0:
            for entry in self.dialogue_history:
                entry["anim_y"] -= 6
            self.history_anim_timer -= 1

    def draw(self, screen):
        # 현재 노드를 대화 박스로 그린다(좌하단 미니 HUD 포함).
        if not self.active:
            return
        node_src = self.dialogue_data[self.idx]
        node = dict(node_src) if node_src else {}
        if self.override_text is not None:
            node["text"] = self.override_text
            if self.override_speaker is not None:
                node["speaker"] = self.override_speaker
        ui.draw_dialogue_box_with_choices(
            screen,
            node,
            self.selected_choice,
            history=self.dialogue_history,
            hud_status=self._hud_status
        )

    def _apply_effect_if_any(self):
        node = self.dialogue_data[self.idx]
        effect = node.get("effect")
        if effect and self.on_effect_callback:
            as_text_only = not bool(node.get("text"))
            line = self.on_effect_callback(effect, node.get("effect_messages"), as_text_only)
            if as_text_only:
                self.override_text = line or ""
                self.override_speaker = node.get("speaker", "")

    def close(self):
        # 대화 강제 종료(ESC, 마지막 대사, main에서 콜백 등)
        self.active = False
        self.dialogue_data = None
        self.idx = 0
        self.selected_choice = 0
        if self.close_callback:
            self.close_callback()