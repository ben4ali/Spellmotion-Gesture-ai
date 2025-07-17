import os
import time
from typing import Dict, Tuple, Optional

import cv2  
import numpy as np
from PIL import Image, ImageDraw, ImageFont, Image

def load_font(font_path: str, size: int = 34) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(font_path, size=size)

SPELL_COLORS = {
    "ARCANE BOLT": (180, 160, 255),
    "FIREBALL": (255, 140, 60),
    "HEAL": (100, 255, 120),
    "LIGHTNING": (50, 150, 255),
    "ICE SPIKE": (150, 240, 255),
}

class SpellDisplayManager:
    def __init__(self, display_duration: float = 1.75, fade_duration: float = 0.2):
        self.display_duration = display_duration
        self.fade_duration = fade_duration
        self.current_spell = None
        self.display_start_time = None
    
    def show_spell(self, spell_name: str):
        self.current_spell = spell_name
        self.display_start_time = time.time()
    
    def get_current_spell_with_alpha(self) -> tuple[Optional[str], float]:
        if self.current_spell is None or self.display_start_time is None:
            return None, 0.0
        
        elapsed_time = time.time() - self.display_start_time
        
        if elapsed_time >= self.display_duration:
            self.current_spell = None
            self.display_start_time = None
            return None, 0.0
        
        if elapsed_time < self.fade_duration:
            alpha = elapsed_time / self.fade_duration
        elif elapsed_time > (self.display_duration - self.fade_duration):
            fade_out_start = self.display_duration - self.fade_duration
            remaining_time = self.display_duration - elapsed_time
            alpha = remaining_time / self.fade_duration
        else:
            alpha = 1.0
        
        return self.current_spell, max(0.0, min(1.0, alpha))
    
    def get_current_spell(self) -> Optional[str]:
        spell_name, alpha = self.get_current_spell_with_alpha()
        return spell_name if alpha > 0 else None

def load_spell_icons(base_path: str, size: Tuple[int, int] = (100, 100)) -> Dict[str, Image.Image]:
    mapping = {
        "ARCANE BOLT": "Arcane_Bolt.png",
        "FIREBALL":    "Fireball.png",
        "HEAL":        "Heal.png",
        "ICE SPIKE":   "Icespikes.png",
        "LIGHTNING":   "Lightning.png",
    }
    out = {}
    for spell, fname in mapping.items():
        p = os.path.join(base_path, fname)
        img = Image.open(p).convert("RGBA")
        if size is not None:
            img = img.resize(size, Image.Resampling.LANCZOS)
        out[spell] = img
    return out

def draw_gesture_status(
    pil_img: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont,
    pos: Tuple[int, int] = (25, 25),
    color: Tuple[int, int, int] = (90, 210, 255),
) -> None:
    draw = ImageDraw.Draw(pil_img)
    draw.text(pos, text, font=font, fill=color)


def draw_spell_icon_with_label(
    pil_img: Image.Image,
    spell_display_manager: SpellDisplayManager,
    icons: Dict[str, Image.Image],
    font: ImageFont.FreeTypeFont,
    margin_right: int = 20,
    margin_top: int = 20,
    gap_text: int = 5,
    text_color: Tuple[int, int, int] = (255, 255, 255),
    text_size_scale: float = 0.7,
) -> None:
    spell_name, alpha = spell_display_manager.get_current_spell_with_alpha()
    if spell_name is None or alpha <= 0:
        return
    
    icon = icons.get(spell_name)
    if icon is None:
        return

    w = pil_img.width
    icon_w, icon_h = icon.size

    pos_x = w - icon_w - margin_right
    pos_y = margin_top

    if alpha < 1.0:
        faded_icon = icon.copy()
        if faded_icon.mode != 'RGBA':
            faded_icon = faded_icon.convert('RGBA')
        
        alpha_channel = faded_icon.split()[-1]
        alpha_channel = alpha_channel.point(lambda p: int(p * alpha))
        faded_icon.putalpha(alpha_channel)
        
        pil_img.paste(faded_icon, (pos_x, pos_y), faded_icon)
    else:
        pil_img.paste(icon, (pos_x, pos_y), icon)

    spell_text = spell_name.upper()
    
    original_font_size = font.size
    smaller_font_size = int(original_font_size * text_size_scale)
    smaller_font = ImageFont.truetype(font.path, size=smaller_font_size)
    
    spell_color = SPELL_COLORS.get(spell_name, text_color)
    
    text_color_with_alpha = (
        spell_color[0],
        spell_color[1], 
        spell_color[2],
        int(255 * alpha)
    )
    
    temp_img = Image.new('RGBA', pil_img.size, (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    
    bbox = temp_draw.textbbox((0, 0), spell_text, font=smaller_font)
    text_w = bbox[2] - bbox[0]

    text_x = pos_x + (icon_w - text_w) // 2
    text_y = pos_y + icon_h + gap_text

    temp_draw.text((text_x, text_y), spell_text, font=smaller_font, fill=text_color_with_alpha)

    pil_img.paste(temp_img, (0, 0), temp_img)
