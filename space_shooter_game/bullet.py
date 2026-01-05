import pygame
import os
from settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=None):
        super().__init__()
        try:
            image_path = os.path.join(IMAGE_DIR, "bullet.png")
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (BULLET_WIDTH, BULLET_HEIGHT))
        except (FileNotFoundError, pygame.error):
            self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT))
            self.image.fill(BULLET_COLOR)
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pos = pygame.math.Vector2(x, y)
        self.speed = BULLET_SPEED
        
        if direction:
            # Normalize direction
            if direction.length() > 0:
                direction = direction.normalize()
            self.velocity = direction * self.speed
            
            # Rotate image to align with direction
            # Original image points up (0, -1). 
            # We calculate angle between (0, -1) and our direction.
            # angle_to returns signed angle in degrees.
            up = pygame.math.Vector2(0, -1)
            angle = direction.angle_to(up)
            self.image = pygame.transform.rotate(self.image, angle)
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            self.velocity = pygame.math.Vector2(0, -self.speed)

    def update(self):
        self.pos += self.velocity
        self.rect.center = self.pos
        
        # Kill if off screen (any direction)
        if (self.rect.bottom < 0 or 
            self.rect.top > SCREEN_HEIGHT or 
            self.rect.right < 0 or 
            self.rect.left > SCREEN_WIDTH):
            self.kill()
