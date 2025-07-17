import time
import cv2
from utils.camera import open_camera, read_frame, release_camera
from detection.hand_detector import HandDetector
from gestures.gesture_classifier import GestureClassifier

current_gesture = None
gesture_start_time = 0
CONFIRMATION_DELAY = 1.5

def main():
    global current_gesture, gesture_start_time

    cap = open_camera(index=0, width=640, height=480)
    detector = HandDetector(max_hands=2)
    classifier = GestureClassifier(margin_px=20)

    try:
        while True:
            frame = read_frame(cap, flip=True)
            annotated_frame, hands = detector.detect_hands(frame)

            if hands:
                label, info = classifier.classify(hands[0], image_shape=frame.shape[:2])
                
                now = time.time()
                if label == current_gesture and current_gesture != "Unknown":
                    if now - gesture_start_time >= CONFIRMATION_DELAY:
                        display_text = f"{label} CONFIRMED"
                    else:
                        display_text = f"{label} (holding...)"
                else:
                    current_gesture = label
                    gesture_start_time = now
                    display_text = f"{label} (new)"
                    
                if current_gesture!="Unknown":
                    cv2.putText(annotated_frame, display_text, (10, 30),
                                cv2.FONT_HERSHEY_TRIPLEX, 1, (0,255,0), 2)

            cv2.imshow("Hand Gesture AI", annotated_frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        release_camera(cap)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
