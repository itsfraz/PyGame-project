import pygame
import math
from settings import *

class UIElement:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self):
        pass

    def draw(self, surface):
        pass

class AnimatedText(UIElement):
    def __init__(self, text, font, color, x, y, align="center", pulse_speed=0):
        super().__init__(x, y)
        self.text = text
        self.font = font
        self.base_color = color
        self.align = align
        self.pulse_speed = pulse_speed
        self.pulse_val = 0
        self.scale_val = 1.0

    def update(self):
        if self.pulse_speed > 0:
            self.pulse_val += self.pulse_speed
            # Pulse opacity or scale? Let's do scale for impact
            self.scale_val = 1.0 + (math.sin(self.pulse_val) * 0.05)

    def draw(self, surface):
        # Render text
        text_surf = self.font.render(self.text, True, self.base_color)
        
        # Scaling
        if self.pulse_speed > 0:
            w = int(text_surf.get_width() * self.scale_val)
            h = int(text_surf.get_height() * self.scale_val)
            text_surf = pygame.transform.scale(text_surf, (w, h))

        rect = text_surf.get_rect()
        if self.align == "center":
            rect.center = (self.x, self.y)
        elif self.align == "nw":
            rect.topleft = (self.x, self.y)
        elif self.align == "ne":
            rect.topright = (self.x, self.y)
            
        # Drop shadow / Glow
        glow_surf = self.font.render(self.text, True, (self.base_color[0]//2, self.base_color[1]//2, self.base_color[2]//2))
        if self.pulse_speed > 0:
             w_g = int(glow_surf.get_width() * self.scale_val)
             h_g = int(glow_surf.get_height() * self.scale_val)
             glow_surf = pygame.transform.scale(glow_surf, (w_g, h_g))
        
        glow_rect = glow_surf.get_rect(center=rect.center)
        glow_rect.x += 2
        glow_rect.y += 2
        
        surface.blit(glow_surf, glow_rect)
        surface.blit(text_surf, rect)

class Button(UIElement):
    def __init__(self, text, font, x, y, width=200, height=50, bg_color=DARK_BLUE, hover_color=BLUE, text_color=WHITE, action=None):
        super().__init__(x, y)
        self.text = text
        self.font = font
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action
        
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x, y)
        
        self.is_hovered = False
        self.click_animation = 0

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        if self.click_animation > 0:
            self.click_animation -= 1

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                self.click_animation = 5
                if self.action:
                    self.action()
                return True
        return False

    def draw(self, surface):
        # Draw background with glass effect (alpha)
        color = self.hover_color if self.is_hovered else self.bg_color
        
        # Click effect
        draw_rect = self.rect.copy()
        if self.click_animation > 0:
             draw_rect.inflate_ip(-4, -4)

        # Transparent surface
        s = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
        # Rounded corners
        pygame.draw.rect(s, (*color, 200), s.get_rect(), border_radius=10)
        
        # Border
        pygame.draw.rect(s, (255, 255, 255, 100), s.get_rect(), 2, border_radius=10)
        
        surface.blit(s, draw_rect.topleft)
        
        # Text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        surface.blit(text_surf, text_rect)

class HealthBar(UIElement):
    def __init__(self, x, y, width, height, max_value=100, color=GREEN):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.max_value = max_value
        self.current_value = max_value
        self.target_value = max_value
        self.color = color
        
    def set_value(self, value):
        self.target_value = max(0, min(value, self.max_value))
        
    def update(self):
        # Smooth lerp
        self.current_value += (self.target_value - self.current_value) * 0.1

    def draw(self, surface):
        # Background
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (50, 50, 50), bg_rect, border_radius=5)
        
        # Foreground
        ratio = self.current_value / self.max_value
        fill_width = int(self.width * ratio)
        fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
        
        # Color based on health?
        c = self.color
        if ratio < 0.3: c = RED
        elif ratio < 0.6: c = ORANGE
        
        pygame.draw.rect(surface, c, fill_rect, border_radius=5)
        
        # Border
        pygame.draw.rect(surface, WHITE, bg_rect, 2, border_radius=5)

