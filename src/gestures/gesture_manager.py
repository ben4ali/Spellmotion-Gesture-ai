import time
from typing import Optional, Dict, Tuple
from .gesture_classifier import GestureClassifier

class GestureManager:
  
    def __init__(self, confirmation_delay: float = 0.75, gesture_to_spell: Dict[str, str] = None):
        self.confirmation_delay = confirmation_delay
        self.gesture_to_spell = gesture_to_spell or {}

        self.current_gesture = None
        self.gesture_start_time = 0.0
        self.spell_triggered = False
        
    def update(self, hands, classifier: GestureClassifier, frame_shape: Tuple[int, int]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        if not hands:
            self._reset_state()
            return None, None, 'UNKNOWN'
            
        label, info = classifier.classify(hands[0], image_shape=frame_shape)
        label = label.upper()
        
        if label == "UNKNOWN":
            self._reset_state()
            return None, None, 'UNKNOWN'
        
        now = time.time()
        
        if label == self.current_gesture:
            if now - self.gesture_start_time >= self.confirmation_delay:
                display_text = f"{label} CONFIRMED"
                confirmed_spell = self.gesture_to_spell.get(label)
                
                if confirmed_spell and not self.spell_triggered:
                    self.spell_triggered = True
                    return display_text, confirmed_spell, 'CONFIRMED'
                else:
                    return display_text, None, 'CONFIRMED'
            else:
                display_text = f"{label} (holding...)"
                return display_text, None, 'HOLDING'
        else:
            self.current_gesture = label
            self.gesture_start_time = now
            self.spell_triggered = False
            display_text = f"{label} (NEW)"
            return display_text, None, 'NEW'
    
    def _reset_state(self):
        self.current_gesture = None
        self.gesture_start_time = 0.0
        self.spell_triggered = False
    
    def get_progress(self) -> float:
        if self.current_gesture is None:
            return 0.0
        
        elapsed = time.time() - self.gesture_start_time
        return min(1.0, elapsed / self.confirmation_delay)
