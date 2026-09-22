import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class HandTracker:
    def __init__(self, mode=False, max_hands=2, detection_con=0.4, track_con=0.4):
        self.max_hands = max_hands
        
        base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=self.max_hands,
            min_hand_detection_confidence=float(detection_con),
            min_hand_presence_confidence=float(track_con),
            min_tracking_confidence=float(track_con)
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.results = None
        
    def find_hands(self, img, draw=False):
        # Convert the frame to RGB for MediaPipe
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        # Detect hands using the tasks API
        self.results = self.detector.detect(mp_image)
        
        # We don't draw the skeleton since the game draws blade trails instead.
        return img
        
    def get_hand_centers(self, img):
        """Returns a list of (x,y) coordinates for the center of the palm."""
        positions = []
        if self.results and self.results.hand_landmarks:
            for hand_landmarks in self.results.hand_landmarks:
                # Landmark 9 is the middle finger MCP (basically the center of the palm/knuckles)
                lm = hand_landmarks[9]
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                positions.append((cx, cy))
        return positions
