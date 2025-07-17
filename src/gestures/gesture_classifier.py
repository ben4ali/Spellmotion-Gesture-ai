from typing import List, Tuple, Dict, Optional
import math

WRIST = 0
THUMB_IDS  = [1, 2, 3, 4]
INDEX_IDS  = [5, 6, 7, 8]
MIDDLE_IDS = [9,10,11,12]
RING_IDS   = [13,14,15,16]
PINKY_IDS  = [17,18,19,20]

class GestureClassifier:
    def __init__(self, margin_px: int = 20):
        self.margin_px = margin_px

    def _finger_extended_vertical(self, landmarks, mcp_idx, tip_idx) -> bool:
        _, mcp_y = landmarks[mcp_idx]
        _, tip_y = landmarks[tip_idx]
        return (mcp_y - tip_y) > self.margin_px

    def _thumb_extended(self, landmarks) -> bool:
        wrist_x, wrist_y = landmarks[WRIST]
        tip_x, tip_y = landmarks[THUMB_IDS[-1]]
        ip_x, ip_y   = landmarks[THUMB_IDS[-2]]

        dist_tip = math.hypot(tip_x - wrist_x, tip_y - wrist_y)
        dist_ip  = math.hypot(ip_x - wrist_x, ip_y - wrist_y)

        return dist_tip > dist_ip * 1.1

    def fingers_state(self, landmarks) -> List[int]:
        thumb  = 1 if self._thumb_extended(landmarks) else 0
        index  = 1 if self._finger_extended_vertical(landmarks, INDEX_IDS[0],  INDEX_IDS[-1])  else 0
        middle = 1 if self._finger_extended_vertical(landmarks, MIDDLE_IDS[0], MIDDLE_IDS[-1]) else 0
        ring   = 1 if self._finger_extended_vertical(landmarks, RING_IDS[0],   RING_IDS[-1])   else 0
        pinky  = 1 if self._finger_extended_vertical(landmarks, PINKY_IDS[0],  PINKY_IDS[-1])  else 0
        return [thumb, index, middle, ring, pinky]

    def classify_pattern(self, fingers: List[int]) -> str:
        t,i,m,r,p = fingers

        if i==0 and m==0 and r==0 and p==0:
            return "Fist"

        if i==1 and m==1 and r==1 and p==1:
            return "OpenPalm"

        if i==1 and m==0 and r==0 and p==0:
            return "Point"

        if i==1 and m==1 and r==0 and p==0:
            return "VSign"
        
        if t==1 and i==0 and m==0 and r==0 and p==1:
            return "RockOn"
      
        
        return "Unknown"

    def classify(self, landmarks: List[Tuple[int,int]], image_shape=None) -> Tuple[str, Dict]:
        fingers = self.fingers_state(landmarks)
        label = self.classify_pattern(fingers)

        confidence = 1.0 if label != "Unknown" else 0.5

        info = {
            "fingers": fingers,
            "confidence": confidence
        }
        return label, info
