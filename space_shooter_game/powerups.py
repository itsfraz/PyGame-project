import pygame
import random
import os
from settings import *

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.type = random.choice(list(POWERUP_COLORS.keys()))
        self.image = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE))
        self.image.fill(POWERUP_COLORS[self.type])
        
        # Add a letter identifier
        try:
            font = pygame.font.SysFont('arial', 20, bold=True)
        except:
             font = pygame.font.Font(None, 20)
        text = str(self.type[0]).upper()
        text_surf = font.render(text, True, (0,0,0))
        text_rect = text_surf.get_rect(center=(POWERUP_SIZE//2, POWERUP_SIZE//2))
        self.image.blit(text_surf, text_rect)

        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speed = POWERUP_SPEED

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
