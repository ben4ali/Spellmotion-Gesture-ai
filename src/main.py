import cv2
from utils.camera import open_camera, read_frame, release_camera

def main():
    cap = open_camera(index=0, width=640, height=480)

    try:
        while True:
            frame = read_frame(cap, flip=True)

            cv2.imshow("Webcam - Press ESC to quit", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        release_camera(cap)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
