import pygame
import random
import os
import sys
import math
import traceback
from settings import *
from player import Player
from enemy import Enemy, Boss, Meteor
from bullet import Bullet
from vfx import Particle, ScreenShake, Star, BackgroundObject
from ui import AnimatedText, Button, HealthBar
from powerups import PowerUp

# Initialize Pygame
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

class HUD:
    def __init__(self, assets):
        self.assets = assets
        self.score_surf = None
        self.lives_surf = None
        self.update_score(0)
        self.update_lives(3)

    def update_score(self, score):
        # Render to a temporary surface large enough
        s = pygame.Surface((300, 60), pygame.SRCALPHA)
        draw_neon_text(s, f"SCORE: {score}", self.assets['font_ui'], WHITE, 280, 30, "ne")
        self.score_surf = s

    def update_lives(self, lives):
        s = pygame.Surface((150, 60), pygame.SRCALPHA)
        draw_neon_text(s, "LIVES", self.assets['font_ui'], WHITE, 75, 30, "center")
        self.lives_surf = s

    def draw(self, screen):
        if self.score_surf:
            screen.blit(self.score_surf, (SCREEN_WIDTH - 300, 0))
        if self.lives_surf:
            screen.blit(self.lives_surf, (0, 15))


def draw_neon_text(surface, text, font, color, x, y, align="center", glow_color=None):
    if glow_color is None:
        glow_color = color
        
    for offset in [(-2, -2), (2, 2), (-2, 2), (2, -2)]:
        glow_surf = font.render(text, True, glow_color)
        glow_rect = glow_surf.get_rect()
        if align == "center":
            glow_rect.center = (x + offset[0], y + offset[1])
        elif align == "nw":
            glow_rect.topleft = (x + offset[0], y + offset[1])
        elif align == "ne":
            glow_rect.topright = (x + offset[0], y + offset[1])
        glow_surf.set_alpha(100)
        surface.blit(glow_surf, glow_rect)
        
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
    font_name = pygame.font.match_font('impact') or pygame.font.match_font('arial')
    assets['font_ui'] = pygame.font.Font(font_name, UI_FONT_SIZE)
    assets['font_large'] = pygame.font.Font(font_name, GAME_OVER_FONT_SIZE)
    assets['font_xl'] = pygame.font.Font(font_name, 80)
    
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

    try:
        bg_img = pygame.image.load(os.path.join(IMAGE_DIR, "background.png")).convert()
        assets['bg_image'] = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        assets['bg_image'] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        assets['bg_image'].fill(DARK_BLUE)

    return assets

def get_high_score():
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read())
    except:
        return 0

def save_high_score(new_score):
    try:
        with open("highscore.txt", "w") as f:
            f.write(str(new_score))
    except:
        pass

class WaveManager:
    def __init__(self):
        self.wave_index = 0
        self.waves = [
            {'name': "Wave 1 - Invasion", 'count': 20, 'rate': 1500, 'type': 'basic'},
            {'name': "Wave 2 - Assault", 'count': 30, 'rate': 1200, 'type': 'fast'}, 
            {'name': "Wave 3 - Meteor Shower", 'count': 40, 'rate': 600, 'type': 'meteor'},
        ]
        # Infinite waves start after
        self.infinite_mode = False
        
        self.state = "SPAWNING" # SPAWNING, CLEARING, RESTING
        self.spawned_count = 0
        self.last_spawn_time = 0
        self.rest_start_time = 0

    def reset(self):
        self.wave_index = 0
        self.state = "SPAWNING"
        self.spawned_count = 0
        self.last_spawn_time = 0
        self.infinite_mode = False

    def update(self, current_time, active_mobs_count, active_boss):
        if active_boss:
            return None # Pause everything

        if self.infinite_mode:
            # Simple random logic
             if current_time - self.last_spawn_time > 1000:
                self.last_spawn_time = current_time
                return 'random'
             return None

        # Logic
        wave_data = self.waves[self.wave_index]
        
        if self.state == "SPAWNING":
            if self.spawned_count < wave_data['count']:
                if current_time - self.last_spawn_time > wave_data['rate']:
                    self.last_spawn_time = current_time
                    self.spawned_count += 1
                    return wave_data['type']
            else:
                self.state = "CLEARING"

        elif self.state == "CLEARING":
            if active_mobs_count == 0:
                self.state = "RESTING"
                self.rest_start_time = current_time

        elif self.state == "RESTING":
            if current_time - self.rest_start_time > WAVE_REST_DURATION:
                self.next_wave()
        
        return None

    def next_wave(self):
        self.wave_index += 1
        if self.wave_index >= len(self.waves):
            self.infinite_mode = True
        else:
            self.state = "SPAWNING"
            self.spawned_count = 0
            self.last_spawn_time = pygame.time.get_ticks()

    def get_info(self):
        if self.infinite_mode:
            return "WAVE ∞"
        if self.state == "RESTING":
            return "WAVE COMPLETE"
        return f"{self.waves[self.wave_index]['name']} ({self.spawned_count}/{self.waves[self.wave_index]['count']})"

def main():
    assets = load_assets()
    high_score = get_high_score()
    hud = HUD(assets)
    wave_manager = WaveManager()
    
    # Groups
    all_sprites = pygame.sprite.Group()
    mobs = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    particles = pygame.sprite.Group()
    stars = pygame.sprite.Group() # Parallax stars
    powerups = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    boss_group = pygame.sprite.Group() # New group for Boss
    meteors = pygame.sprite.Group() # Separate group for meteors
    bg_objects = pygame.sprite.Group() # Dynamic background objects
    
    # Create Stars
    for _ in range(50):
        s = Star([stars]) 
    
    player = Player()
    all_sprites.add(player)
    
    # Logic
    score = 0
    running = True
    game_state = "MENU"
    paused = False
    
    # Boss Logic
    boss_active = False
    next_boss_score = BOSS_SPAWN_SCORE
    
    # Bg Scroll
    bg_y = 0
    
    # VFX
    shaker = ScreenShake()
    
    # --- UI SETUP ---
    # Menu
    title_text = AnimatedText(TITLE.upper(), assets['font_xl'], CYAN, SCREEN_WIDTH/2, SCREEN_HEIGHT/4, pulse_speed=0.05)
    hs_text_menu = AnimatedText(f"HIGH SCORE: {high_score}", assets['font_ui'], YELLOW, SCREEN_WIDTH/2, SCREEN_HEIGHT/4 + 60, pulse_speed=0.02)
    

    def start_game():
        nonlocal game_state, score, player, boss_active, next_boss_score
        game_state = "PLAYING"
        all_sprites.empty()
        mobs.empty()
        bullets.empty()
        particles.empty()
        powerups.empty() 
        enemy_bullets.empty()
        boss_group.empty()
        meteors.empty()
        bg_objects.empty()
        
        player = Player()
        all_sprites.add(player)
        score = 0
        hud.update_score(0)
        hud.update_lives(player.lives)
        health_bar.set_value(player.lives)
        
        boss_active = False
        next_boss_score = BOSS_SPAWN_SCORE
        
        wave_manager.reset()
        
    btn_play = Button("PLAY", assets['font_large'], SCREEN_WIDTH/2, SCREEN_HEIGHT/2, action=start_game)
    btn_quit = Button("QUIT", assets['font_large'], SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 80, bg_color=RED, hover_color=(200, 50, 50))

    
    def quit_game():
        nonlocal running
        running = False
    btn_quit.action = quit_game

    # HUD
    health_bar = HealthBar(20, 20, 200, 20, max_value=PLAYER_LIVES, color=GREEN)
    boss_health_bar = HealthBar(SCREEN_WIDTH//2 - 150, 60, 300, 20, max_value=BOSS_HP, color=PURPLE)
    
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
    # ADDENEMY = pygame.USEREVENT + 1
    # pygame.time.set_timer(ADDENEMY, ENEMY_SPAWN_RATE)
        
    while running:
        dt = clock.tick(FPS) / 1000.0
        current_time = pygame.time.get_ticks()
        
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
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
                    
        # 2. Update
        shake_offset = (0, 0)
        
        if game_state == "MENU":
            title_text.update()
            hs_text_menu.text = f"HIGH SCORE: {high_score}"
            hs_text_menu.update()
            btn_play.update()
            btn_quit.update()
            stars.update()
            particles.update()

        elif game_state == "PLAYING" and not paused:
            # Random Background Object Spawn (Nebula or Planet)
            if random.random() < 0.001: # 0.1% chance per frame (~once every 16 seconds at 60fps? No, 60 * 0.001 = 0.06 per sec. Once every 16 secs approx)
                new_bg = BackgroundObject([bg_objects], random.choice(['planet', 'nebula']))

            # Wave Logic
            active_mobs_count = len(mobs) + len(meteors)
            spawn_type = wave_manager.update(current_time, active_mobs_count, boss_active)
            
            if spawn_type:
                 if spawn_type == 'meteor':
                     m = Meteor()
                     meteors.add(m)
                     all_sprites.add(m)
                 else:
                     etype = None
                     if spawn_type == 'fast': etype = 'chaser'
                     elif spawn_type == 'basic': etype = 'basic'
                     elif spawn_type == 'random': etype = None
                     
                     new_enemy = Enemy(score, enemy_type=etype)
                     mobs.add(new_enemy)
                     all_sprites.add(new_enemy)

            # Check Boss Spawn
            if score >= next_boss_score and not boss_active:
                boss_active = True
                new_boss = Boss()
                boss_group.add(new_boss)
                all_sprites.add(new_boss)
                # Ensure no other enemies are clogging the screen (optional, but requested behavior is just pause spawn)
                
            # Auto-fire
            mouse_pos = pygame.mouse.get_pos()
            if player.shoot(current_time, bullets, lambda x, y, d=None: bullets.add(Bullet(x, y, d)), target_pos=mouse_pos):
                if assets['shoot_sound']: assets['shoot_sound'].play()
                for b in bullets:
                    if b not in all_sprites: all_sprites.add(b)

            player.update(create_particle)
            mobs.update(player.rect, enemy_bullets)
            meteors.update()
            boss_group.update(enemy_bullets) # Boss updates with bullet group
            bullets.update()
            enemy_bullets.update()
            stars.update()
            bg_objects.update()
            particles.update()
            powerups.update()
            
            # Collisions: Player <-> Powerups
            hits = pygame.sprite.spritecollide(player, powerups, True)
            for hit in hits:
                player.powerup(hit.type)
                if hit.type == 'health':
                    hud.update_lives(player.lives)

            # Check Player <-> Enemy Bullet Collision
            hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
            for hit in hits:
                if player.has_shield:
                    spawn_explosion(hit.rect.center, BLUE, 10)
                else:
                    player.lives -= 1
                    hud.update_lives(player.lives)
                    if assets['explosion_sound']: assets['explosion_sound'].play()
                    spawn_explosion(hit.rect.center, RED, 10)
                    shaker.shake(5, 5)
                    if player.lives <= 0:
                         game_state = "GAMEOVER"
                         spawn_explosion(player.rect.center, CYAN, 50)
                         if score > high_score:
                             high_score = score
                             save_high_score(high_score)

            # Collisions: Bullet <-> Enemy
            hits = pygame.sprite.groupcollide(mobs, bullets, False, True) 
            for enemy, hit_bullets in hits.items():
                for b in hit_bullets:
                    score += 10
                    hud.update_score(score)
                    create_particle(b.rect.center, ORANGE, 2, 2)
                    
                    if enemy.take_damage(1):
                        score += 90
                        hud.update_score(score)
                        enemy.kill()
                        
                        if assets['explosion_sound']: assets['explosion_sound'].play()
                        spawn_explosion(enemy.rect.center, ORANGE)
                        shaker.shake(5, 5)
                        
                        if random.random() < POWERUP_SPAWN_CHANCE:
                             p = PowerUp(enemy.rect.center)
                             all_sprites.add(p)
                             powerups.add(p)
                
                if score >= 3500:
                    player.bullet_count = 5

            # Handle Meteors Collision with Bullets
            hits = pygame.sprite.groupcollide(meteors, bullets, False, True)
            for m, hit_bullets in hits.items():
                for b in hit_bullets:
                    create_particle(b.rect.center, (100, 100, 100), 2, 2)
            
            # Collisions: Player <-> Meteors
            hits = pygame.sprite.spritecollide(player, meteors, True)
            for hit in hits:
                 if player.has_shield:
                    spawn_explosion(hit.rect.center, BLUE, 30)
                    shaker.shake(10, 10)
                 else:
                    player.lives -= 1
                    hud.update_lives(player.lives)
                    if assets['explosion_sound']: assets['explosion_sound'].play()
                    spawn_explosion(hit.rect.center, (139, 69, 19), 30)
                    shaker.shake(20, 20)
                    if player.lives <= 0:
                        game_state = "GAMEOVER"
                        spawn_explosion(player.rect.center, CYAN, 50)
                        if score > high_score:
                            high_score = score
                            save_high_score(high_score)

            # Collision: Bullet <-> Boss
            if boss_active:
                boss_hits = pygame.sprite.groupcollide(boss_group, bullets, False, True)
                for boss, hit_bullets in boss_hits.items():
                    for b in hit_bullets:
                        # Damage Boss
                        if boss.state == "FIGHTING": # Invulnerable while entering? Maybe. Let's allow damage.
                            create_particle(b.rect.center, PURPLE, 2, 2)
                            is_dead = boss.take_damage(1)
                            boss_health_bar.set_value(boss.hp)
                            
                            if is_dead:
                                score += 5000
                                hud.update_score(score)
                                boss.kill()
                                boss_active = False
                                next_boss_score += 5000
                                spawn_explosion(boss.rect.center, MAGENTA, 100)
                                shaker.shake(20, 30)
                                if assets['explosion_sound']: assets['explosion_sound'].play()
                                
                                # Spawn a guaranteed powerup
                                p = PowerUp(boss.rect.center)
                                all_sprites.add(p)
                                powerups.add(p)

            # Collisions: Player <-> Mobs
            hits = pygame.sprite.spritecollide(player, mobs, True)
            for hit in hits:
                if player.has_shield:
                    spawn_explosion(hit.rect.center, BLUE, 20)
                    shaker.shake(5, 5)
                else:
                    player.lives -= 1
                    hud.update_lives(player.lives)
                    if assets['explosion_sound']: assets['explosion_sound'].play()
                    spawn_explosion(hit.rect.center, RED, 20)
                    shaker.shake(15, 15)
                    if player.lives <= 0:
                        game_state = "GAMEOVER"
                        spawn_explosion(player.rect.center, CYAN, 50)
                        if score > high_score:
                            high_score = score
                            save_high_score(high_score)
            
            # Collisions: Player <-> Boss Body
            if boss_active:
                hits = pygame.sprite.spritecollide(player, boss_group, False)
                if hits:
                    if not player.has_shield:
                        # Instakill or massive damage?
                        player.lives = 0
                        hud.update_lives(player.lives)
                        game_state = "GAMEOVER"
                        spawn_explosion(player.rect.center, CYAN, 50)
                        if score > high_score:
                             high_score = score
                             save_high_score(high_score)
                    else:
                        # Bounce player back or something? Just keep taking damage if shield up?
                        # Shield usually protects 1 hit? Let's assume shield breaks instantly on boss
                        player.has_shield = False
                        spawn_explosion(player.rect.center, BLUE, 30)
                        shaker.shake(10, 10)
                        # Push player down
                        player.rect.y += 100

        elif game_state == "GAMEOVER":
            go_text.update()
            btn_retry.update()
            btn_menu.update()
            stars.update()
            particles.update()

        shake_offset = shaker.get_offset()

        rel_y = bg_y % assets['bg_image'].get_rect().height
        screen.blit(assets['bg_image'], (0 + shake_offset[0], rel_y - assets['bg_image'].get_rect().height + shake_offset[1]))
        if rel_y < SCREEN_HEIGHT:
            screen.blit(assets['bg_image'], (0 + shake_offset[0], rel_y + shake_offset[1]))
        if game_state == "PLAYING" and not paused:
            bg_y += 1
            
        for star in stars:
            star.draw(screen, shake_offset)
            
        for bg_obj in bg_objects:
            screen.blit(bg_obj.image, (bg_obj.rect.x + shake_offset[0], bg_obj.rect.y + shake_offset[1]))

        if game_state == "PLAYING" or (game_state == "GAMEOVER" and player.lives > 0):
             for sprite in all_sprites:
                 screen.blit(sprite.image, (sprite.rect.x + shake_offset[0], sprite.rect.y + shake_offset[1]))
             
             for b in enemy_bullets:
                 screen.blit(b.image, (b.rect.x + shake_offset[0], b.rect.y + shake_offset[1]))
        
        for p in particles:
            p.draw(screen, shake_offset)

        if game_state == "MENU":
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))
            screen.blit(s, (0,0))
            
            title_text.draw(screen)
            hs_text_menu.draw(screen)
            btn_play.draw(screen)
            btn_quit.draw(screen)
            draw_neon_text(screen, "Mouse to Aim/Shoot", assets['font_ui'], YELLOW, SCREEN_WIDTH/2, SCREEN_HEIGHT - 40)

        elif game_state == "PLAYING":
             hud.draw(screen)
             health_bar.draw(screen)
             
             # Draw Wave Info
             draw_neon_text(screen, wave_manager.get_info(), assets['font_ui'], WHITE, SCREEN_WIDTH//2, 20)
             
             if boss_active:
                 boss_health_bar.update()
                 boss_health_bar.draw(screen)
                 # Draw Boss Name
                 draw_neon_text(screen, "WARNING: BOSS APPROACHING", assets['font_ui'], RED, SCREEN_WIDTH/2, 40)


             if paused:
                 s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                 s.fill((0, 0, 0, 150))
                 screen.blit(s, (0,0))
                 draw_neon_text(screen, "PAUSED", assets['font_xl'], WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        elif game_state == "GAMEOVER":
             if player.lives > 0:
                 for sprite in all_sprites:
                     screen.blit(sprite.image, (sprite.rect.x + shake_offset[0], sprite.rect.y + shake_offset[1]))
             
             s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
             s.fill((50, 0, 0, 200)) # Red tint
             screen.blit(s, (0,0))
             
             go_text.draw(screen)
             draw_neon_text(screen, f"FINAL SCORE: {score}", assets['font_large'], WHITE, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 40)
             draw_neon_text(screen, f"HIGH SCORE: {high_score}", assets['font_ui'], YELLOW, SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 10)
             
             btn_retry.draw(screen)
             btn_menu.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except BaseException:
        import datetime
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash_log.txt")
        with open(log_path, "w") as f:
            f.write(f"Crash Timestamp: {datetime.datetime.now()}\n")
            traceback.print_exc(file=f)
        pygame.quit()
        sys.exit()
