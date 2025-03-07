import math
import pygame
from src.entities.entity import Entity
from src.core.constants import (
    PLAYER_SPEED,
    PLAYER_ACCELERATION,
    PLAYER_FRICTION,
    PLAYER_MAX_VELOCITY,
    PLAYER_MIN_VELOCITY,
    FINAL_APPROACH_DISTANCE,
    SLOWDOWN_DISTANCE,
    MOMENTUM_REDUCTION_DISTANCE,
)


class Player(Entity):
    """Player class with smooth movement and momentum physics"""

    def __init__(self, x, y, radius, color=(0, 0, 0)):
        # Initialize the base entity with player-specific properties
        super().__init__(
            x,
            y,
            radius,
            color,
            speed=PLAYER_SPEED,
            max_velocity=PLAYER_MAX_VELOCITY,
            friction=PLAYER_FRICTION,
        )

        # Player-specific properties
        self.is_player = True
        self.min_velocity = PLAYER_MIN_VELOCITY
        self.acceleration = PLAYER_ACCELERATION

        # Target and path
        self.target_x = None
        self.target_y = None
        self.moving = False
        self.path = []

        # Movement state tracking
        self.prev_dx = 0
        self.prev_dy = 0
        self.direction_change_timer = 0
        self.final_approach = False

        # Constants for movement behavior
        self.FINAL_APPROACH_DISTANCE = FINAL_APPROACH_DISTANCE
        self.SLOWDOWN_DISTANCE = SLOWDOWN_DISTANCE
        self.MOMENTUM_REDUCTION_DISTANCE = MOMENTUM_REDUCTION_DISTANCE

    def set_target(self, x, y):
        """Set a target position for the player to move towards"""
        self.target_x = x
        self.target_y = y
        self.moving = True
        self.final_approach = False

        # Clear any existing path
        self.path = []

        # Create a direct path to the target
        self.path.append((x, y))

    def update(self, delta_time=1.0, entities=None):
        """Update player position and velocity based on physics"""
        if not self.moving or not self.path:
            # Use the base entity update for basic physics when not moving to a target
            super().update(delta_time)
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
        if distance < self.FINAL_APPROACH_DISTANCE:
            self.final_approach = True

        # Handle final approach differently for smoother stopping
        if self.final_approach:
            # Calculate ideal velocity for smooth stopping
            # Use a curve that gradually reduces to zero as we approach the target
            stop_factor = distance / self.FINAL_APPROACH_DISTANCE
            ideal_speed = self.min_velocity * stop_factor

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
            if distance < self.SLOWDOWN_DISTANCE:
                # Use a smoother curve for deceleration
                # Linear blend between MIN_VELOCITY and MAX_VELOCITY based on distance
                target_speed = self.min_velocity + (
                    self.max_velocity - self.min_velocity
                ) * (distance / self.SLOWDOWN_DISTANCE)

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
                            + dx * self.acceleration * 2 * correction_strength
                        )
                        self.vel_y = (
                            self.vel_y * (1 - correction_strength)
                            + dy * self.acceleration * 2 * correction_strength
                        )

            # Reduce momentum (velocity) as we get closer to the target
            if distance < self.MOMENTUM_REDUCTION_DISTANCE:
                # Calculate momentum reduction factor - stronger as we get closer
                # But ensure we don't slow down too much
                momentum_factor = self.min_velocity / self.max_velocity + (
                    1 - self.min_velocity / self.max_velocity
                ) * (distance / self.MOMENTUM_REDUCTION_DISTANCE)

                # Apply stronger momentum reduction if we've recently changed direction
                if self.direction_change_timer > 0:
                    momentum_factor = max(
                        momentum_factor * 0.7, self.min_velocity / self.max_velocity
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
                    if new_vel_length < self.min_velocity and not self.final_approach:
                        # Boost velocity to minimum if it's too low
                        scale = self.min_velocity / max(new_vel_length, 0.1)
                        self.vel_x *= scale
                        self.vel_y *= scale

            # Apply acceleration in the direction of the target
            # Use a higher acceleration when we're below minimum velocity
            accel_boost = 1.0
            if vel_length < self.min_velocity and not self.final_approach:
                accel_boost = 2.0  # Boost acceleration when moving too slowly

            self.vel_x += dx * self.acceleration * slowdown_factor * accel_boost
            self.vel_y += dy * self.acceleration * slowdown_factor * accel_boost

            # Limit maximum velocity
            vel_length = math.sqrt(self.vel_x * self.vel_x + self.vel_y * self.vel_y)
            if vel_length > self.max_velocity:
                self.vel_x = (self.vel_x / vel_length) * self.max_velocity
                self.vel_y = (self.vel_y / vel_length) * self.max_velocity

        # Update position with velocity
        self.x += self.vel_x * delta_time
        self.y += self.vel_y * delta_time

    def draw(self, screen, camera_offset=(0, 0)):
        """Draw the player and movement indicators"""
        # Draw the player
        super().draw(screen, camera_offset)

        # Draw velocity vector (optional, for debugging)
        vel_scale = 5  # Scale factor to make velocity vector visible
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        pygame.draw.line(
            screen,
            (0, 0, 255),
            (screen_x, screen_y),
            (
                int(screen_x + self.vel_x * vel_scale),
                int(screen_y + self.vel_y * vel_scale),
            ),
            2,
        )

        # Draw target indicator if moving
        if self.moving and self.path:
            for target_x, target_y in self.path:
                # Calculate screen position
                target_screen_x = int(target_x - camera_offset[0])
                target_screen_y = int(target_y - camera_offset[1])

                # Only draw if target is within screen bounds
                screen_width, screen_height = pygame.display.get_surface().get_size()
                if (
                    0 <= target_screen_x <= screen_width
                    and 0 <= target_screen_y <= screen_height
                ):
                    # Draw a small red circle at the target position
                    pygame.draw.circle(
                        screen, (255, 0, 0), (target_screen_x, target_screen_y), 5
                    )

                    # Draw the slowdown radius (for debugging)
                    pygame.draw.circle(
                        screen,
                        (255, 200, 200),
                        (target_screen_x, target_screen_y),
                        self.SLOWDOWN_DISTANCE,
                        1,
                    )

                    # Draw momentum reduction radius
                    pygame.draw.circle(
                        screen,
                        (200, 200, 255),
                        (target_screen_x, target_screen_y),
                        self.MOMENTUM_REDUCTION_DISTANCE,
                        1,
                    )

                    # Draw final approach radius
                    pygame.draw.circle(
                        screen,
                        (100, 255, 100),
                        (target_screen_x, target_screen_y),
                        self.FINAL_APPROACH_DISTANCE,
                        1,
                    )

            # Draw a line from player to the first target in the path
            if self.path:
                first_target_x, first_target_y = self.path[0]
                first_target_screen_x = int(first_target_x - camera_offset[0])
                first_target_screen_y = int(first_target_y - camera_offset[1])

                screen_width, screen_height = pygame.display.get_surface().get_size()
                if (
                    0 <= first_target_screen_x <= screen_width
                    and 0 <= first_target_screen_y <= screen_height
                ):
                    # Use a different color if in final approach mode
                    line_color = (0, 200, 0) if self.final_approach else (255, 0, 0)
                    pygame.draw.line(
                        screen,
                        line_color,
                        (screen_x, screen_y),
                        (first_target_screen_x, first_target_screen_y),
                        2,
                    )
