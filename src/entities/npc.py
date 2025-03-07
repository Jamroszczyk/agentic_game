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
    BEHAVIOR_TALKING = 4  # New behavior for when NPCs are talking

    # Conversation states
    CONVERSATION_NONE = 0
    CONVERSATION_GREETING = 1
    CONVERSATION_RESPONSE = 2
    CONVERSATION_FINISHED = 3

    # Class variable to track NPC groups
    groups = {}  # Dictionary to track groups: {leader_id: [follower_ids]}
    conversations = {}  # Dictionary to track conversations: {leader_id: (state, timer)}

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
        self.id = id(self)  # Unique identifier for this NPC

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

        # Conversation properties
        self.speech_bubble = None
        self.speech_timer = 0
        self.conversation_partner = None

    def set_behavior(self, behavior, target_entity=None):
        """Set the NPC's behavior and optionally a target entity"""
        old_behavior = self.behavior
        old_target = self.target_entity

        # Update behavior and target
        self.behavior = behavior
        self.target_entity = target_entity

        # Update group tracking
        if behavior == self.BEHAVIOR_FOLLOW and target_entity:
            # If this NPC is starting to follow another NPC
            if hasattr(target_entity, "id"):
                # Add this NPC as a follower of the target
                if target_entity.id not in self.groups:
                    self.groups[target_entity.id] = []

                # Only add if not already in the group
                if self.id not in self.groups[target_entity.id]:
                    self.groups[target_entity.id].append(self.id)

                    # Start a conversation when a new group forms
                    if target_entity.id not in self.conversations:
                        # Set both NPCs to talking behavior
                        self.behavior = self.BEHAVIOR_TALKING
                        self.conversation_partner = target_entity

                        if hasattr(target_entity, "set_talking"):
                            target_entity.set_talking(self)

                        # Start conversation with greeting
                        self.conversations[target_entity.id] = (
                            self.CONVERSATION_GREETING,
                            30,
                        )  # Start with greeting, shorter delay

        # If the NPC was previously following someone, remove from that group
        if (
            old_behavior == self.BEHAVIOR_FOLLOW
            and old_target
            and hasattr(old_target, "id")
        ):
            if old_target.id in self.groups and self.id in self.groups[old_target.id]:
                self.groups[old_target.id].remove(self.id)

                # Clean up empty groups
                if not self.groups[old_target.id]:
                    del self.groups[old_target.id]

                # Clean up conversation if group is disbanded
                if old_target.id in self.conversations:
                    del self.conversations[old_target.id]

    def set_talking(self, partner):
        """Set this NPC to talking behavior with a partner"""
        self.behavior = self.BEHAVIOR_TALKING
        self.conversation_partner = partner
        # Stop wandering
        self.wander_target_x = None
        self.wander_target_y = None

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
        elif self.behavior == self.BEHAVIOR_TALKING:
            self._talking_behavior()

        # Check for nearby entities if we're wandering
        if entities and self.behavior == self.BEHAVIOR_WANDER:
            self._detect_entities(entities)

        # Update conversations
        self._update_conversations()

        # Update speech bubble timer
        if self.speech_timer > 0:
            self.speech_timer -= 1
            if self.speech_timer <= 0:
                self.speech_bubble = None

        # Use the base entity update for physics
        super().update(delta_time)

    def _talking_behavior(self):
        """Behavior when talking to another NPC"""
        # Stand still and face the conversation partner
        if self.conversation_partner:
            # Face the partner
            dx = self.conversation_partner.x - self.x
            dy = self.conversation_partner.y - self.y
            distance = math.sqrt(dx * dx + dy * dy)

            # If too far from partner, move closer
            if distance > self.follow_distance:
                # Use the base entity's move_towards method
                self.move_towards(
                    self.conversation_partner.x,
                    self.conversation_partner.y,
                    self.acceleration,
                )
            # If too close, back off a bit
            elif distance < self.follow_distance * 0.8:
                # Normalize direction (away from target)
                if distance > 0:
                    dx /= distance
                    dy /= distance

                    # Apply acceleration away from the target
                    self.apply_force(-dx * self.acceleration, -dy * self.acceleration)
            else:
                # Just stand still
                self.vel_x *= 0.8  # Apply extra friction to stop faster
                self.vel_y *= 0.8

    def _update_conversations(self):
        """Update conversation states for groups this NPC is part of"""
        # If this NPC is a leader with followers
        if (
            self.id in self.groups
            and self.groups[self.id]
            and self.id in self.conversations
        ):
            state, timer = self.conversations[self.id]

            # Decrement timer
            timer -= 1

            # Handle conversation state transitions
            if timer <= 0:
                if state == self.CONVERSATION_GREETING:
                    # Leader says "Hi"
                    self.say("Hi", 90)
                    # Move to response state
                    state = self.CONVERSATION_RESPONSE
                    timer = 60  # Wait 1 second before response
                elif state == self.CONVERSATION_RESPONSE:
                    # Find the follower
                    if self.groups[self.id]:
                        follower_id = self.groups[self.id][0]
                        # Find the follower entity
                        for entity in self.groups.get("all_entities", []):
                            if hasattr(entity, "id") and entity.id == follower_id:
                                # Follower says "Hello"
                                entity.say("Hello", 90)
                                break

                    # Move to finished state
                    state = self.CONVERSATION_FINISHED
                    timer = 90  # Keep conversation record for 1.5 seconds
                elif state == self.CONVERSATION_FINISHED:
                    # End the conversation
                    del self.conversations[self.id]

                    # Return to normal behavior
                    if self.behavior == self.BEHAVIOR_TALKING:
                        self.behavior = self.BEHAVIOR_WANDER
                        self.conversation_partner = None

                        # Also return the follower to normal behavior
                        if self.groups[self.id]:
                            follower_id = self.groups[self.id][0]
                            for entity in self.groups.get("all_entities", []):
                                if hasattr(entity, "id") and entity.id == follower_id:
                                    if entity.behavior == entity.BEHAVIOR_TALKING:
                                        entity.behavior = entity.BEHAVIOR_FOLLOW
                                        entity.conversation_partner = None
                                    break
                    return

            # Update conversation state
            self.conversations[self.id] = (state, timer)

        # Check if this NPC is a follower in a conversation
        if (
            self.behavior == self.BEHAVIOR_TALKING
            and self.conversation_partner
            and hasattr(self.conversation_partner, "id")
        ):
            leader_id = self.conversation_partner.id
            if leader_id in self.conversations:
                state, timer = self.conversations[leader_id]
                if state == self.CONVERSATION_RESPONSE and timer <= 0:
                    # This is a follower that needs to respond
                    self.say("Hello", 90)

    def say(self, text, duration=60):
        """Display a speech bubble with text for a duration"""
        self.speech_bubble = text
        self.speech_timer = duration

    def _idle_behavior(self):
        """Stand still"""
        # Just apply friction, no new forces
        pass

    def _wander_behavior(self):
        """Wander around randomly"""
        # If we have followers, don't wander too far
        if self.id in self.groups and self.groups[self.id]:
            # Stand still or move very little
            if random.random() < 0.95:  # 95% chance to just stand still
                return

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
        # Store all entities for conversation handling
        if "all_entities" not in self.groups:
            self.groups["all_entities"] = entities

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
                # If it's another NPC, consider following
                elif (
                    isinstance(entity, NPC) and random.random() < 0.1
                ):  # Increased chance to start following (10%)
                    # Check if the other NPC is already being followed
                    if hasattr(entity, "id"):
                        # If the other NPC already has a follower, don't follow
                        if (
                            entity.id in self.groups
                            and len(self.groups[entity.id]) >= 1
                        ):
                            continue

                        # If the other NPC is following someone who already has a follower, don't follow
                        if entity.behavior == self.BEHAVIOR_FOLLOW and hasattr(
                            entity.target_entity, "id"
                        ):
                            target_id = entity.target_entity.id
                            if (
                                target_id in self.groups
                                and len(self.groups[target_id]) >= 1
                            ):
                                continue

                    # If we get here, it's safe to follow
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

        # Draw a line to the entity being followed or conversation partner
        if (
            self.behavior == self.BEHAVIOR_FOLLOW
            or self.behavior == self.BEHAVIOR_TALKING
        ) and self.target_entity:
            target_screen_x = int(self.target_entity.x - camera_offset[0])
            target_screen_y = int(self.target_entity.y - camera_offset[1])

            screen_width, screen_height = pygame.display.get_surface().get_size()
            if (
                0 <= target_screen_x <= screen_width
                and 0 <= target_screen_y <= screen_height
            ):
                # Use green for following, blue for talking
                line_color = (
                    (0, 0, 255)
                    if self.behavior == self.BEHAVIOR_TALKING
                    else (0, 255, 0)
                )
                pygame.draw.line(
                    screen,
                    line_color,
                    (screen_x, screen_y),
                    (target_screen_x, target_screen_y),
                    1,
                )

        # Draw speech bubble if active
        if self.speech_bubble:
            self._draw_speech_bubble(screen, camera_offset)

    def _draw_speech_bubble(self, screen, camera_offset):
        """Draw a speech bubble with text"""
        # Get screen position
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])

        # Create font if not already created
        font = pygame.font.SysFont("Arial", 14)

        # Render text
        text_surface = font.render(self.speech_bubble, True, (50, 50, 50))
        text_rect = text_surface.get_rect()

        # Calculate bubble dimensions
        padding = 10
        bubble_width = text_rect.width + padding * 2
        bubble_height = text_rect.height + padding * 2

        # Calculate bubble position (above the NPC)
        bubble_x = screen_x - bubble_width // 2
        bubble_y = screen_y - self.radius - bubble_height - 5

        # Draw bubble background
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (bubble_x, bubble_y, bubble_width, bubble_height),
            border_radius=10,
        )

        # Draw bubble border
        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (bubble_x, bubble_y, bubble_width, bubble_height),
            width=2,
            border_radius=10,
        )

        # Draw text
        screen.blit(text_surface, (bubble_x + padding, bubble_y + padding))

        # Draw little triangle pointing to the NPC
        pygame.draw.polygon(
            screen,
            (255, 255, 255),
            [
                (screen_x, screen_y - self.radius),
                (screen_x - 5, bubble_y + bubble_height),
                (screen_x + 5, bubble_y + bubble_height),
            ],
        )

        # Draw triangle border
        pygame.draw.polygon(
            screen,
            (0, 0, 0),
            [
                (screen_x, screen_y - self.radius),
                (screen_x - 5, bubble_y + bubble_height),
                (screen_x + 5, bubble_y + bubble_height),
            ],
            width=2,
        )
