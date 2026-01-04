# Galactic Defender - Space Shooter Game

## Project Overview

This project is a 2D arcade-style Space Shooter game built using Python and the Pygame library. The player controls a spaceship to defend against waves of alien enemies. The game demonstrates core game development concepts such as the game loop, event handling, collision detection, and object-oriented programming.

## Features

- **Player Movement**: Smooth left/right movement using keyboard controls.
- **Shooting Mechanism**: Fire bullets to destroy enemies.
- **Enemy Spawning**: Enemies spawn randomly and move downwards.
- **Scoring System**: Score increases for every enemy destroyed.
- **Lives System**: Player has 3 lives; game ends when logic is depleted.
- **Sound Effects**: Shoot, explosion, and background music.
- **Visuals**: Animated scrolling background and sprite-based graphics.

## Project Structure

```
space_shooter_game/
│── main.py          # Entry point, game loop, state management
│── player.py        # Player class logic
│── enemy.py         # Enemy spawn and movement logic
│── bullet.py        # Bullet mechanics
│── settings.py      # Constants (Screen size, colors, speeds)
│── assets/          # Images and Sounds
```

## Game Logic Explanation

1.  **Initialization**: Pygame is initialized, screen and clock are set up. Assets calls are made to load images/sounds.
2.  **Game Loop**: The core `while` loop runs continuously to:
    - **Process Events**: Check for Quit, Keypresses (Movement, Shooting).
    - **Update**: Move all sprites (Player, Enemies, Bullets) and check for collisions.
    - **Draw**: Render the background, sprites, and UI text to the screen.
3.  **State Management**: `MENU` -> `PLAYING` -> `GAMEOVER`.

## Collision Detection

We use Pygame's built-in collision functions:

- `pygame.sprite.groupcollide(mobs, bullets, True, True)`: Checks if any enemy overlaps with any bullet. Both are removed (`True, True` arguments).
- `pygame.sprite.spritecollide(player, mobs, True)`: Checks if any enemy overlaps with the player. The enemy is removed.

## Step Breakdown (Flowchart Logic)

1.  **Start**: Run `main.py`.
2.  **Menu**: Display Title. specific Wait for 'Space' key.
3.  **Play**:
    - Spawn enemies at intervals.
    - Player inputs moves ship.
    - Spacebar creates Bullet.
    - Bullet hits Enemy -> Score +10, Explosion.
    - Enemy hits Player -> Lives -1.
    - If Lives <= 0 -> Game Over.
4.  **Game Over**: Show Score. Wait for 'R' to Restart or 'ESC' to Quit.

## Future Enhancements

- **Power-ups**: Double shot, shield, speed boost.
- **Boss Fight**: A large enemy after a certain score.
- **High Score**: Save to file.
- **Levels**: Increasing difficulty/speed over time.

## Viva-Ready Questions & Answers

- **Q: What is `flips()` vs `update()`?**
  - A: `flip()` updates the entire screen, while `update()` can update specific portions. In this game, we use `flip()` for simplicity.
- **Q: How does the game loop work?**
  - A: It's a `while running:` loop that ensures the game processes input, updates game state, and renders to the screen 60 times a second (FPS).
- **Q: Why use Classes (OOP)?**
  - A: It allows us to create multiple instances of Enemies and Bullets easily, each managing its own position and state.
- **Q: How is frame rate controlled?**
  - A: `clock.tick(FPS)` ensures the loop doesn't run faster than 60 times per second.

## Controls

- **Arrow Keys / WASD**: Move.
- **Space**: Shoot.
- **P**: Pause.
- **R**: Restart (on Game Over).
- **ESC**: Quit.
