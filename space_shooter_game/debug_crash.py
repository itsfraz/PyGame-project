import pygame
import sys
import traceback
from settings import *
from vfx import Particle, Star

try:
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # Test valid colors
    print("Testing colors...")
    c = (*ORANGE, 255)
    print(f"Orange with alpha: {c}")
    pygame.draw.circle(screen, c, (10, 10), 5)
    
    print("Testing Particle...")
    p = Particle([], (100, 100), CYAN, 5, 5)
    p.update()
    p.draw(screen)
    
    print("Testing Star...")
    s = Star([])
    s.update()
    s.draw(screen)
    
    print("Testing Text...")
    font = pygame.font.SysFont("arial", 20)
    # Test your text function logic roughly
    glow_surf = font.render("TEST", True, BLUE)
    
    print("All tests passed.")
    pygame.quit()
except Exception:
    traceback.print_exc()
