import cv2
import numpy as np
from PIL import Image
from typing import Optional, Dict
from .hud import load_font, load_spell_icons, draw_gesture_status, draw_spell_icon_with_label, SpellDisplayManager

class UIManager:
    
    def __init__(self, font_path: str, icon_path: str, font_size: int = 34, icon_size: tuple = (100, 100)):
        self.font = load_font(font_path, size=font_size)
        self.icons = load_spell_icons(icon_path, size=icon_size)
        self.spell_manager = SpellDisplayManager(display_duration=1.0, fade_duration=0.3)
    
    def show_spell(self, spell_name: str):
        """Déclenche l'affichage d'un sort"""
        self.spell_manager.show_spell(spell_name)
    
    def render_frame(self, annotated_frame: np.ndarray, gesture_text: Optional[str] = None) -> np.ndarray:
        pil_img = Image.fromarray(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB))

        if gesture_text:
            draw_gesture_status(pil_img, gesture_text, font=self.font)
        
        draw_spell_icon_with_label(pil_img, self.spell_manager, self.icons, font=self.font, margin_right=50)

        final_frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        return final_frame
    
    def update_spell_display_settings(self, display_duration: float = None, fade_duration: float = None):
        if display_duration is not None:
            self.spell_manager.display_duration = display_duration
        if fade_duration is not None:
            self.spell_manager.fade_duration = fade_duration
