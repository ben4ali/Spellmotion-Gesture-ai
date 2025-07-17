import cv2
from utils.camera import open_camera, read_frame, release_camera
from detection.hand_detector import HandDetector
from gestures.gesture_classifier import GestureClassifier

def main():
    cap = open_camera(index=0, width=640, height=480)
    detector = HandDetector(max_hands=2)
    classifier = GestureClassifier(margin_px=20)

    try:
        while True:
            frame = read_frame(cap, flip=True)
            annotated_frame, hands = detector.detect_hands(frame)

            if hands:
                label, info = classifier.classify(hands[0], image_shape=frame.shape[:2])
                text = f"{label} {info['fingers']}"
                cv2.putText(annotated_frame, text, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            cv2.imshow("Hand Gesture AI", annotated_frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        release_camera(cap)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
