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

from ui import AnimatedText, Button, HealthBar

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
    
    # --- UI SETUP ---
    # Menu
    title_text = AnimatedText(TITLE.upper(), assets['font_xl'], CYAN, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, pulse_speed=0.05)
    
    def start_game():
        nonlocal game_state, score, player
        game_state = "PLAYING"
        all_sprites.empty()
        mobs.empty()
        bullets.empty()
        particles.empty()
        player = Player()
        all_sprites.add(player)
        score = 0
        
    btn_play = Button("PLAY", assets['font_large'], SCREEN_WIDTH/2, SCREEN_HEIGHT/2, action=start_game)
    btn_quit = Button("QUIT", assets['font_large'], SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 80, bg_color=RED, hover_color=(200, 50, 50))
    # Actually, proper way for closure variable:
    def quit_game():
        nonlocal running
        running = False
    btn_quit.action = quit_game

    # HUD
    health_bar = HealthBar(20, 20, 200, 20, max_value=PLAYER_LIVES, color=GREEN)
    
    # Game Over
    go_text = AnimatedText("MISSION FAILED", assets['font_xl'], RED, SCREEN_WIDTH/2, SCREEN_HEIGHT/3, pulse_speed=0.02)
    btn_retry = Button("RETRY", assets['font_large'], SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50, action=start_game)
    btn_menu = Button("MENU", assets['font_large'], SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 130)
    
    def set_state_menu():
        nonlocal game_state
        game_state = "MENU"
    btn_menu.action = set_state_menu
    
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
    
    while running:
        dt = clock.tick(FPS) / 1000.0 # Delta time in seconds if needed, but we use frames mostly
        current_time = pygame.time.get_ticks()
        
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Pass events to UI buttons based on state
            if game_state == "MENU":
                btn_play.handle_event(event)
                btn_quit.handle_event(event)
                
            elif game_state == "GAMEOVER":
                btn_retry.handle_event(event)
                btn_menu.handle_event(event)

            if game_state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = not paused
                    if event.key == pygame.K_ESCAPE:
                        game_state = "MENU"

                if event.type == ADDENEMY and not paused:
                    new_enemy = Enemy(score)
                    mobs.add(new_enemy)
                    all_sprites.add(new_enemy)
                    
        # 2. Update
        shake_offset = (0, 0)
        
        if game_state == "MENU":
            title_text.update()
            btn_play.update()
            btn_quit.update()
            stars.update() # Keep stars moving
            particles.update()

        elif game_state == "PLAYING" and not paused:
            # Auto-fire
            mouse_pos = pygame.mouse.get_pos()
            if player.shoot(current_time, bullets, lambda x, y, d=None: bullets.add(Bullet(x, y, d)), target_pos=mouse_pos):
                if assets['shoot_sound']: assets['shoot_sound'].play()
                all_sprites.add(bullets.sprites()[-1])

            # Player update with particle callback
            player.update(create_particle)
            mobs.update()
            bullets.update()
            stars.update()
            particles.update()
            
            # UI Update
            health_bar.set_value(player.lives)
            health_bar.update()
            
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
        
        elif game_state == "GAMEOVER":
            go_text.update()
            btn_retry.update()
            btn_menu.update()
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
        if game_state == "MENU":
            # Dim Background
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))
            screen.blit(s, (0,0))
            
            title_text.draw(screen)
            btn_play.draw(screen)
            btn_quit.draw(screen)
            
            # Reset instructions
            draw_neon_text(screen, "Mouse to Aim/Shoot", assets['font_ui'], YELLOW, SCREEN_WIDTH/2, SCREEN_HEIGHT - 40)

        elif game_state == "PLAYING":
             # Score
             draw_neon_text(screen, f"SCORE: {score}", assets['font_ui'], WHITE, SCREEN_WIDTH - 100, 30)
             # Lives Bar
             health_bar.draw(screen)
             draw_neon_text(screen, "LIVES", assets['font_ui'], WHITE, 60, 45, "center")

             if paused:
                 s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                 s.fill((0, 0, 0, 150))
                 screen.blit(s, (0,0))
                 draw_neon_text(screen, "PAUSED", assets['font_xl'], WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        elif game_state == "GAMEOVER":
             # Draw game scene behind?
             if player.lives > 0:
                 for sprite in all_sprites:
                     screen.blit(sprite.image, (sprite.rect.x + shake_offset[0], sprite.rect.y + shake_offset[1]))
             
             s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
             s.fill((50, 0, 0, 200)) # Red tint
             screen.blit(s, (0,0))
             
             go_text.draw(screen)
             draw_neon_text(screen, f"FINAL SCORE: {score}", assets['font_large'], WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 40)
             
             btn_retry.draw(screen)
             btn_menu.draw(screen)

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
