from enum import Enum

class GameState(Enum):
    ONGOING = 0
    PLAYER_WIN = 1
    AI_WIN = 2
    DRAW = 3

class PowerUpType(Enum):
    NONE = 0
    BLOCK = 1  # Block a cell from being used by opponent
    SWAP = 2   # Swap two pieces on the board
    WILDCARD = 3  # Place your symbol in any free spot

class AIPersonality(Enum):
    BALANCED = 0   # Standard min-max with alpha-beta
    AGGRESSIVE = 1 # Prioritizes attacking positions
    DEFENSIVE = 2  # Prioritizes blocking player wins
    RANDOM = 3     # Occasionally makes non-optimal moves
    LEARNING = 4   # Adapts strategy based on player's moves