import math
import pygame


class Entity:
    """Base class for all game entities (player, NPCs, etc.)"""

    def __init__(
        self, x, y, radius, color=(0, 0, 0), speed=0, max_velocity=0, friction=0.9
    ):
        """Initialize the entity with position, size, appearance, and movement properties"""
        # Position and appearance
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

        # Movement properties
        self.vel_x = 0
        self.vel_y = 0
        self.speed = speed
        self.max_velocity = max_velocity
        self.friction = friction

        # Entity state
        self.active = True
        self.visible = True
        self.collidable = True

    def update(self, delta_time=1.0):
        """Update entity state (to be overridden by subclasses)"""
        # Apply friction
        self.vel_x *= self.friction
        self.vel_y *= self.friction

        # If velocity is very small, just stop
        if abs(self.vel_x) < 0.1:
            self.vel_x = 0
        if abs(self.vel_y) < 0.1:
            self.vel_y = 0

        # Limit maximum velocity
        vel_length = math.sqrt(self.vel_x * self.vel_x + self.vel_y * self.vel_y)
        if vel_length > self.max_velocity and self.max_velocity > 0:
            self.vel_x = (self.vel_x / vel_length) * self.max_velocity
            self.vel_y = (self.vel_y / vel_length) * self.max_velocity

        # Basic movement with velocity
        self.x += self.vel_x * delta_time
        self.y += self.vel_y * delta_time

    def draw(self, screen, camera_offset=(0, 0)):
        """Draw the entity on the screen"""
        if not self.visible:
            return

        # Calculate screen position (with camera offset)
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])

        # Draw the entity as a circle
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.radius)

    def constrain_to_boundaries(self, min_x, min_y, max_x, max_y, bounce_factor=0.5):
        """Keep entity within specified boundaries"""
        if self.x < min_x + self.radius:
            self.x = min_x + self.radius
            self.vel_x *= -bounce_factor  # Bounce off wall with reduced velocity
        elif self.x > max_x - self.radius:
            self.x = max_x - self.radius
            self.vel_x *= -bounce_factor  # Bounce off wall with reduced velocity

        if self.y < min_y + self.radius:
            self.y = min_y + self.radius
            self.vel_y *= -bounce_factor  # Bounce off wall with reduced velocity
        elif self.y > max_y - self.radius:
            self.y = max_y - self.radius
            self.vel_y *= -bounce_factor  # Bounce off wall with reduced velocity

    def apply_force(self, force_x, force_y):
        """Apply a force to the entity, changing its velocity"""
        self.vel_x += force_x
        self.vel_y += force_y

    def move_towards(self, target_x, target_y, acceleration):
        """Move the entity towards a target position"""
        # Calculate direction to target
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        # If we're already at the target, do nothing
        if distance < 1:
            return True

        # Normalize direction
        dx /= distance
        dy /= distance

        # Apply acceleration in the direction of the target
        self.vel_x += dx * acceleration
        self.vel_y += dy * acceleration

        return False  # Not at target yet

    def distance_to(self, other_entity):
        """Calculate distance to another entity"""
        dx = other_entity.x - self.x
        dy = other_entity.y - self.y
        return math.sqrt(dx * dx + dy * dy)

    def direction_to(self, other_entity):
        """Calculate normalized direction vector to another entity"""
        dx = other_entity.x - self.x
        dy = other_entity.y - self.y
        distance = self.distance_to(other_entity)

        if distance == 0:
            return (0, 0)

        return (dx / distance, dy / distance)

    def is_colliding_with(self, other_entity):
        """Check if this entity is colliding with another entity"""
        if not self.collidable or not other_entity.collidable:
            return False

        distance = self.distance_to(other_entity)
        return distance < (self.radius + other_entity.radius)
