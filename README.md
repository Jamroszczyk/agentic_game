# Top Down Game

A simple top-down game created with Pygame where you control a black sphere in a world with NPCs.

## Game Features

- 1000 x 1000 world with grid lines
- White background
- Black player sphere with smooth movement
- NPCs with basic AI behaviors (wander, follow, flee)
- Click-to-move controls (similar to Baldur's Gate)
- Smooth movement with momentum and physics
- Advanced gradual deceleration system with minimum velocity
- Smooth final approach and stopping behavior
- Camera system that follows the player

## Project Structure

```
.
├── main.py                 # Main entry point
├── src/                    # Source code
│   ├── core/               # Core game functionality
│   │   ├── camera.py       # Camera handling
│   │   ├── constants.py    # Game constants
│   │   └── game.py         # Main game class
│   ├── entities/           # Game entities
│   │   ├── entity.py       # Base entity class
│   │   ├── player.py       # Player class
│   │   └── npc.py          # NPC class
│   ├── utils/              # Utility functions
│   └── assets/             # Game assets
```

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
- ESC: Quit the game
- F: Toggle fixed/following camera
- Close the window to exit the game

## Adding New Entities

To add a new type of entity to the game:

1. Create a new class in the `src/entities` directory that inherits from `Entity`
2. Override the `update` and `draw` methods as needed
3. Add any specific behavior methods
4. Create instances of your new entity in the `Game` class

Example:

```python
# src/entities/my_entity.py
from src.entities.entity import Entity

class MyEntity(Entity):
    def __init__(self, x, y, radius, color=(255, 0, 0)):
        super().__init__(x, y, radius, color, speed=2, max_velocity=3)
        # Add custom properties
        
    def update(self, delta_time=1.0):
        # Custom update logic
        super().update(delta_time)  # Don't forget to call the parent update
        
    def draw(self, screen, camera_offset=(0, 0)):
        # Custom drawing
        super().draw(screen, camera_offset)  # Call parent draw method
```

Then in game.py:

```python
from src.entities.my_entity import MyEntity

# In the Game class
def create_my_entity(self, x, y):
    my_entity = MyEntity(x, y, 10)
    self.entities.append(my_entity)
    return my_entity
```

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