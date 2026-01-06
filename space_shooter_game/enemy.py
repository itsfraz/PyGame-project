import pygame
import random
import os
import math
from settings import *

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 15))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed = 4

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, score_factor=0, enemy_type=None):
        super().__init__()
        
        # Determine Type
        if enemy_type:
            self.type = enemy_type
        else:
            roll = random.random()
            if roll < 0.6: self.type = 'basic'
            elif roll < 0.8: self.type = 'shooter'
            elif roll < 0.9: self.type = 'chaser'
            else: self.type = 'tank'

        # Default Attributes
        self.hp = 1
        speed_multiplier = 1 + (score_factor * 0.005)
        base_speed = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)

        # Type Specifics
        width, height = ENEMY_WIDTH, ENEMY_HEIGHT
        color = RED
        
        if self.type == 'basic':
            pass # Defaults are fine
            
        elif self.type == 'shooter':
            color = ORANGE
            self.last_shot = pygame.time.get_ticks()
            self.shoot_delay = 2000 # 2 seconds
            
        elif self.type == 'chaser':
            color = PURPLE
            base_speed *= 1.5
            
        elif self.type == 'tank':
            color = (100, 100, 100) # Gray
            width, height = int(ENEMY_WIDTH * 1.5), int(ENEMY_HEIGHT * 1.5)
            self.hp = 5
            base_speed *= 0.5

        # Image Handling
        try:
            filename = f"enemy_{self.type}.png" if self.type != 'basic' else "enemy.png"
            image_path = os.path.join(IMAGE_DIR, filename)
            # Check if file exists, otherwise fallback
            if os.path.exists(image_path):
                 self.image = pygame.image.load(image_path).convert_alpha()
                 self.image = pygame.transform.scale(self.image, (width, height))
            else:
                 # Fallback to creating a colored rect if specific image missing
                 if self.type == 'basic':
                     # Try generic enemy.png again
                     image_path = os.path.join(IMAGE_DIR, "enemy.png")
                     if os.path.exists(image_path):
                         self.image = pygame.image.load(image_path).convert_alpha()
                         self.image = pygame.transform.scale(self.image, (width, height))
                     else: raise FileNotFoundError
                 else: raise FileNotFoundError
        except (FileNotFoundError, pygame.error):
            self.image = pygame.Surface((width, height))
            self.image.fill(color)
            
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, SCREEN_WIDTH - width)
        self.rect.y = random.randrange(-150, -50)
        
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.speed = base_speed * speed_multiplier

    def update(self, player_rect=None, enemy_bullets_group=None):
        # Y Movement
        self.pos_y += self.speed
        
        # X Movement (Chaser)
        if self.type == 'chaser' and player_rect:
            center_x = self.pos_x + self.rect.width / 2
            if center_x < player_rect.centerx:
                self.pos_x += 1 # Chase speed
            elif center_x > player_rect.centerx:
                self.pos_x -= 1
        
        # Shooting (Shooter)
        if self.type == 'shooter' and enemy_bullets_group:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
                enemy_bullets_group.add(bullet)

        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

        if self.rect.top > SCREEN_HEIGHT + 10:
            self.kill()

    def take_damage(self, amount=1):
        self.hp -= amount
        return self.hp <= 0
