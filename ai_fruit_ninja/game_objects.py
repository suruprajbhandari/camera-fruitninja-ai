import random
import cv2
import math

class Fruit:
    def __init__(self, width, height):
        self.screen_w = width
        self.screen_h = height
        self.radius = random.randint(35, 60)
        self.x = random.randint(100, width - 100)
        
        # Start slightly below the screen
        self.y = height + self.radius
        
        # Velocity
        self.vx = random.uniform(-4, 4)  # horizontal drift
        self.vy = random.uniform(-30, -20) # initial upward burst
        self.gravity = 1.0 # Gravity pulling it down
        
        # Colors: BGR format (since OpenCV uses BGR instead of RGB)
        colors = [
            (0, 0, 255),    # Red (Apple)
            (0, 255, 0),    # Green (Watermelon)
            (0, 165, 255),  # Orange (Orange)
            (255, 0, 255)   # Purple (Plum)
        ]
        self.color = random.choice(colors)
        self.is_sliced = False

    def update(self):
        # Apply physics
        self.x += int(self.vx)
        self.y += int(self.vy)
        self.vy += self.gravity # Gravity accelerates it downwards over time
            
    def draw(self, img):
        if not self.is_sliced:
            # Draw main circle
            cv2.circle(img, (int(self.x), int(self.y)), self.radius, self.color, -1)
            # Draw a white outline for better visibility
            cv2.circle(img, (int(self.x), int(self.y)), self.radius, (255, 255, 255), 3)
            
    def is_off_screen(self):
        # Returns True if it falls completely past the bottom of the screen
        return self.y > self.screen_h + self.radius * 2

    def check_slice(self, finger_x, finger_y):
        if self.is_sliced:
            return False
            
        # Distance formula to check if finger is inside the circle
        dist = math.hypot(self.x - finger_x, self.y - finger_y)
        if dist < self.radius:
            self.is_sliced = True
            return True
        return False
