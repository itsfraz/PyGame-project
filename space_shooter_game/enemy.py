import pygame
import random
import os
from settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, score_factor=0):
        super().__init__()
        try:
            image_path = os.path.join(IMAGE_DIR, "enemy.png")
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (ENEMY_WIDTH, ENEMY_HEIGHT))
        except (FileNotFoundError, pygame.error):
            self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
            self.image.fill(RED)
            
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - ENEMY_WIDTH)
        self.rect.y = random.randrange(-100, -40)
        
        # Speed increases slightly with score/difficulty
        speed_multiplier = 1 + (score_factor * 0.01)
        self.speed = random.randrange(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX + 1) * speed_multiplier

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT + 10:
            self.kill()
