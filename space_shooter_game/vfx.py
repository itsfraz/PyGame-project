import pygame
import random
from settings import *

class Particle(pygame.sprite.Sprite):
    def __init__(self, groups, pos, color, speed, radius, decay=0.2, vector=None):
        super().__init__(groups)
        self.pos = list(pos)
        self.color = color
        self.speed = speed
        self.radius = radius
        self.decay = decay
        self.life = 255
        
        if vector:
            self.direction = vector
        else:
            # Random direction
            mx = random.uniform(-1, 1)
            my = random.uniform(-1, 1)
            self.direction = pygame.math.Vector2(mx, my).normalize()

    def update(self):
        # Move
        self.pos[0] += self.direction.x * self.speed
        self.pos[1] += self.direction.y * self.speed
        
        # Fade
        self.life -= self.decay * 10
        if self.life <= 0 or self.radius <= 0:
            self.kill()

    def draw(self, surface, offset=(0,0)):
        if self.life > 0:
            try:
                # Create a surface for transparency
                r = int(self.radius) if self.radius > 0 else 1
                surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                
                # Ensure color is valid
                if len(self.color) != 3:
                     self.color = (255, 255, 255)
                     
                alpha_color = (*self.color, min(255, max(0, int(self.life))))
                pygame.draw.circle(surf, alpha_color, (r, r), r)
                surface.blit(surf, (self.pos[0] - r + offset[0], self.pos[1] - r + offset[1]))
            except Exception as e:
                pass # Silently fail particle draw to avoid crash

class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.timer = 0
        
    def shake(self, intensity=5, duration=10):
        self.intensity = intensity
        self.timer = duration
        
    def get_offset(self):
        if self.timer > 0:
            self.timer -= 1
            ox = random.randint(-self.intensity, self.intensity)
            oy = random.randint(-self.intensity, self.intensity)
            return (ox, oy)
        return (0, 0)

class Star(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.5, 3.0)
        self.radius = random.randint(1, 3)
        self.color = random.choice([WHITE, CYAN, PURPLE])
        # Brightness flicker
        self.alpha = random.randint(100, 255)
        self.alpha_change = random.choice([-2, 2])

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = -10
            self.x = random.randint(0, SCREEN_WIDTH)
            
        # Flicker
        self.alpha += self.alpha_change
        
        # Clamp alpha in update logic too, just to be safe
        if self.alpha >= 255:
            self.alpha = 255
            self.alpha_change *= -1
        elif self.alpha <= 100:
            self.alpha = 100
            self.alpha_change *= -1

    def draw(self, surface, offset=(0,0)):
        # Allow drawing with offset for shake
        pos = (int(self.x + offset[0]), int(self.y + offset[1]))
        if 0 <= pos[0] <= SCREEN_WIDTH and 0 <= pos[1] <= SCREEN_HEIGHT:
            try:
                surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
                
                # Ensure alpha is valid for drawing
                # Although we clamp in update, let's double check here
                a = min(255, max(0, int(self.alpha)))
                
                # Ensure color
                c = self.color
                if len(c) != 3: c = (255, 255, 255)
                
                # Draw
                pygame.draw.circle(surf, (*c, a), (self.radius, self.radius), self.radius)
                surface.blit(surf, (pos[0]-self.radius, pos[1]-self.radius))
            except Exception as e:
                # Log but don't crash
                 print(f"Star Draw Error: {e}")

class BackgroundObject(pygame.sprite.Sprite):
    def __init__(self, groups, image_type='planet'):
        super().__init__(groups)
        self.image_type = image_type
        
        # Random size and speed for parallax
        self.z_depth = random.uniform(0.2, 0.8) # 0.2 is far/slow, 0.8 is near/faster
        size = int(random.randint(50, 150) * self.z_depth)
        self.speed = 1.0 * self.z_depth
        
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if image_type == 'planet':
            # Draw a planet
            color = random.choice([(100, 100, 200), (200, 100, 100), (100, 200, 100), (150, 150, 150)])
            pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
            # Add some shading?
            pygame.draw.circle(self.image, (0,0,0, 50), (size//2 + 10, size//2 + 10), size//2 - 5)
            
        elif image_type == 'nebula':
            # Draw a cloud-like blob
            color = random.choice([(100, 0, 100, 50), (0, 0, 100, 50), (100, 0, 0, 50)])
            for _ in range(5):
                cx = random.randint(0, size)
                cy = random.randint(0, size)
                cr = random.randint(size//4, size//2)
                pygame.draw.circle(self.image, color, (cx, cy), cr)
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - size)
        self.rect.y = -size - 50
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
