import pygame
import random
from src.core.camera import Camera
from src.entities.player import Player
from src.entities.npc import NPC


class Game:
    """Main game class to manage game state, entities, and game loop"""

    def __init__(self, width, height, world_width, world_height):
        """Initialize the game with screen and world dimensions"""
        # Initialize pygame
        pygame.init()

        # Game dimensions
        self.width = width
        self.height = height
        self.world_width = world_width
        self.world_height = world_height

        # Create the game window
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Top Down Game")

        # Create the camera
        self.camera = Camera(width, height, world_width, world_height)

        # Create entities
        self.entities = []
        self.player = None

        # Game state
        self.running = False
        self.clock = pygame.time.Clock()
        self.fps = 60

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.GRAY = (200, 200, 200)

    def create_player(self, x, y, radius=15, color=(0, 0, 0)):
        """Create the player entity"""
        self.player = Player(x, y, radius, color)
        self.player.is_player = True  # Mark as player for NPC detection
        self.entities.append(self.player)

        # Set the camera to follow the player
        self.camera.set_target(self.player)

        return self.player

    def create_npc(self, x, y, radius=10, color=None):
        """Create an NPC entity"""
        # Generate a random color if none provided
        if color is None:
            color = (
                random.randint(50, 200),
                random.randint(50, 200),
                random.randint(50, 200),
            )

        npc = NPC(x, y, radius, color)
        self.entities.append(npc)
        return npc

    def spawn_random_npcs(self, count):
        """Spawn a number of NPCs at random positions"""
        for _ in range(count):
            x = random.randint(50, self.world_width - 50)
            y = random.randint(50, self.world_height - 50)
            self.create_npc(x, y)

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Convert screen coordinates to world coordinates
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    world_x, world_y = self.camera.screen_to_world(mouse_x, mouse_y)

                    # Set player target
                    if self.player:
                        self.player.set_target(world_x, world_y)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_f:
                    # Toggle fixed camera
                    self.camera.set_fixed(not self.camera.is_fixed)

    def update(self):
        """Update game state"""
        # Update player
        if self.player:
            self.player.update()
            self.player.constrain_to_boundaries(
                0, 0, self.world_width, self.world_height
            )

        # Update NPCs
        for entity in self.entities:
            if entity != self.player:
                entity.update(entities=self.entities)
                entity.constrain_to_boundaries(
                    0, 0, self.world_width, self.world_height
                )

        # Update camera
        self.camera.update()

    def draw(self):
        """Draw the game"""
        # Clear the screen
        self.screen.fill(self.WHITE)

        # Draw grid for reference
        self._draw_grid()

        # Draw entities
        for entity in sorted(self.entities, key=lambda e: e == self.player):
            if self.camera.is_visible(entity):
                entity.draw(self.screen, (self.camera.x, self.camera.y))

        # Draw world boundaries
        self._draw_world_boundaries()

        # Update the display
        pygame.display.flip()

    def _draw_grid(self):
        """Draw a grid for reference"""
        # Calculate grid start and end based on camera position
        start_x = int((self.camera.x // 50) * 50)
        start_y = int((self.camera.y // 50) * 50)

        # Draw vertical lines
        for x in range(start_x, int(start_x + self.width + 50), 50):
            screen_x = x - self.camera.x
            pygame.draw.line(
                self.screen, self.GRAY, (screen_x, 0), (screen_x, self.height), 1
            )

        # Draw horizontal lines
        for y in range(start_y, int(start_y + self.height + 50), 50):
            screen_y = y - self.camera.y
            pygame.draw.line(
                self.screen, self.GRAY, (0, screen_y), (self.width, screen_y), 1
            )

    def _draw_world_boundaries(self):
        """Draw the world boundaries"""
        # Calculate screen coordinates of world boundaries
        left = 0 - self.camera.x
        top = 0 - self.camera.y
        right = self.world_width - self.camera.x
        bottom = self.world_height - self.camera.y

        # Draw the boundaries
        pygame.draw.rect(
            self.screen, self.RED, (left, top, self.world_width, self.world_height), 2
        )

    def run(self):
        """Run the game loop"""
        self.running = True

        while self.running:
            # Handle events
            self.handle_events()

            # Update game state
            self.update()

            # Draw the game
            self.draw()

            # Cap the frame rate
            self.clock.tick(self.fps)

        # Quit pygame
        pygame.quit()

    def quit(self):
        """Quit the game"""
        self.running = False
