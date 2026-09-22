# AI Camera Fruit Ninja 🍉⚔️

A computer vision-based Fruit Ninja clone where you use your actual hands to slice virtual fruits on your webcam feed!

## Features (Beta)
- **Hand Tracking:** Play by swiping your index finger in the air.
- **Dual Wielding Option:** Track one hand or both hands.
- **Timer Mode:** Slice as many fruits as you can in 60 seconds.
- **Pure Python:** Built using OpenCV and MediaPipe without a heavy game engine.

## Installation

1. Clone or download this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

Run the main script:
```bash
python main.py
```

- Stand/sit in front of your webcam.
- The game will track your index finger(s).
- Fruits (colored circles for now) will fly up from the bottom of the screen.
- Swipe your finger through the center of a fruit to slice it and score points.
- You have 60 seconds to get the highest score!

### Controls & Options
Inside `main.py`, you can change the `MAX_HANDS` variable to `1` or `2` to toggle between single-blade and dual-wielding mode.

## Future Updates Planned
- [ ] Replace simple colored circles with actual fruit image sprites (Apples, Watermelons, etc.).
- [ ] Add a "Survival Mode" with lives.
- [ ] Add bomb obstacles.
- [ ] Particle effects when slicing.
