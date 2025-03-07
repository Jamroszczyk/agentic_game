import pygame
import sys
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600  # Window size (now also the playable area)
PLAYER_RADIUS = 10
PLAYER_SPEED = 5
PLAYER_ACCELERATION = 0.5  # How quickly player accelerates
PLAYER_FRICTION = 0.9  # Friction to slow down player (0-1)
MAX_VELOCITY = 5  # Maximum velocity
MIN_VELOCITY = 2.0  # Minimum velocity even when close to target
FINAL_APPROACH_DISTANCE = 15  # Distance at which to start final approach
SLOWDOWN_DISTANCE = 100  # Distance at which to start slowing down
MOMENTUM_REDUCTION_DISTANCE = 50  # Distance at which to start reducing momentum
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top Down Game - Smooth Movement")


# Player class
class Player:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = PLAYER_SPEED
        self.target_x = None
        self.target_y = None
        self.moving = False
        self.path = []

        # Add velocity for momentum
        self.vel_x = 0
        self.vel_y = 0

        # Track previous direction for momentum reduction
        self.prev_dx = 0
        self.prev_dy = 0
        self.direction_change_timer = 0

        # Final approach flag
        self.final_approach = False

    def set_target(self, x, y):
        # Set a target position for the player to move towards
        self.target_x = x
        self.target_y = y
        self.moving = True
        self.final_approach = False

        # Clear any existing path
        self.path = []

        # Create a direct path to the target
        self.path.append((x, y))

    def update(self):
        if not self.moving or not self.path:
            # Apply friction when not actively moving to a target
            self.vel_x *= PLAYER_FRICTION
            self.vel_y *= PLAYER_FRICTION

            # If velocity is very small, just stop
            if abs(self.vel_x) < 0.1:
                self.vel_x = 0
            if abs(self.vel_y) < 0.1:
                self.vel_y = 0

            # Update position with remaining velocity
            self.x += self.vel_x
            self.y += self.vel_y

            # Keep player within window boundaries
            self.constrain_to_boundaries()
            return

        # Get the next target point
        target_x, target_y = self.path[0]

        # Calculate direction vector to target
        dx = target_x - self.x
        dy = target_y - self.y

        # Calculate distance to target
        distance = math.sqrt(dx * dx + dy * dy)

        # If we're close enough to the target, remove it from the path
        if distance < 1:  # Smaller threshold for arrival
            self.x = target_x
            self.y = target_y
            self.vel_x = 0  # Stop completely at target
            self.vel_y = 0
            self.path.pop(0)
            self.final_approach = False

            # If no more points in the path, stop moving
            if not self.path:
                self.moving = False
                return
            return

        # Normalize direction vector for smooth movement in any direction
        dx /= distance
        dy /= distance

        # Check for direction change
        dot_with_prev = dx * self.prev_dx + dy * self.prev_dy
        if dot_with_prev < 0.7:  # Direction changed significantly
            self.direction_change_timer = (
                10  # Apply extra momentum reduction for 10 frames
            )
            self.final_approach = (
                False  # Reset final approach on significant direction change
            )

        if self.direction_change_timer > 0:
            self.direction_change_timer -= 1

        # Store current direction for next frame
        self.prev_dx = dx
        self.prev_dy = dy

        # Calculate current velocity magnitude
        vel_length = math.sqrt(self.vel_x * self.vel_x + self.vel_y * self.vel_y)

        # Check if we're in final approach mode
        if distance < FINAL_APPROACH_DISTANCE:
            self.final_approach = True

        # Handle final approach differently for smoother stopping
        if self.final_approach:
            # Calculate ideal velocity for smooth stopping
            # Use a curve that gradually reduces to zero as we approach the target
            stop_factor = distance / FINAL_APPROACH_DISTANCE
            ideal_speed = MIN_VELOCITY * stop_factor

            # Calculate how much we're moving in the target direction
            if vel_length > 0:
                vel_norm_x = self.vel_x / vel_length
                vel_norm_y = self.vel_y / vel_length
                dot_product = dx * vel_norm_x + dy * vel_norm_y

                # If we're moving away from the target, apply stronger correction
                if dot_product < 0.7:
                    # Stronger correction to align with target direction
                    self.vel_x = self.vel_x * 0.5 + dx * ideal_speed * 0.5
                    self.vel_y = self.vel_y * 0.5 + dy * ideal_speed * 0.5
                else:
                    # Gradually adjust velocity to match ideal speed and direction
                    target_vel_x = dx * ideal_speed
                    target_vel_y = dy * ideal_speed

                    # Blend current velocity with target velocity
                    blend_factor = 0.2  # Higher values = faster adjustment
                    self.vel_x = (
                        self.vel_x * (1 - blend_factor) + target_vel_x * blend_factor
                    )
                    self.vel_y = (
                        self.vel_y * (1 - blend_factor) + target_vel_y * blend_factor
                    )
        else:
            # Normal movement (not final approach)
            # Calculate slowdown factor based on distance to target
            slowdown_factor = 1.0
            if distance < SLOWDOWN_DISTANCE:
                # Use a smoother curve for deceleration
                # Linear blend between MIN_VELOCITY and MAX_VELOCITY based on distance
                target_speed = MIN_VELOCITY + (MAX_VELOCITY - MIN_VELOCITY) * (
                    distance / SLOWDOWN_DISTANCE
                )

                # Only slow down if we're going faster than the target speed
                if vel_length > target_speed:
                    # Calculate how much we need to slow down
                    slowdown_factor = target_speed / vel_length
                    # Apply the slowdown to current velocity
                    self.vel_x *= 0.9 + (
                        slowdown_factor * 0.1
                    )  # Blend between current and target
                    self.vel_y *= 0.9 + (slowdown_factor * 0.1)

                # If we're moving away from or perpendicular to the target, apply correction
                if vel_length > 0:
                    vel_norm_x = self.vel_x / vel_length
                    vel_norm_y = self.vel_y / vel_length
                    dot_product = dx * vel_norm_x + dy * vel_norm_y

                    if dot_product < 0.7 and distance < 30:
                        # Stronger correction to prevent orbiting, more aggressive as we get closer
                        correction_strength = (
                            0.5 + (1.0 - distance / 30) * 0.3
                        )  # 0.5 to 0.8
                        self.vel_x = (
                            self.vel_x * (1 - correction_strength)
                            + dx * PLAYER_ACCELERATION * 2 * correction_strength
                        )
                        self.vel_y = (
                            self.vel_y * (1 - correction_strength)
                            + dy * PLAYER_ACCELERATION * 2 * correction_strength
                        )

            # Reduce momentum (velocity) as we get closer to the target
            if distance < MOMENTUM_REDUCTION_DISTANCE:
                # Calculate momentum reduction factor - stronger as we get closer
                # But ensure we don't slow down too much
                momentum_factor = MIN_VELOCITY / MAX_VELOCITY + (
                    1 - MIN_VELOCITY / MAX_VELOCITY
                ) * (distance / MOMENTUM_REDUCTION_DISTANCE)

                # Apply stronger momentum reduction if we've recently changed direction
                if self.direction_change_timer > 0:
                    momentum_factor = max(
                        momentum_factor * 0.7, MIN_VELOCITY / MAX_VELOCITY
                    )

                # If we're very close, align velocity more with the direction to target
                if distance < 20 and vel_length > 0:
                    # Calculate the perpendicular component of velocity
                    # (the part that would cause orbiting)
                    dot = self.vel_x * dx + self.vel_y * dy
                    perp_x = self.vel_x - (dx * dot)
                    perp_y = self.vel_y - (dy * dot)

                    # Reduce the perpendicular component more aggressively
                    perp_reduction = 0.7 * (1.0 - distance / 20)
                    self.vel_x -= perp_x * perp_reduction
                    self.vel_y -= perp_y * perp_reduction

                    # Ensure we maintain minimum velocity towards target
                    new_vel_length = math.sqrt(
                        self.vel_x * self.vel_x + self.vel_y * self.vel_y
                    )
                    if new_vel_length < MIN_VELOCITY and not self.final_approach:
                        # Boost velocity to minimum if it's too low
                        scale = MIN_VELOCITY / max(new_vel_length, 0.1)
                        self.vel_x *= scale
                        self.vel_y *= scale

            # Apply acceleration in the direction of the target
            # Use a higher acceleration when we're below minimum velocity
            accel_boost = 1.0
            if vel_length < MIN_VELOCITY and not self.final_approach:
                accel_boost = 2.0  # Boost acceleration when moving too slowly

            self.vel_x += dx * PLAYER_ACCELERATION * slowdown_factor * accel_boost
            self.vel_y += dy * PLAYER_ACCELERATION * slowdown_factor * accel_boost

            # Limit maximum velocity
            vel_length = math.sqrt(self.vel_x * self.vel_x + self.vel_y * self.vel_y)
            if vel_length > MAX_VELOCITY:
                self.vel_x = (self.vel_x / vel_length) * MAX_VELOCITY
                self.vel_y = (self.vel_y / vel_length) * MAX_VELOCITY

        # Update position with velocity
        self.x += self.vel_x
        self.y += self.vel_y

        # Keep player within window boundaries
        self.constrain_to_boundaries()

    def constrain_to_boundaries(self):
        # Keep player within window boundaries
        if self.x < self.radius:
            self.x = self.radius
            self.vel_x *= -0.5  # Bounce off wall with reduced velocity
        elif self.x > WIDTH - self.radius:
            self.x = WIDTH - self.radius
            self.vel_x *= -0.5  # Bounce off wall with reduced velocity

        if self.y < self.radius:
            self.y = self.radius
            self.vel_y *= -0.5  # Bounce off wall with reduced velocity
        elif self.y > HEIGHT - self.radius:
            self.y = HEIGHT - self.radius
            self.vel_y *= -0.5  # Bounce off wall with reduced velocity

    def draw(self, screen):
        # Draw player
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)

        # Draw velocity vector (optional, for debugging)
        vel_scale = 5  # Scale factor to make velocity vector visible
        pygame.draw.line(
            screen,
            (0, 0, 255),
            (int(self.x), int(self.y)),
            (
                int(self.x + self.vel_x * vel_scale),
                int(self.y + self.vel_y * vel_scale),
            ),
            2,
        )

        # Draw target indicator if moving
        if self.moving and self.path:
            for target_x, target_y in self.path:
                # Only draw if target is within screen bounds
                if 0 <= target_x <= WIDTH and 0 <= target_y <= HEIGHT:
                    # Draw a small red circle at the target position
                    pygame.draw.circle(screen, RED, (int(target_x), int(target_y)), 5)

                    # Draw the slowdown radius (for debugging)
                    pygame.draw.circle(
                        screen,
                        (255, 200, 200),
                        (int(target_x), int(target_y)),
                        SLOWDOWN_DISTANCE,
                        1,
                    )

                    # Draw momentum reduction radius
                    pygame.draw.circle(
                        screen,
                        (200, 200, 255),
                        (int(target_x), int(target_y)),
                        MOMENTUM_REDUCTION_DISTANCE,
                        1,
                    )

                    # Draw final approach radius
                    pygame.draw.circle(
                        screen,
                        (100, 255, 100),
                        (int(target_x), int(target_y)),
                        FINAL_APPROACH_DISTANCE,
                        1,
                    )

            # Draw a line from player to the first target in the path
            if self.path:
                first_target_x, first_target_y = self.path[0]

                if 0 <= first_target_x <= WIDTH and 0 <= first_target_y <= HEIGHT:
                    # Use a different color if in final approach mode
                    line_color = (0, 200, 0) if self.final_approach else RED
                    pygame.draw.line(
                        screen,
                        line_color,
                        (int(self.x), int(self.y)),
                        (int(first_target_x), int(first_target_y)),
                        2,
                    )


# Create player in the center of the screen
player = Player(WIDTH // 2, HEIGHT // 2, PLAYER_RADIUS)

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Get mouse position (already in screen coordinates)
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Set player target
                player.set_target(mouse_x, mouse_y)

    # Update player position
    player.update()

    # Clear the screen
    screen.fill(WHITE)

    # Draw a grid to make movement more visible
    for x in range(0, WIDTH, 50):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 50):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y), 1)

    # Draw the player
    player.draw(screen)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()
