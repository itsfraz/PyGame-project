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
        self.bullet_count = BULLETS_PER_SHOT

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

    def shoot(self, current_time, bullet_group, create_bullet_callback, target_pos=None):
        if current_time - self.last_shot_time >= SHOOT_COOLDOWN:
            self.last_shot_time = current_time
            
            base_direction = None
            if target_pos:
                base_direction = pygame.math.Vector2(target_pos) - pygame.math.Vector2(self.rect.center)
            else:
                base_direction = pygame.math.Vector2(0, -1)
                
            if base_direction.length() > 0:
                base_direction = base_direction.normalize()
                
            # Spread shot logic
            if self.bullet_count > 1:
                start_angle = -((self.bullet_count - 1) * SPREAD_ANGLE) / 2
                for i in range(self.bullet_count):
                    angle = start_angle + (i * SPREAD_ANGLE)
                    # Vector2.rotate uses degrees
                    new_dir = base_direction.rotate(angle)
                    create_bullet_callback(self.rect.centerx, self.rect.centery, new_dir)
            else:
                create_bullet_callback(self.rect.centerx, self.rect.centery, base_direction)
                
            return True
        return False
