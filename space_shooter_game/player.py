import pygame
import os
import random
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load image or fallback to surface
        try:
            # Try to load the new player image
            image_path = os.path.join(IMAGE_DIR, "player_new.png")
            # If player_new doesn't exist, try falling back to player.png
            if not os.path.exists(image_path):
                image_path = os.path.join(IMAGE_DIR, "player.png")

            self.image = pygame.image.load(image_path).convert()
            # Set colorkey to remove background (assumes top-left pixel is background color)
            self.image.set_colorkey(self.image.get_at((0, 0)))
            self.image = pygame.transform.scale(self.image, (PLAYER_WIDTH, PLAYER_HEIGHT))
        except (FileNotFoundError, pygame.error) as e:
            print(f"Error loading player image: {e}")
            self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            self.image.fill(GREEN)
        
        self.rect = self.image.get_rect()
        self.rect.midbottom = (PLAYER_START_X, PLAYER_START_Y)
        self.speed = PLAYER_SPEED
        self.last_shot_time = 0
        self.lives = PLAYER_LIVES
        self.bullet_count = BULLETS_PER_SHOT
        self.shoot_delay = SHOOT_COOLDOWN
        self.powerups = {}
        self.has_shield = False

    def powerup(self, p_type):
        now = pygame.time.get_ticks()
        self.powerups[p_type] = now + POWERUP_DURATION
        
        if p_type == 'health':
            self.lives += 1
            # One time effect, remove immediately from update tracking if desired,
            # but keeping it simple. Actually Health doesn't need duration.
            del self.powerups['health']
        elif p_type == 'shield':
            self.has_shield = True
        elif p_type == 'rapid_fire':
            self.shoot_delay = SHOOT_COOLDOWN / 2

    def update(self, create_particle_callback=None):
        # Powerup expiration
        now = pygame.time.get_ticks()
        if 'shield' in self.powerups and now > self.powerups['shield']:
            self.has_shield = False
            del self.powerups['shield']
        
        if 'rapid_fire' in self.powerups and now > self.powerups['rapid_fire']:
            self.shoot_delay = SHOOT_COOLDOWN
            del self.powerups['rapid_fire']

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
        if create_particle_callback:
            # 1. Engine Trail (Always active when moving or just always active for engine idle)
            # Emit from bottom center
            offset_x = random.randint(-5, 5)
            pos = (self.rect.centerx + offset_x, self.rect.bottom - 5)
            vec = pygame.math.Vector2(0, random.uniform(1, 3)) # Downward
            
            # Color based on speed or random neon
            p_color = CYAN
            if random.random() < 0.3: p_color = WHITE
            
            create_particle_callback(pos, p_color, random.randint(2, 5), random.randint(2, 4), vector=vec)
            
            # 2. Damage Smoke (Low Health)
            if self.lives == 1:
                # Random position on ship
                smoke_pos = (
                    self.rect.x + random.randint(0, self.rect.width),
                    self.rect.y + random.randint(0, self.rect.height)
                )
                smoke_vec = pygame.math.Vector2(random.uniform(-0.5, 0.5), -1) # Upward smoke
                # Grey/Dark Grey
                smoke_color = (100, 100, 100)
                if random.random() < 0.2: smoke_color = (50, 50, 50) # Darker
                elif random.random() < 0.1: smoke_color = ORANGE # Spark
                
                create_particle_callback(smoke_pos, smoke_color, random.randint(1, 3), random.randint(3, 8), vector=smoke_vec)

    def shoot(self, current_time, bullet_group, create_bullet_callback, target_pos=None):
        if current_time - self.last_shot_time >= self.shoot_delay:
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
