from src.core.game import Game
from src.core.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    WORLD_WIDTH,
    WORLD_HEIGHT,
    PLAYER_RADIUS,
    NPC_COUNT,
)


def main():
    """Main function to run the game"""
    # Create the game
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT)

    # Create the player in the center of the world
    game.create_player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2, PLAYER_RADIUS)

    # Spawn some NPCs
    game.spawn_random_npcs(NPC_COUNT)

    # Run the game
    game.run()


if __name__ == "__main__":
    main()
