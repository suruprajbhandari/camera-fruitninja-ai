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

    def check_slice_line(self, p1, p2, blade_radius=40):
        if self.is_sliced:
            return False
            
        x1, y1 = p1
        x2, y2 = p2
        cx, cy = self.x, self.y
        # Total collision radius is the fruit's radius PLUS the hand's radius
        r = self.radius + blade_radius
        
        # 1. Check if either point is inside the circle (slow swipe)
        if math.hypot(x1 - cx, y1 - cy) < r or math.hypot(x2 - cx, y2 - cy) < r:
            self.is_sliced = True
            return True
            
        # 2. Check if the line segment between the two frames crossed the circle (fast swipe)
        dx = x2 - x1
        dy = y2 - y1
        length_sq = dx*dx + dy*dy
        
        if length_sq == 0:
            return False
            
        # Find the closest point on the line segment to the center of the fruit
        t = max(0, min(1, ((cx - x1) * dx + (cy - y1) * dy) / length_sq))
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        # If the closest point is inside the total radius, it was a slice!
        if math.hypot(closest_x - cx, closest_y - cy) < r:
            self.is_sliced = True
            return True
            
        return False
