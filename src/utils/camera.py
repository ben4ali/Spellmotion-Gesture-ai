import cv2

def open_camera(index=0, width=None, height=None):
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index {index}")

    if width is not None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    if height is not None:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    return cap


def read_frame(cap, flip=False):
    ok, frame = cap.read()
    if not ok or frame is None:
        raise RuntimeError("Failed to read frame from camera.")
    if flip:
        frame = cv2.flip(frame, 1)
    return frame


def release_camera(cap):
    if cap is not None:
        cap.release()