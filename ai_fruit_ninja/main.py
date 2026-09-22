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
            img = tracker.find_hands(img, draw=False) 
            hand_centers = tracker.get_hand_centers(img)
            
            # --- BLADE TRAILS ---
            # Update history of positions for each hand
            for i in range(MAX_HANDS):
                if i < len(hand_centers):
                    blade_trails[i].append(hand_centers[i])
                    # Keep only the last 7 frames for the trail length
                    if len(blade_trails[i]) > 7: 
                        blade_trails[i].pop(0)
                else:
                    # Hand was lost, clear its trail
                    blade_trails[i] = [] 
            
            # Draw the blade trails
            for trail in blade_trails:
                for i in range(1, len(trail)):
                    # Make the trail massive since it represents the whole hand now
                    thickness = int(i * 3)
                    # Outer white glow
                    cv2.line(img, trail[i-1], trail[i], (255, 255, 255), thickness + 5)
                    # Inner yellow blade
                    cv2.line(img, trail[i-1], trail[i], (0, 200, 255), max(1, thickness - 2))

            # Update and draw fruits
            for fruit in fruits[:]:
                fruit.update()
                fruit.draw(img)
                
                # Check for collisions with whole hand (fast swipe detection)
                for trail in blade_trails:
                    if len(trail) >= 2:
                        p1 = trail[-2]
                        p2 = trail[-1]
                        # blade_radius=70 creates a huge hit-box around your hand
                        if fruit.check_slice_line(p1, p2, blade_radius=70):
                            score += 10
                            fruits.remove(fruit)
                            break # Stop checking other hands for this fruit
                
                # Remove if it falls off the bottom of the screen
                if fruit in fruits and fruit.is_off_screen():
                    fruits.remove(fruit)
                    
            # Draw a massive glowing aura on your hands so you know exactly where your hit-box is
            for center in hand_centers:
                cv2.circle(img, (center[0], center[1]), 20, (0, 150, 255), cv2.FILLED)
                cv2.circle(img, (center[0], center[1]), 35, (255, 255, 255), 3)
                    
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
