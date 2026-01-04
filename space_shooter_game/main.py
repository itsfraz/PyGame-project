import pygame
import random
import os
import sys
import math
import traceback
from settings import *
from player import Player
from enemy import Enemy
from bullet import Bullet
from vfx import Particle, ScreenShake, Star

# Initialize Pygame
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# --- Helpers ---

def draw_neon_text(surface, text, font, color, x, y, align="center", glow_color=None):
    if glow_color is None:
        glow_color = color
        
    # Draw glow (multiple offsets)
    for offset in [(-2, -2), (2, 2), (-2, 2), (2, -2)]:
        glow_surf = font.render(text, True, glow_color)
        glow_rect = glow_surf.get_rect()
        if align == "center":
            glow_rect.center = (x + offset[0], y + offset[1])
        elif align == "nw":
            glow_rect.topleft = (x + offset[0], y + offset[1])
        # Only alpha changed slightly? Actually simpler to just draw thicker
        glow_surf.set_alpha(100)
        surface.blit(glow_surf, glow_rect)
        
    # Draw main text
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if align == "nw":
        text_rect.topleft = (x, y)
    elif align == "ne":
        text_rect.topright = (x, y)
    elif align == "center":
        text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)
    return text_rect

def load_assets():
    assets = {}
    
    # Fonts - Try to find a cool one, fallback to system default
    font_name = pygame.font.match_font('impact') or pygame.font.match_font('arial')
    assets['font_ui'] = pygame.font.Font(font_name, UI_FONT_SIZE)
    assets['font_large'] = pygame.font.Font(font_name, GAME_OVER_FONT_SIZE)
    assets['font_xl'] = pygame.font.Font(font_name, 80)
    
    # Sounds
    try:
        assets['shoot_sound'] = pygame.mixer.Sound(os.path.join(SOUND_DIR, "shoot.wav"))
        assets['shoot_sound'].set_volume(0.4)
    except: assets['shoot_sound'] = None
        
    try:
        assets['explosion_sound'] = pygame.mixer.Sound(os.path.join(SOUND_DIR, "explosion.wav"))
        assets['explosion_sound'].set_volume(0.5)
    except: assets['explosion_sound'] = None

    try:
        pygame.mixer.music.load(os.path.join(SOUND_DIR, "bg_music.mp3"))
        pygame.mixer.music.set_volume(0.3)
    except: pass

    # Background
    try:
        bg_img = pygame.image.load(os.path.join(IMAGE_DIR, "background.png")).convert()
        assets['bg_image'] = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        assets['bg_image'] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        assets['bg_image'].fill(DARK_BLUE)

    return assets

def main():
    assets = load_assets()
    
    # Groups
    all_sprites = pygame.sprite.Group()
    mobs = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    particles = pygame.sprite.Group()
    stars = pygame.sprite.Group() # Parallax stars
    
    # Create Stars
    for _ in range(50):
        s = Star([stars]) # Render separately from all_sprites often for layering
    
    player = Player()
    all_sprites.add(player)
    
    # Logic
    score = 0
    running = True
    game_state = "MENU"
    paused = False
    
    # Bg Scroll
    bg_y = 0
    
    # VFX
    shaker = ScreenShake()
    
    # Callbacks
    def create_particle(pos, color, speed, radius, vector=None):
        Particle([particles], pos, color, speed, radius, decay=0.2, vector=vector)

    def spawn_explosion(center, color=ORANGE, count=15):
        for _ in range(count):
            create_particle(center, color, random.randint(2, 6), random.randint(3, 6))

    # Music
    if pygame.mixer.music.get_busy() == False:
        try: pygame.mixer.music.play(-1) 
        except: pass
        
    # Events
    ADDENEMY = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDENEMY, ENEMY_SPAWN_RATE)
    
    # Menu Animation
    pulse_val = 0

    while running:
        dt = clock.tick(FPS) / 1000.0 # Delta time in seconds if needed, but we use frames mostly
        current_time = pygame.time.get_ticks()
        
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_state == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        game_state = "PLAYING"
                        # Reset
                        all_sprites.empty()
                        mobs.empty()
                        bullets.empty()
                        particles.empty()
                        # Re-add player
                        player = Player()
                        all_sprites.add(player)
                        score = 0
                    if event.key == pygame.K_ESCAPE:
                        running = False

            elif game_state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                         if player.shoot(current_time, bullets, lambda x, y: bullets.add(Bullet(x, y))):
                             if assets['shoot_sound']: assets['shoot_sound'].play()
                             all_sprites.add(bullets.sprites()[-1])
                             # Kickback/Recoil visual? Maybe just sound for now
                    if event.key == pygame.K_p:
                        paused = not paused
                    if event.key == pygame.K_ESCAPE:
                        game_state = "MENU"

                if event.type == ADDENEMY and not paused:
                    new_enemy = Enemy(score)
                    mobs.add(new_enemy)
                    all_sprites.add(new_enemy)
                    
            elif game_state == "GAMEOVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game_state = "PLAYING"
                        all_sprites.empty()
                        mobs.empty()
                        bullets.empty()
                        particles.empty()
                        player = Player()
                        all_sprites.add(player)
                        score = 0
                    if event.key == pygame.K_ESCAPE:
                        running = False

        # 2. Update
        shake_offset = (0, 0)
        
        if game_state == "PLAYING" and not paused:
            # Player update with particle callback
            player.update(create_particle)
            mobs.update()
            bullets.update()
            stars.update()
            particles.update()
            
            # Collisions: Bullet <-> Enemy
            hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
            for hit in hits:
                score += 100
                if assets['explosion_sound']: assets['explosion_sound'].play()
                spawn_explosion(hit.rect.center, ORANGE)
                shaker.shake(5, 5) # Small shake

            # Collisions: Player <-> Enemy
            hits = pygame.sprite.spritecollide(player, mobs, True)
            for hit in hits:
                player.lives -= 1
                if assets['explosion_sound']: assets['explosion_sound'].play()
                spawn_explosion(hit.rect.center, RED, 20)
                shaker.shake(15, 15) # Big shake
                if player.lives <= 0:
                    game_state = "GAMEOVER"
                    spawn_explosion(player.rect.center, CYAN, 50) # Huge player explosion
        
        elif game_state in ["MENU", "GAMEOVER"]:
             stars.update()
             particles.update() 

        # Get screen shake offset
        shake_offset = shaker.get_offset()

        # 3. Draw
        rel_y = bg_y % assets['bg_image'].get_rect().height
        screen.blit(assets['bg_image'], (0 + shake_offset[0], rel_y - assets['bg_image'].get_rect().height + shake_offset[1]))
        if rel_y < SCREEN_HEIGHT:
            screen.blit(assets['bg_image'], (0 + shake_offset[0], rel_y + shake_offset[1]))
        if game_state == "PLAYING" and not paused:
            bg_y += 1
            
        # Draw Stars
        for star in stars:
            star.draw(screen, shake_offset)

        # Draw Sprites
        if game_state == "PLAYING" or (game_state == "GAMEOVER" and player.lives > 0): # Draw remains if just paused?
             for sprite in all_sprites:
                 screen.blit(sprite.image, (sprite.rect.x + shake_offset[0], sprite.rect.y + shake_offset[1]))
        
        # Draw Particles
        for p in particles:
            p.draw(screen, shake_offset)

        # UI Overlay
        if game_state == "PLAYING":
             # Score
             draw_neon_text(screen, f"SCORE: {score}", assets['font_ui'], WHITE, SCREEN_WIDTH/2, 20)
             # Lives Bar
             draw_neon_text(screen, "♥ " * player.lives, assets['font_ui'], RED, 20, 20, "nw")

             if paused:
                 s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                 s.fill((0, 0, 0, 150))
                 screen.blit(s, (0,0))
                 draw_neon_text(screen, "PAUSED", assets['font_xl'], WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        elif game_state == "MENU":
            # Darken bg
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 100))
            screen.blit(s, (0,0))
            
            draw_neon_text(screen, TITLE.upper(), assets['font_xl'], CYAN, SCREEN_WIDTH/2, SCREEN_HEIGHT/3, glow_color=BLUE)
            
            # Pulsing text
            pulse_val += 0.1
            alpha = abs(math.sin(pulse_val)) * 255
            
            start_surf = assets['font_large'].render("PRESS START", True, WHITE)
            start_surf.set_alpha(alpha)
            start_rect = start_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
            screen.blit(start_surf, start_rect)
            
            draw_neon_text(screen, "ARROWS to Move  |  SPACE to Shoot", assets['font_ui'], YELLOW, SCREEN_WIDTH/2, SCREEN_HEIGHT - 60)

        elif game_state == "GAMEOVER":
             s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
             s.fill((50, 0, 0, 180)) # Red tint
             screen.blit(s, (0,0))
             
             draw_neon_text(screen, "MISSION FAILED", assets['font_xl'], RED, SCREEN_WIDTH/2, SCREEN_HEIGHT/3)
             draw_neon_text(screen, f"FINAL SCORE: {score}", assets['font_large'], WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
             draw_neon_text(screen, "Press R to Retry", assets['font_ui'], YELLOW, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 80)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        with open("crash_log.txt", "w") as f:
            traceback.print_exc(file=f)
        pygame.quit()
        sys.exit()
