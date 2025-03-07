import math
import random
import pygame
from src.entities.entity import Entity
from src.core.constants import (
    NPC_RADIUS,
    NPC_SPEED,
    NPC_ACCELERATION,
    NPC_FRICTION,
    NPC_MAX_VELOCITY,
    NPC_DETECTION_RADIUS,
    NPC_FOLLOW_DISTANCE,
    NPC_FLEE_DISTANCE,
)


class NPC(Entity):
    """NPC class with basic AI behavior"""

    # NPC behavior types
    BEHAVIOR_IDLE = 0
    BEHAVIOR_WANDER = 1
    BEHAVIOR_FOLLOW = 2
    BEHAVIOR_FLEE = 3

    def __init__(self, x, y, radius, color=(100, 100, 100)):
        # Initialize the base entity with NPC-specific properties
        super().__init__(
            x,
            y,
            radius,
            color,
            speed=NPC_SPEED,
            max_velocity=NPC_MAX_VELOCITY,
            friction=NPC_FRICTION,
        )

        # NPC-specific properties
        self.acceleration = NPC_ACCELERATION

        # AI properties
        self.behavior = self.BEHAVIOR_WANDER
        self.target_entity = None
        self.wander_target_x = None
        self.wander_target_y = None
        self.wander_timer = 0
        self.wander_interval = random.randint(100, 200)  # Frames between wandering
        self.detection_radius = NPC_DETECTION_RADIUS  # How far the NPC can "see"
        self.follow_distance = (
            NPC_FOLLOW_DISTANCE  # Distance to maintain when following
        )
        self.flee_distance = NPC_FLEE_DISTANCE  # Distance to maintain when fleeing

    def set_behavior(self, behavior, target_entity=None):
        """Set the NPC's behavior and optionally a target entity"""
        self.behavior = behavior
        self.target_entity = target_entity

    def update(self, delta_time=1.0, entities=None):
        """Update NPC position and behavior"""
        # Handle different behaviors
        if self.behavior == self.BEHAVIOR_IDLE:
            self._idle_behavior()
        elif self.behavior == self.BEHAVIOR_WANDER:
            self._wander_behavior()
        elif self.behavior == self.BEHAVIOR_FOLLOW and self.target_entity:
            self._follow_behavior()
        elif self.behavior == self.BEHAVIOR_FLEE and self.target_entity:
            self._flee_behavior()

        # Check for nearby entities if we're wandering
        if entities and self.behavior == self.BEHAVIOR_WANDER:
            self._detect_entities(entities)

        # Use the base entity update for physics
        super().update(delta_time)

    def _idle_behavior(self):
        """Stand still"""
        # Just apply friction, no new forces
        pass

    def _wander_behavior(self):
        """Wander around randomly"""
        # Decrement wander timer
        self.wander_timer -= 1

        # If we don't have a target or timer expired, pick a new random target
        if (
            self.wander_target_x is None
            or self.wander_target_y is None
            or self.wander_timer <= 0
        ):
            # Pick a random point within a certain radius
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(50, 150)
            self.wander_target_x = self.x + math.cos(angle) * distance
            self.wander_target_y = self.y + math.sin(angle) * distance
            self.wander_timer = self.wander_interval

        # Use the base entity's move_towards method
        if self.wander_target_x is not None and self.wander_target_y is not None:
            arrived = self.move_towards(
                self.wander_target_x, self.wander_target_y, self.acceleration
            )

            # If we've arrived at the target, clear it
            if arrived:
                self.wander_target_x = None
                self.wander_target_y = None

    def _follow_behavior(self):
        """Follow the target entity while maintaining a certain distance"""
        if not self.target_entity:
            return

        # Calculate direction to target
        dx = self.target_entity.x - self.x
        dy = self.target_entity.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        # If we're too far, move closer
        if distance > self.follow_distance:
            # Use the base entity's move_towards method
            self.move_towards(
                self.target_entity.x, self.target_entity.y, self.acceleration
            )
        # If we're too close, back off a bit
        elif distance < self.follow_distance * 0.8:
            # Normalize direction (away from target)
            dx /= distance
            dy /= distance

            # Apply acceleration away from the target
            self.apply_force(-dx * self.acceleration, -dy * self.acceleration)

    def _flee_behavior(self):
        """Run away from the target entity"""
        if not self.target_entity:
            return

        # Calculate direction to target
        dx = self.target_entity.x - self.x
        dy = self.target_entity.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        # If we're within flee distance, run away
        if distance < self.flee_distance:
            # Normalize direction
            dx /= distance
            dy /= distance

            # Apply acceleration away from the target
            self.apply_force(
                -dx * self.acceleration * 1.5, -dy * self.acceleration * 1.5
            )  # Flee faster
        # If we're far enough away, go back to wandering
        elif distance > self.flee_distance * 2:
            self.behavior = self.BEHAVIOR_WANDER
            self.target_entity = None

    def _detect_entities(self, entities):
        """Detect nearby entities and react to them"""
        for entity in entities:
            # Skip self
            if entity == self:
                continue

            # Calculate distance to entity
            distance = self.distance_to(entity)

            # If entity is within detection radius
            if distance < self.detection_radius:
                # If it's a player, flee
                if hasattr(entity, "is_player") and entity.is_player:
                    self.set_behavior(self.BEHAVIOR_FLEE, entity)
                    break
                # If it's another NPC, follow
                elif (
                    isinstance(entity, NPC) and random.random() < 0.01
                ):  # Small chance to start following
                    self.set_behavior(self.BEHAVIOR_FOLLOW, entity)
                    break

    def draw(self, screen, camera_offset=(0, 0)):
        """Draw the NPC and its behavior indicators"""
        # Draw the NPC
        super().draw(screen, camera_offset)

        # Draw detection radius (for debugging)
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        pygame.draw.circle(
            screen, (200, 200, 200), (screen_x, screen_y), self.detection_radius, 1
        )

        # Draw wander target if applicable
        if self.behavior == self.BEHAVIOR_WANDER and self.wander_target_x is not None:
            target_screen_x = int(self.wander_target_x - camera_offset[0])
            target_screen_y = int(self.wander_target_y - camera_offset[1])

            screen_width, screen_height = pygame.display.get_surface().get_size()
            if (
                0 <= target_screen_x <= screen_width
                and 0 <= target_screen_y <= screen_height
            ):
                pygame.draw.circle(
                    screen, (150, 150, 150), (target_screen_x, target_screen_y), 3
                )
                pygame.draw.line(
                    screen,
                    (150, 150, 150),
                    (screen_x, screen_y),
                    (target_screen_x, target_screen_y),
                    1,
                )
