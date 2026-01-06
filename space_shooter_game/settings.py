import os

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Galactic Defender"

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
DARK_BLUE = (10, 10, 35)

# Neon Palette
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 20, 147)
NEON_GREEN = (57, 255, 20)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGE_DIR = os.path.join(ASSETS_DIR, "images")
SOUND_DIR = os.path.join(ASSETS_DIR, "sounds")

# UI Settings
UI_FONT_SIZE = 24
GAME_OVER_FONT_SIZE = 64

# Player settings
PLAYER_SPEED = 6 # Slightly faster
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_START_X = SCREEN_WIDTH // 2
PLAYER_START_Y = SCREEN_HEIGHT - 80
PLAYER_LIVES = 3
PLAYER_ENGINE_OFFSET = (0, 25) # Behind the ship center

# Bullet settings
BULLET_SPEED = 10 # Faster bullets feel better
BULLET_WIDTH = 5
BULLET_HEIGHT = 15
BULLET_COLOR = NEON_GREEN
SHOOT_COOLDOWN = 200  # Faster fire rate
BULLETS_PER_SHOT = 3
SPREAD_ANGLE = 10

# Enemy settings
ENEMY_SPEED_MIN = 0.5
ENEMY_SPEED_MAX = 1.5
ENEMY_WIDTH = 45
ENEMY_HEIGHT = 45
ENEMY_SPAWN_RATE = 1500  # More intense

# Boss Settings
BOSS_SPAWN_SCORE = 5000
BOSS_HP = 100
BOSS_WIDTH = 150
BOSS_HEIGHT = 100
BOSS_COLOR = (200, 0, 200) # Purple-ish
BOSS_SPEED = 2

# VFX Settings
SCREEN_SHAKE_AMOUNT = 5
PARTICLE_DECAY = 2

# Power-up Settings
POWERUP_SPAWN_CHANCE = 0.1  # 10% chance
POWERUP_SPEED = 2
POWERUP_SIZE = 30
POWERUP_COLORS = {
    'health': (0, 255, 0),      # Green
    'shield': (0, 0, 255),      # Blue
    'rapid_fire': (255, 255, 0) # Yellow
}
POWERUP_DURATION = 5000 # 5 seconds for temporary effects
