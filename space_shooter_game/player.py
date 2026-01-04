import pygame
import os
import random
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load image or fallback to surface
        try:
            image_path = os.path.join(IMAGE_DIR, "player.png")
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (PLAYER_WIDTH, PLAYER_HEIGHT))
        except (FileNotFoundError, pygame.error):
            self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            self.image.fill(GREEN)
        
        self.rect = self.image.get_rect()
        self.rect.midbottom = (PLAYER_START_X, PLAYER_START_Y)
        self.speed = PLAYER_SPEED
        self.last_shot_time = 0
        self.lives = PLAYER_LIVES

    def update(self, create_particle_callback=None):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Boundary checks
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # Engine Particles
        if create_particle_callback and random.random() < 0.5:
            # Emit from bottom center
            # Add some randomness to X
            offset_x = random.randint(-5, 5)
            pos = (self.rect.centerx + offset_x, self.rect.bottom - 5)
            # Vector pointing down
            vec = pygame.math.Vector2(0, 1)
            create_particle_callback(pos, CYAN, random.randint(2, 5), random.randint(2, 4), vector=vec)

    def shoot(self, current_time, bullet_group, create_bullet_callback):
        if current_time - self.last_shot_time >= SHOOT_COOLDOWN:
            self.last_shot_time = current_time
            create_bullet_callback(self.rect.centerx, self.rect.top)
            return True
        return False
