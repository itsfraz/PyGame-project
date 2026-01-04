import pygame
import os
from settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            image_path = os.path.join(IMAGE_DIR, "bullet.png")
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (BULLET_WIDTH, BULLET_HEIGHT))
        except (FileNotFoundError, pygame.error):
            self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
            self.image.fill(BULLET_COLOR)
            
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = BULLET_SPEED

    def update(self):
        self.rect.y -= self.speed
        # Kill if off screen
        if self.rect.bottom < 0:
            self.kill()
