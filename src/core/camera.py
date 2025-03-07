class Camera:
    """Camera class for handling viewport and scrolling"""

    def __init__(self, width, height, world_width, world_height):
        """Initialize the camera with viewport and world dimensions"""
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.world_width = world_width
        self.world_height = world_height
        self.target = None
        self.is_fixed = False

    def set_target(self, target):
        """Set the entity for the camera to follow"""
        self.target = target

    def set_fixed(self, is_fixed):
        """Set whether the camera is fixed or follows the target"""
        self.is_fixed = is_fixed

    def update(self):
        """Update camera position to follow target"""
        if self.is_fixed or not self.target:
            return

        # Center the camera on the target
        self.x = self.target.x - self.width // 2
        self.y = self.target.y - self.height // 2

        # Keep the camera within the world boundaries
        self.constrain_to_world()

    def constrain_to_world(self):
        """Keep the camera within the world boundaries"""
        self.x = max(0, min(self.x, self.world_width - self.width))
        self.y = max(0, min(self.y, self.world_height - self.height))

    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates"""
        screen_x = world_x - self.x
        screen_y = world_y - self.y
        return screen_x, screen_y

    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        world_x = screen_x + self.x
        world_y = screen_y + self.y
        return world_x, world_y

    def is_visible(self, entity):
        """Check if an entity is visible in the camera's viewport"""
        # Get entity bounds
        left = entity.x - entity.radius
        right = entity.x + entity.radius
        top = entity.y - entity.radius
        bottom = entity.y + entity.radius

        # Check if entity is within camera bounds
        return (
            right >= self.x
            and left <= self.x + self.width
            and bottom >= self.y
            and top <= self.y + self.height
        )
