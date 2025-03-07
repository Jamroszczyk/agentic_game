# Top Down Game

A simple top-down game created with Pygame where you control a black sphere on a white background.

## Game Features

- 800 x 600 playable area with grid lines
- White background
- Black player sphere
- Click-to-move controls (similar to Baldur's Gate)
- Smooth movement with momentum and physics
- Advanced gradual deceleration system with minimum velocity
- Smooth final approach and stopping behavior
- Momentum reduction to prevent orbiting
- Fixed camera (no scrolling)
- Visual indicators for movement target and velocity

## Requirements

- Python 3.x
- Pygame 2.5.2

## Installation

1. Make sure you have Python installed on your system.
2. Install the required package:

```bash
pip install pygame==2.5.2
```

## How to Run

Simply run the main.py file:

```bash
python main.py
```
or
```bash
python3 main.py
```

## Controls

- Left-click: Move player to the clicked location
- Close the window to exit the game

## Physics Details

- The player has momentum, meaning it will gradually accelerate and decelerate
- When changing direction, the player will smoothly transition rather than making sharp turns
- The player will bounce slightly when hitting the boundaries of the play area
- A blue line shows the current velocity vector (direction and magnitude)
- Pink circle shows the deceleration zone - the player slows down gradually in this area
- Blue circle shows the momentum reduction zone where sideways momentum is reduced
- Green circle shows the final approach zone where the player smoothly decelerates to stop
- Two-phase movement system: normal movement followed by a specialized final approach
- Linear deceleration curve provides smooth slowdown while maintaining minimum velocity
- Final approach uses gradual velocity blending for a smooth, natural stop
- Direction change detection applies extra momentum reduction when changing course
- Perpendicular velocity reduction prevents orbiting by reducing sideways momentum
- Anti-orbiting system prevents the player from circling around the target even with rapid direction changes
- Visual indicator changes color during final approach phase 