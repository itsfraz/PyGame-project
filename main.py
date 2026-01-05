import os
import sys

# Get the directory of this script's location
current_dir = os.path.dirname(os.path.abspath(__file__))
# The game code is in 'space_shooter_game'
game_dir = os.path.join(current_dir, 'space_shooter_game')

# Change the working directory to the game directory
# This ensures that assets (images/sounds) loading with relative paths works correctly
# and that local imports (like 'import settings') inside the game module work.
os.chdir(game_dir)

# Add the game dir to sys.path so we can import the module
sys.path.insert(0, game_dir)

import main

if __name__ == "__main__":
    main.main()
