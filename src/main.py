import time
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from utils.camera import open_camera, read_frame, release_camera
from detection.hand_detector import HandDetector
from gestures.gesture_classifier import GestureClassifier

current_gesture = None
gesture_start_time = 0
CONFIRMATION_DELAY = 1.5

def main():
    global current_gesture, gesture_start_time

    # Charge la police pixel art
    font_path = "src/ressources/Pixel_Font.ttf"
    font = ImageFont.truetype(font_path, size=34)

    cap = open_camera(index=0, width=640, height=480)
    detector = HandDetector(max_hands=2)
    classifier = GestureClassifier(margin_px=20)

    try:
        while True:
            frame = read_frame(cap, flip=True)
            annotated_frame, hands = detector.detect_hands(frame)

            pil_img = Image.fromarray(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_img)

            if hands:
                label, info = classifier.classify(hands[0], image_shape=frame.shape[:2])
                label = label.upper()

                if label == "UNKNOWN":
                    current_gesture = None
                    gesture_start_time = 0
                else:
                    now = time.time()
                    if label == current_gesture:
                        if now - gesture_start_time >= CONFIRMATION_DELAY:
                            display_text = f"{label} CONFIRMED"
                        else:
                            display_text = f"{label} (HOLDING...)"
                    else:
                        current_gesture = label
                        gesture_start_time = now
                        display_text = f"{label} (NEW)"

                    draw.text((25, 25), display_text, font=font, fill=(90, 210, 255))
                    annotated_frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                
            cv2.imshow("Hand Gesture AI", annotated_frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        release_camera(cap)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
