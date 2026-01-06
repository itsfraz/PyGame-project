import pygame
import random
import os
import math
from settings import *

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx=0, dy=1, speed=None):
        super().__init__()
        self.image = pygame.Surface((6, 15))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.dx = dx
        self.dy = dy
        self.speed = speed if speed else 4
        
        # Rotate image if moving sideways significantly
        if dx != 0:
            angle = -math.degrees(math.atan2(dy, dx)) - 90
            self.image = pygame.transform.rotate(self.image, angle)

    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        
        if (self.rect.top > SCREEN_HEIGHT or 
            self.rect.bottom < 0 or 
            self.rect.right < 0 or 
            self.rect.left > SCREEN_WIDTH):
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

class Boss(pygame.sprite.Sprite):
    def __init__(self, hp_override=None):
        super().__init__()
        self.hp = hp_override if hp_override else BOSS_HP
        self.max_hp = self.hp
        
        width, height = BOSS_WIDTH, BOSS_HEIGHT
        
        # Try to load boss image or fallback
        try:
             image_path = os.path.join(IMAGE_DIR, "boss.png")
             if os.path.exists(image_path):
                 self.image = pygame.image.load(image_path).convert_alpha()
                 self.image = pygame.transform.scale(self.image, (width, height))
             else: raise FileNotFoundError
        except:
             self.image = pygame.Surface((width, height))
             self.image.fill(BOSS_COLOR)
             # Draw some "eyes"
             pygame.draw.rect(self.image, YELLOW, (20, 50, 20, 20))
             pygame.draw.rect(self.image, YELLOW, (width-40, 50, 20, 20))
        
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.y = -150
        
        self.state = "ENTERING" # ENTERING, FIGHTING
        self.target_y = 50
        self.speed_x = BOSS_SPEED
        
        self.last_attack_time = pygame.time.get_ticks()
        self.attack_cooldown = 2000 # 2 seconds between patterns

    def update(self, enemy_bullets_group):
        if self.state == "ENTERING":
            self.rect.y += 2
            if self.rect.y >= self.target_y:
                self.state = "FIGHTING"
                
        elif self.state == "FIGHTING":
            # Move side to side
            self.rect.x += self.speed_x
            if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
                self.speed_x *= -1
                
            # Attacks
            now = pygame.time.get_ticks()
            if now - self.last_attack_time > self.attack_cooldown:
                self.last_attack_time = now
                pattern = random.choice(['spread', 'sweep', 'circle'])
                
                if pattern == 'spread':
                    self.attack_spread(enemy_bullets_group)
                elif pattern == 'sweep':
                    self.attack_sweep(enemy_bullets_group)
                elif pattern == 'circle':
                    self.attack_circle(enemy_bullets_group)

    def attack_spread(self, group):
        # 5 bullets in a cone
        start_x = self.rect.centerx
        start_y = self.rect.bottom
        for i in range(-2, 3): # -2, -1, 0, 1, 2
            dx = i * 0.3
            dy = 1
            group.add(EnemyBullet(start_x, start_y, dx, dy, speed=6))

    def attack_sweep(self, group):
        # Just fire rapidly across?
        # Let's do a simple 3-wave burst for now
        start_x = self.rect.centerx
        start_y = self.rect.bottom
        # We can't do a time-based sweep easily without state, so let's do a static "shotgun" blast
        for i in range(10):
            dx = random.uniform(-1, 1)
            dy = random.uniform(0.5, 1.5)
            group.add(EnemyBullet(start_x, start_y, dx, dy, speed=7))

    def attack_circle(self, group):
        start_x = self.rect.centerx
        start_y = self.rect.centery
        count = 12
        for i in range(count):
            angle = (360 / count) * i
            rad = math.radians(angle)
            dx = math.cos(rad)
            dy = math.sin(rad)
            group.add(EnemyBullet(start_x, start_y, dx, dy, speed=5))

    def take_damage(self, amount):
        self.hp -= amount
        return self.hp <= 0
