import cv2
import time
import random
import os
import urllib.request
from hand_tracking import HandTracker
from game_objects import Fruit

# --- GAME CONFIGURATION ---
MAX_HANDS = 2       # Change to 1 for single-hand mode
GAME_DURATION = 60  # seconds
# --------------------------

def download_model():
    model_path = 'hand_landmarker.task'
    if not os.path.exists(model_path):
        print("Downloading AI hand tracking model (this only happens once)...")
        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        urllib.request.urlretrieve(url, model_path)
        print("Download complete!")

def main():
    download_model()
    # 0 is the default camera. If you have multiple, you might need to change it to 1 or 2.
    cap = cv2.VideoCapture(0)
    
    # Try to set a high resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Initialize the MediaPipe hand tracker
    tracker = HandTracker(max_hands=MAX_HANDS)
    
    fruits = []
    score = 0
    start_time = time.time()
    game_over = False
    
    # Store previous finger positions to draw the "sword trail" effect
    blade_trails = [[] for _ in range(MAX_HANDS)]
    
    print("Game Started! Press 'Q' in the window to quit.")
    
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to read from camera. Ensure it is connected.")
            break
            
        # Flip image horizontally for a mirror effect (more natural to play)
        img = cv2.flip(img, 1)
        h, w, c = img.shape
        
        if not game_over:
            # Timer logic
            elapsed_time = time.time() - start_time
            time_left = max(0, GAME_DURATION - int(elapsed_time))
            
            if time_left == 0:
                game_over = True
                
            # Randomly spawn fruits
            # Spawns roughly 1 fruit every second at 30 FPS (0.03 * 30 ~ 1)
            if random.random() < 0.04: 
                fruits.append(Fruit(w, h))
                
            # --- HAND TRACKING ---
            # We pass draw=False because we want to draw our own ninja blade, not dots
            img = tracker.find_hands(img, draw=False) 
            fingers = tracker.get_index_fingers(img)
            
            # --- BLADE TRAILS ---
            # Update history of finger positions for each hand
            for i in range(MAX_HANDS):
                if i < len(fingers):
                    blade_trails[i].append(fingers[i])
                    # Keep only the last 7 frames for the trail length
                    if len(blade_trails[i]) > 7: 
                        blade_trails[i].pop(0)
                else:
                    # Hand was lost, clear its trail
                    blade_trails[i] = [] 
            
            # Draw the blade trails
            for trail in blade_trails:
                for i in range(1, len(trail)):
                    thickness = int(i * 1.5)
                    # Outer white glow
                    cv2.line(img, trail[i-1], trail[i], (255, 255, 255), thickness + 2)
                    # Inner yellow blade
                    cv2.line(img, trail[i-1], trail[i], (0, 200, 255), max(1, thickness - 2))

            # --- UPDATE AND DRAW FRUITS ---
            # Iterate backwards or over a copy to safely remove items from list
            for fruit in fruits[:]:
                fruit.update()
                fruit.draw(img)
                
                # Check for collisions with fingers
                for finger in fingers:
                    if fruit.check_slice(finger[0], finger[1]):
                        score += 10
                        # Fruit is sliced, remove it from screen immediately for Beta
                        fruits.remove(fruit)
                        break # Stop checking other fingers for this fruit
                
                # Remove if it falls off the bottom of the screen
                if fruit in fruits and fruit.is_off_screen():
                    fruits.remove(fruit)
                    
            # --- DRAW UI ---
            # Score
            cv2.putText(img, f"Score: {score}", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)
            
            # Timer (Turns red in last 10 seconds)
            timer_color = (0, 0, 255) if time_left <= 10 else (255, 255, 255)
            cv2.putText(img, f"Time: {time_left}s", (w - 300, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, timer_color, 4)
            
        else:
            # --- GAME OVER SCREEN ---
            cv2.putText(img, "GAME OVER", (w//2 - 200, h//2 - 50), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 255), 5)
            cv2.putText(img, f"Final Score: {score}", (w//2 - 200, h//2 + 50), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 0), 4)
            cv2.putText(img, "Press 'R' to Restart or 'Q' to Quit", (w//2 - 350, h//2 + 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
            
            # Check for restart or quit inputs during Game Over
            key = cv2.waitKey(1) & 0xFF
            if key == ord('r'):
                # Reset game state
                fruits = []
                score = 0
                start_time = time.time()
                game_over = False
                blade_trails = [[] for _ in range(MAX_HANDS)]
            elif key == ord('q'):
                break

        # Show the final composite image
        cv2.imshow("AI Fruit Ninja", img)
        
        # Check for quit input during normal gameplay
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
