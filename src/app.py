import cv2
from utils.camera import open_camera, read_frame, release_camera
from detection.hand_detector import HandDetector
from gestures.gesture_classifier import GestureClassifier
from gestures.gesture_manager import GestureManager
from ui.ui_manager import UIManager
from transfer.ws_server import WebSocketServer


class HandGestureApp:
    def __init__(self):
        self.gesture_to_spell = {
            "FIST": "ARCANE BOLT",
            "OPENPALM": "FIREBALL", 
            "POINT": "ICE SPIKE",
            "VSIGN": "LIGHTNING",
            "ROCKON": "HEAL",
        }
        
        self.camera = None
        self.detector = HandDetector(max_hands=2)
        self.classifier = GestureClassifier(margin_px=20)
        self.gesture_manager = GestureManager(
            confirmation_delay=0.75,
            gesture_to_spell=self.gesture_to_spell
        )
        self.ui_manager = UIManager(
            font_path="src/ressources/Pixel_Font.ttf",
            icon_path="src/ressources/sprites"
        )

        self.ws_server = WebSocketServer()
        self.ws_server.start()
    
    def initialize_camera(self, width: int = 640, height: int = 480, index: int = 0):
        self.camera = open_camera(index=index, width=width, height=height)
    
    def cleanup(self):
        if self.camera:
            release_camera(self.camera)
        cv2.destroyAllWindows()
    
    def process_frame(self):
        if not self.camera:
            raise RuntimeError("Camera not initialized. Call initialize_camera() first.")
        
        frame = read_frame(self.camera, flip=True)
        annotated_frame, hands = self.detector.detect_hands(frame)
        
        display_text, confirmed_spell, gesture_status = self.gesture_manager.update(
            hands, self.classifier, frame.shape[:2]
        )
        
        if confirmed_spell:
            self.ui_manager.show_spell(confirmed_spell)
            gesture_label = self.gesture_manager.current_gesture or "UNKNOWN"
            print(f"[GestureApp] Sending spell via WebSocket: {confirmed_spell} (gesture={gesture_label})")
            self.ws_server.send_spell(confirmed_spell, gesture_label)
        
        final_frame = self.ui_manager.render_frame(annotated_frame, display_text)
        return final_frame, gesture_status
    
    def run(self):
        self.initialize_camera()
        try:
            while True:
                final_frame, _ = self.process_frame()
                cv2.imshow("Hand Gesture AI", final_frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break
        finally:
            self.cleanup()
    
    def get_gesture_progress(self) -> float:
        return self.gesture_manager.get_progress()
