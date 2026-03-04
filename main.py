import sys

import pygame
import random

from controls import move_player, move_player_with_joystick
from classes.constants import WIDTH, HEIGHT, FPS, SHOOT_DELAY
from functions import show_game_over, music_background
from menu import MainMenu

from classes.player import Player
from classes.bullets import Bullet
from classes.refill import BulletRefill, HealthRefill, DoubleRefill, ExtraScore
from classes.meteors import Meteors, Meteors2, BlackHole
from classes.explosions import Explosion, Explosion2
from classes.enemies import Enemy1, Enemy2
from classes.bosses import Boss1, Boss2, Boss3


class GameState:
    """Enum-like class for game states."""
    MENU = "menu"
    PLAYING = "playing"
    QUIT = "quit"


class Game:
    """Main game class that manages the game loop and state."""

    def __init__(self, show_menu=True):
        pygame.init()
        music_background()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.surface = pygame.Surface((WIDTH, HEIGHT))
        pygame.display.set_caption("Cosmic Heat")
        self.clock = pygame.time.Clock()

        self.show_menu = show_menu
        self.state = GameState.MENU if show_menu else GameState.PLAYING
        self.running = True

        self._init_sprite_groups()
        self._init_boss_state()
        self._init_backgrounds()
        self._init_images()
        self._init_player_state()
        self._init_joystick()

    def _init_sprite_groups(self):
        self.explosions = pygame.sprite.Group()
        self.explosions2 = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy1_group = pygame.sprite.Group()
        self.enemy2_group = pygame.sprite.Group()
        self.boss1_group = pygame.sprite.Group()
        self.boss2_group = pygame.sprite.Group()
        self.boss3_group = pygame.sprite.Group()
        self.bullet_refill_group = pygame.sprite.Group()
        self.health_refill_group = pygame.sprite.Group()
        self.double_refill_group = pygame.sprite.Group()
        self.meteor_group = pygame.sprite.Group()
        self.meteor2_group = pygame.sprite.Group()
        self.extra_score_group = pygame.sprite.Group()
        self.black_hole_group = pygame.sprite.Group()
        self.enemy2_bullets = pygame.sprite.Group()
        self.boss1_bullets = pygame.sprite.Group()
        self.boss2_bullets = pygame.sprite.Group()
        self.boss3_bullets = pygame.sprite.Group()

    def _init_boss_state(self):
        self.boss1_health = 150
        self.boss1_health_bar_rect = pygame.Rect(0, 0, 150, 5)
        self.boss1_spawned = False

        self.boss2_health = 150
        self.boss2_health_bar_rect = pygame.Rect(0, 0, 150, 5)
        self.boss2_spawned = False

        self.boss3_health = 200
        self.boss3_health_bar_rect = pygame.Rect(0, 0, 200, 5)
        self.boss3_spawned = False

    def _init_backgrounds(self):
        self.bg_y_shift = -HEIGHT
        self.background_img = pygame.image.load('images/bg/background.jpg').convert()
        self.background_img2 = pygame.image.load('images/bg/background2.png').convert()
        self.background_img3 = pygame.image.load('images/bg/background3.png').convert()
        self.background_img4 = pygame.image.load('images/bg/background4.png').convert()
        self.background_top = self.background_img.copy()
        self.current_image = self.background_img
        self.new_background_activated = False

    def _init_images(self):
        self.explosion_images = [pygame.image.load(f"images/explosion/explosion{i}.png") for i in range(8)]
        self.explosion2_images = [pygame.image.load(f"images/explosion2/explosion{i}.png") for i in range(18)]
        self.explosion3_images = [pygame.image.load(f"images/explosion3/explosion{i}.png") for i in range(18)]

        self.enemy1_img = [
            pygame.image.load('images/enemy/enemy1_1.png').convert_alpha(),
            pygame.image.load('images/enemy/enemy1_2.png').convert_alpha(),
            pygame.image.load('images/enemy/enemy1_3.png').convert_alpha()
        ]
        self.enemy2_img = [
            pygame.image.load('images/enemy/enemy2_1.png').convert_alpha(),
            pygame.image.load('images/enemy/enemy2_2.png').convert_alpha()
        ]
        self.boss1_img = pygame.image.load('images/boss/boss1.png').convert_alpha()
        self.boss2_img = pygame.image.load('images/boss/boss2_1.png').convert_alpha()
        self.boss3_img = pygame.image.load('images/boss/boss3.png').convert_alpha()

        self.health_refill_img = pygame.image.load('images/refill/health_refill.png').convert_alpha()
        self.bullet_refill_img = pygame.image.load('images/refill/bullet_refill.png').convert_alpha()
        self.double_refill_img = pygame.image.load('images/refill/double_refill.png').convert_alpha()

        self.meteor_imgs = [
            pygame.image.load('images/meteors/meteor_1.png').convert_alpha(),
            pygame.image.load('images/meteors/meteor_2.png').convert_alpha(),
            pygame.image.load('images/meteors/meteor_3.png').convert_alpha(),
            pygame.image.load('images/meteors/meteor_4.png').convert_alpha()
        ]
        self.meteor2_imgs = [
            pygame.image.load('images/meteors/meteor2_1.png').convert_alpha(),
            pygame.image.load('images/meteors/meteor2_2.png').convert_alpha(),
            pygame.image.load('images/meteors/meteor2_3.png').convert_alpha(),
            pygame.image.load('images/meteors/meteor2_4.png').convert_alpha()
        ]
        self.extra_score_img = pygame.image.load('images/score/score_coin.png').convert_alpha()
        self.black_hole_imgs = [
            pygame.image.load('images/hole/black_hole.png').convert_alpha(),
            pygame.image.load('images/hole/black_hole2.png').convert_alpha()
        ]

    def _init_player_state(self):
        self.initial_player_pos = (WIDTH // 2, HEIGHT - 100)
        self.score = 0
        self.hi_score = 0
        self.player = Player()
        self.player_life = 200
        self.bullet_counter = 200
        self.paused = False
        self.is_shooting = False
        self.last_shot_time = 0

    def _init_joystick(self):
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

    def run_menu(self):
        """Run the main menu and return when user starts game or quits."""
        menu = MainMenu()
        menu.run()
        self.state = GameState.PLAYING

    def handle_events(self):
        """Process all pygame events. Returns False if game should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.state = GameState.QUIT
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.paused:
                    if self.bullet_counter > 0 and pygame.time.get_ticks() - self.last_shot_time > SHOOT_DELAY:
                        self.last_shot_time = pygame.time.get_ticks()
                        bullet = Bullet(self.player.rect.centerx, self.player.rect.top)
                        self.bullets.add(bullet)
                        self.bullet_counter -= 1
                    self.is_shooting = True

                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                    self.state = GameState.QUIT
                    return False
                elif event.key == pygame.K_p or event.key == pygame.K_PAUSE:
                    self.paused = not self.paused
                elif not self.paused:
                    if event.key == pygame.K_LEFT:
                        self.player.move_left()
                    elif event.key == pygame.K_RIGHT:
                        self.player.move_right()
                    elif event.key == pygame.K_UP:
                        self.player.move_up()
                    elif event.key == pygame.K_DOWN:
                        self.player.move_down()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE and self.player.original_image is not None:
                    self.player.image = self.player.original_image.copy()
                    self.is_shooting = False
                elif not self.paused:
                    if event.key == pygame.K_LEFT:
                        self.player.stop_left()
                    elif event.key == pygame.K_RIGHT:
                        self.player.stop_right()
                    elif event.key == pygame.K_UP:
                        self.player.stop_up()
                    elif event.key == pygame.K_DOWN:
                        self.player.stop_down()

            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0 and not self.paused:
                    self.is_shooting = True
                    if self.bullet_counter > 0:
                        bullet = Bullet(self.player.rect.centerx, self.player.rect.top)
                        self.bullets.add(bullet)
                        self.bullet_counter -= 1
                elif event.button == 7:
                    self.paused = not self.paused
            elif event.type == pygame.JOYBUTTONUP:
                if event.button == 0 and self.player.original_image is not None:
                    self.is_shooting = False

        return True

    def update(self):
        """Update game state for one frame."""
        if pygame.time.get_ticks() - self.last_shot_time > SHOOT_DELAY and self.is_shooting and not self.paused:
            if self.bullet_counter > 0:
                self.last_shot_time = pygame.time.get_ticks()
                bullet = Bullet(self.player.rect.centerx, self.player.rect.top)
                self.bullets.add(bullet)
                self.bullet_counter -= 1

        if self.joystick:
            if not self.paused:
                move_player_with_joystick(self.joystick, self.player)

        if self.paused:
            return

        keys = pygame.key.get_pressed()
        move_player(keys, self.player)

        self._update_background()
        self._spawn_enemies()
        self._update_entities()
        self._check_collisions()
        self._update_score()

    def _update_background(self):
        self.bg_y_shift += 1
        if self.bg_y_shift >= 0:
            self.bg_y_shift = -HEIGHT

        if self.score > 3000:
            self.bg_y_shift += 2

        if self.score >= 3000 and not self.new_background_activated:
            self.current_image = self.background_img2
            self.background_top = self.background_img2.copy()
            self.new_background_activated = True

        if self.score >= 10000 and self.new_background_activated:
            self.current_image = self.background_img3
            self.background_top = self.background_img3.copy()

        if self.score >= 15000 and self.new_background_activated:
            self.current_image = self.background_img4
            self.background_top = self.background_img4.copy()

        if self.score == 0:
            self.current_image = self.background_img
            self.background_top = self.background_img.copy()
            self.new_background_activated = False

    def _spawn_enemies(self):
        if random.randint(0, 120) == 0:
            enemy_img = random.choice(self.enemy1_img)
            enemy_object = Enemy1(
                random.randint(100, WIDTH - 50),
                random.randint(-HEIGHT, -50),
                enemy_img,
            )
            self.enemy1_group.add(enemy_object)

        if self.score >= 3000 and random.randint(0, 40) == 0 and len(self.enemy2_group) < 2:
            enemy_img = random.choice(self.enemy2_img)
            enemy2_object = Enemy2(
                random.randint(200, WIDTH - 100),
                random.randint(-HEIGHT, -100),
                enemy_img,
            )
            self.enemy2_group.add(enemy2_object)

        if self.score >= 5000 and not self.boss1_spawned:
            pygame.mixer.Sound('game_sounds/warning.mp3').play()
            boss1_object = Boss1(
                random.randint(200, WIDTH - 100),
                random.randint(-HEIGHT, -100),
                self.boss1_img,
            )
            self.boss1_group.add(boss1_object)
            self.boss1_spawned = True

        if self.score >= 10000 and not self.boss2_spawned:
            pygame.mixer.Sound('game_sounds/warning.mp3').play()
            boss2_object = Boss2(
                random.randint(200, WIDTH - 100),
                random.randint(-HEIGHT, -100),
                self.boss2_img,
            )
            self.boss2_group.add(boss2_object)
            self.boss2_spawned = True

        if self.score >= 15000 and not self.boss3_spawned:
            pygame.mixer.Sound('game_sounds/warning.mp3').play()
            boss3_object = Boss3(
                random.randint(200, WIDTH - 100),
                random.randint(-HEIGHT, -100),
                self.boss3_img,
            )
            self.boss3_group.add(boss3_object)
            self.boss3_spawned = True

        if random.randint(0, 60) == 0:
            extra_score = ExtraScore(
                random.randint(50, WIDTH - 50),
                random.randint(-HEIGHT, -50 - self.extra_score_img.get_rect().height),
                self.extra_score_img,
            )
            self.extra_score_group.add(extra_score)

        if self.score > 3000 and random.randint(0, 100) == 0:
            meteor_img = random.choice(self.meteor_imgs)
            meteor_object = Meteors(
                random.randint(0, 50),
                random.randint(0, 50),
                meteor_img,
            )
            self.meteor_group.add(meteor_object)

        if random.randint(0, 90) == 0:
            meteor2_img = random.choice(self.meteor2_imgs)
            meteor2_object = Meteors2(
                random.randint(100, WIDTH - 50),
                random.randint(-HEIGHT, -50 - meteor2_img.get_rect().height),
                meteor2_img,
            )
            self.meteor2_group.add(meteor2_object)

        if self.score > 1000 and random.randint(0, 500) == 0:
            black_hole_img = random.choice(self.black_hole_imgs)
            black_hole_object = BlackHole(
                random.randint(100, WIDTH - 50),
                random.randint(-HEIGHT, -50 - black_hole_img.get_rect().height),
                black_hole_img,
            )
            self.black_hole_group.add(black_hole_object)

    def _update_entities(self):
        for black_hole_object in self.black_hole_group:
            black_hole_object.update()

        for bullet_refill in self.bullet_refill_group:
            bullet_refill.update()

        for health_refill in self.health_refill_group:
            health_refill.update()

        for extra_score in self.extra_score_group:
            extra_score.update()

        for double_refill in self.double_refill_group:
            double_refill.update()

        for meteor_object in self.meteor_group:
            meteor_object.update()

        for meteor2_object in self.meteor2_group:
            meteor2_object.update()

        for enemy_object in self.enemy1_group:
            enemy_object.update(self.enemy1_group)

        for enemy2_object in self.enemy2_group:
            enemy2_object.update(self.enemy2_group, self.enemy2_bullets, self.player)

        self.enemy2_bullets.update()

        for boss1_object in self.boss1_group:
            boss1_object.update(self.boss1_bullets, self.player)
        self.boss1_bullets.update()

        for boss2_object in self.boss2_group:
            boss2_object.update(self.boss2_bullets, self.player)
        self.boss2_bullets.update()

        for boss3_object in self.boss3_group:
            boss3_object.update(self.boss3_bullets, self.player)
        self.boss3_bullets.update()

        for explosion in self.explosions:
            explosion.update()

        for explosion2 in self.explosions2:
            explosion2.update()

        for bullet in self.bullets:
            bullet.update()
            if bullet.rect.bottom < 0:
                bullet.kill()
                self.bullet_counter -= 1

    def _check_collisions(self):
        # Black hole collisions
        for black_hole_object in self.black_hole_group:
            if black_hole_object.rect.colliderect(self.player.rect):
                self.player_life -= 1
                black_hole_object.sound_effect.play()

        # Bullet refill collisions
        for bullet_refill in self.bullet_refill_group:
            if self.player.rect.colliderect(bullet_refill.rect):
                if self.bullet_counter < 200:
                    self.bullet_counter += 50
                    if self.bullet_counter > 200:
                        self.bullet_counter = 200
                bullet_refill.kill()
                bullet_refill.sound_effect.play()

        # Health refill collisions
        for health_refill in self.health_refill_group:
            if self.player.rect.colliderect(health_refill.rect):
                if self.player_life < 200:
                    self.player_life += 50
                    if self.player_life > 200:
                        self.player_life = 200
                health_refill.kill()
                health_refill.sound_effect.play()

        # Extra score collisions
        for extra_score in self.extra_score_group:
            if self.player.rect.colliderect(extra_score.rect):
                self.score += 20
                extra_score.kill()
                extra_score.sound_effect.play()

        # Double refill collisions
        for double_refill in self.double_refill_group:
            if self.player.rect.colliderect(double_refill.rect):
                if self.player_life < 200:
                    self.player_life += 50
                    if self.player_life > 200:
                        self.player_life = 200
                if self.bullet_counter < 200:
                    self.bullet_counter += 50
                    if self.bullet_counter > 200:
                        self.bullet_counter = 200
                double_refill.kill()
                double_refill.sound_effect.play()

        # Meteor collisions
        for meteor_object in self.meteor_group:
            if meteor_object.rect.colliderect(self.player.rect):
                self.player_life -= 10
                explosion = Explosion(meteor_object.rect.center, self.explosion_images)
                self.explosions.add(explosion)
                meteor_object.kill()
                self.score += 50

            bullet_collisions = pygame.sprite.spritecollide(meteor_object, self.bullets, True)
            for _ in bullet_collisions:
                explosion = Explosion(meteor_object.rect.center, self.explosion_images)
                self.explosions.add(explosion)
                meteor_object.kill()
                self.score += 80

                if random.randint(0, 10) == 0:
                    double_refill = DoubleRefill(
                        meteor_object.rect.centerx,
                        meteor_object.rect.centery,
                        self.double_refill_img,
                    )
                    self.double_refill_group.add(double_refill)

        # Meteor2 collisions
        for meteor2_object in self.meteor2_group:
            if meteor2_object.rect.colliderect(self.player.rect):
                self.player_life -= 10
                explosion = Explosion(meteor2_object.rect.center, self.explosion_images)
                self.explosions.add(explosion)
                meteor2_object.kill()
                self.score += 20

            bullet_collisions = pygame.sprite.spritecollide(meteor2_object, self.bullets, True)
            for _ in bullet_collisions:
                explosion = Explosion(meteor2_object.rect.center, self.explosion_images)
                self.explosions.add(explosion)
                meteor2_object.kill()
                self.score += 40

                if random.randint(0, 20) == 0:
                    double_refill = DoubleRefill(
                        meteor2_object.rect.centerx,
                        meteor2_object.rect.centery,
                        self.double_refill_img,
                    )
                    self.double_refill_group.add(double_refill)

        # Enemy1 collisions
        for enemy_object in self.enemy1_group:
            if enemy_object.rect.colliderect(self.player.rect):
                self.player_life -= 10
                explosion = Explosion(enemy_object.rect.center, self.explosion_images)
                self.explosions.add(explosion)
                enemy_object.kill()
                self.score += 20

            bullet_collisions = pygame.sprite.spritecollide(enemy_object, self.bullets, True)
            for _ in bullet_collisions:
                explosion = Explosion(enemy_object.rect.center, self.explosion_images)
                self.explosions.add(explosion)
                enemy_object.kill()
                self.score += 50

                if random.randint(0, 8) == 0:
                    bullet_refill = BulletRefill(
                        enemy_object.rect.centerx,
                        enemy_object.rect.centery,
                        self.bullet_refill_img,
                    )
                    self.bullet_refill_group.add(bullet_refill)

                if random.randint(0, 8) == 0:
                    health_refill = HealthRefill(
                        random.randint(50, WIDTH - 30),
                        random.randint(-HEIGHT, -30),
                        self.health_refill_img,
                    )
                    self.health_refill_group.add(health_refill)

        # Enemy2 collisions
        for enemy2_object in self.enemy2_group:
            if enemy2_object.rect.colliderect(self.player.rect):
                self.player_life -= 40
                explosion2 = Explosion2(enemy2_object.rect.center, self.explosion2_images)
                self.explosions2.add(explosion2)
                enemy2_object.kill()
                self.score += 20

            bullet_collisions = pygame.sprite.spritecollide(enemy2_object, self.bullets, True)
            for _ in bullet_collisions:
                explosion2 = Explosion2(enemy2_object.rect.center, self.explosion2_images)
                self.explosions2.add(explosion2)
                enemy2_object.kill()
                self.score += 80

                if random.randint(0, 20) == 0:
                    double_refill = DoubleRefill(
                        enemy2_object.rect.centerx,
                        enemy2_object.rect.centery,
                        self.double_refill_img,
                    )
                    self.double_refill_group.add(double_refill)

            for enemy2_bullet in self.enemy2_bullets:
                if enemy2_bullet.rect.colliderect(self.player.rect):
                    self.player_life -= 10
                    explosion = Explosion(self.player.rect.center, self.explosion3_images)
                    self.explosions.add(explosion)
                    enemy2_bullet.kill()

        # Boss collisions
        self._check_boss_collisions()

        # Check game over
        if self.player_life <= 0:
            self._handle_game_over()

    def _check_boss_collisions(self):
        # Boss1
        for boss1_object in self.boss1_group:
            if boss1_object.rect.colliderect(self.player.rect):
                self.player_life -= 20
                explosion = Explosion2(boss1_object.rect.center, self.explosion2_images)
                self.explosions2.add(explosion)

            bullet_collisions = pygame.sprite.spritecollide(boss1_object, self.bullets, True)
            for _ in bullet_collisions:
                explosion2 = Explosion(boss1_object.rect.center, self.explosion2_images)
                self.explosions2.add(explosion2)
                self.boss1_health -= 5
                if self.boss1_health <= 0:
                    explosion = Explosion2(boss1_object.rect.center, self.explosion3_images)
                    self.explosions.add(explosion)
                    boss1_object.kill()
                    self.score += 400

            for boss1_bullet in self.boss1_bullets:
                if boss1_bullet.rect.colliderect(self.player.rect):
                    self.player_life -= 20
                    explosion = Explosion(self.player.rect.center, self.explosion3_images)
                    self.explosions.add(explosion)
                    boss1_bullet.kill()

            if self.boss1_health <= 0:
                explosion = Explosion2(boss1_object.rect.center, self.explosion2_images)
                self.explosions2.add(explosion)
                boss1_object.kill()

        # Boss2
        for boss2_object in self.boss2_group:
            if boss2_object.rect.colliderect(self.player.rect):
                self.player_life -= 2
                explosion2 = Explosion2(boss2_object.rect.center, self.explosion2_images)
                self.explosions2.add(explosion2)

            bullet_collisions = pygame.sprite.spritecollide(boss2_object, self.bullets, True)
            for _ in bullet_collisions:
                explosion2 = Explosion2(boss2_object.rect.center, self.explosion2_images)
                self.explosions2.add(explosion2)
                self.boss2_health -= 8
                if self.boss2_health <= 0:
                    explosion2 = Explosion2(boss2_object.rect.center, self.explosion3_images)
                    self.explosions2.add(explosion2)
                    boss2_object.kill()
                    self.score += 800

            for boss2_bullet in self.boss2_bullets:
                if boss2_bullet.rect.colliderect(self.player.rect):
                    self.player_life -= 20
                    explosion = Explosion(self.player.rect.center, self.explosion3_images)
                    self.explosions.add(explosion)
                    boss2_bullet.kill()

            if self.boss2_health <= 0:
                explosion = Explosion2(boss2_object.rect.center, self.explosion2_images)
                self.explosions2.add(explosion)
                boss2_object.kill()

        # Boss3
        for boss3_object in self.boss3_group:
            if boss3_object.rect.colliderect(self.player.rect):
                self.player_life -= 1
                explosion2 = Explosion2(boss3_object.rect.center, self.explosion2_images)
                self.explosions2.add(explosion2)

            bullet_collisions = pygame.sprite.spritecollide(boss3_object, self.bullets, True)
            for _ in bullet_collisions:
                explosion2 = Explosion2(boss3_object.rect.center, self.explosion2_images)
                self.explosions2.add(explosion2)
                self.boss3_health -= 6
                if self.boss3_health <= 0:
                    explosion2 = Explosion2(boss3_object.rect.center, self.explosion3_images)
                    self.explosions2.add(explosion2)
                    boss3_object.kill()
                    self.score += 1000

            for boss3_bullet in self.boss3_bullets:
                if boss3_bullet.rect.colliderect(self.player.rect):
                    self.player_life -= 20
                    explosion = Explosion(self.player.rect.center, self.explosion3_images)
                    self.explosions.add(explosion)
                    boss3_bullet.kill()

            if self.boss3_health <= 0:
                explosion = Explosion2(boss3_object.rect.center, self.explosion2_images)
                self.explosions2.add(explosion)
                boss3_object.kill()

    def _handle_game_over(self):
        show_game_over(self.score)
        self.boss1_spawned = False
        self.boss1_health = 150
        self.boss2_spawned = False
        self.boss2_health = 150
        self.boss3_spawned = False
        self.boss3_health = 200
        self.score = 0
        self.player_life = 200
        self.bullet_counter = 200
        self.player.rect.topleft = self.initial_player_pos
        self.bullets.empty()
        self.bullet_refill_group.empty()
        self.health_refill_group.empty()
        self.double_refill_group.empty()
        self.extra_score_group.empty()
        self.black_hole_group.empty()
        self.meteor_group.empty()
        self.meteor2_group.empty()
        self.enemy1_group.empty()
        self.enemy2_group.empty()
        self.boss1_group.empty()
        self.boss2_group.empty()
        self.boss3_group.empty()
        self.explosions.empty()
        self.explosions2.empty()

    def _update_score(self):
        if self.score > self.hi_score:
            self.hi_score = self.score

    def render(self):
        """Render the current game state."""
        if self.paused:
            font = pygame.font.SysFont('Comic Sans MS', 40)
            text = font.render("PAUSE", True, (255, 255, 255))
            text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
            self.screen.blit(text, text_rect)
            pygame.display.flip()
            return

        # Draw background
        self.screen.blit(self.current_image, (0, self.bg_y_shift))
        background_top_rect = self.background_top.get_rect(topleft=(0, self.bg_y_shift))
        background_top_rect.top = self.bg_y_shift + HEIGHT
        self.screen.blit(self.background_top, background_top_rect)

        # Draw entities
        for black_hole_object in self.black_hole_group:
            black_hole_object.draw(self.screen)

        for bullet_refill in self.bullet_refill_group:
            bullet_refill.draw(self.screen)

        for health_refill in self.health_refill_group:
            health_refill.draw(self.screen)

        for extra_score in self.extra_score_group:
            extra_score.draw(self.screen)

        for double_refill in self.double_refill_group:
            double_refill.draw(self.screen)

        for meteor_object in self.meteor_group:
            meteor_object.draw(self.screen)

        for meteor2_object in self.meteor2_group:
            meteor2_object.draw(self.screen)

        self.enemy1_group.draw(self.screen)
        self.enemy2_group.draw(self.screen)
        self.enemy2_bullets.draw(self.screen)

        self.boss1_group.draw(self.screen)
        self.boss1_bullets.draw(self.screen)

        self.boss2_group.draw(self.screen)
        self.boss2_bullets.draw(self.screen)

        self.boss3_group.draw(self.screen)
        self.boss3_bullets.draw(self.screen)

        # Draw boss health bars
        if self.boss1_group:
            boss1_object = self.boss1_group.sprites()[0]
            self.boss1_health_bar_rect.center = (boss1_object.rect.centerx, boss1_object.rect.top - 5)
            pygame.draw.rect(self.screen, (255, 0, 0), self.boss1_health_bar_rect)
            pygame.draw.rect(self.screen, (0, 255, 0), (self.boss1_health_bar_rect.left, self.boss1_health_bar_rect.top, self.boss1_health, self.boss1_health_bar_rect.height))

        if self.boss2_group:
            boss2_object = self.boss2_group.sprites()[0]
            self.boss2_health_bar_rect.center = (boss2_object.rect.centerx, boss2_object.rect.top - 5)
            pygame.draw.rect(self.screen, (255, 0, 0), self.boss2_health_bar_rect)
            pygame.draw.rect(self.screen, (0, 255, 0), (self.boss2_health_bar_rect.left, self.boss2_health_bar_rect.top, self.boss2_health, self.boss2_health_bar_rect.height))

        if self.boss3_group:
            boss3_object = self.boss3_group.sprites()[0]
            self.boss3_health_bar_rect.center = (boss3_object.rect.centerx, boss3_object.rect.top - 5)
            pygame.draw.rect(self.screen, (255, 0, 0), self.boss3_health_bar_rect)
            pygame.draw.rect(self.screen, (0, 255, 0), (self.boss3_health_bar_rect.left, self.boss3_health_bar_rect.top, self.boss3_health, self.boss3_health_bar_rect.height))

        # Draw player
        player_image_copy = self.player.image.copy()
        self.screen.blit(player_image_copy, self.player.rect)

        # Draw explosions
        for explosion in self.explosions:
            self.screen.blit(explosion.image, explosion.rect)

        for explosion2 in self.explosions2:
            self.screen.blit(explosion2.image, explosion2.rect)

        # Draw bullets
        for bullet in self.bullets:
            self.screen.blit(bullet.image, bullet.rect)

        # Draw UI
        self._render_ui()

        pygame.display.flip()

    def _render_ui(self):
        # Player life bar
        player_life_surface = pygame.Surface((200, 25), pygame.SRCALPHA, 32)
        player_life_surface.set_alpha(216)

        player_life_bar_width = int(self.player_life / 200 * 200)
        player_life_bar_width = max(0, min(player_life_bar_width, 200))

        player_life_bar = pygame.Surface((player_life_bar_width, 30), pygame.SRCALPHA, 32)
        player_life_bar.set_alpha(216)

        life_bar_image = pygame.image.load("images/life_bar.png").convert_alpha()

        if self.player_life > 50:
            player_life_bar.fill((152, 251, 152))
        else:
            player_life_bar.fill((0, 0, 0))

        player_life_surface.blit(life_bar_image, (0, 0))
        player_life_surface.blit(player_life_bar, (35, 0))

        life_x_pos = 10
        self.screen.blit(player_life_surface, (life_x_pos, 10))

        # Bullet counter bar
        bullet_counter_surface = pygame.Surface((200, 25), pygame.SRCALPHA, 32)
        bullet_counter_surface.set_alpha(216)
        bullet_counter_bar = pygame.Surface(((self.bullet_counter / 200) * 200, 30), pygame.SRCALPHA, 32)
        bullet_counter_bar.set_alpha(216)
        bullet_bar_image = pygame.image.load("images/bullet_bar.png").convert_alpha()
        if self.bullet_counter > 50:
            bullet_counter_bar.fill((255, 23, 23))
        else:
            bullet_counter_bar.fill((0, 0, 0))
        bullet_counter_surface.blit(bullet_bar_image, (0, 0))
        bullet_counter_surface.blit(bullet_counter_bar, (35, 0))
        bullet_x_pos = 10
        bullet_y_pos = player_life_surface.get_height() + 20
        self.screen.blit(bullet_counter_surface, (bullet_x_pos, bullet_y_pos))

        # Score
        score_surface = pygame.font.SysFont('Comic Sans MS', 30).render(f'{self.score}', True, (238, 232, 170))
        score_image_rect = score_surface.get_rect()
        score_image_rect.x, score_image_rect.y = WIDTH - score_image_rect.width - self.extra_score_img.get_width() - 10, 10

        self.screen.blit(self.extra_score_img, (score_image_rect.right + 5, score_image_rect.centery - self.extra_score_img.get_height()//2))
        self.screen.blit(score_surface, score_image_rect)

        # Hi-score
        hi_score_surface = pygame.font.SysFont('Comic Sans MS', 20).render(f'HI-SCORE: {self.hi_score}', True, (255, 255, 255))
        hi_score_surface.set_alpha(128)
        hi_score_x_pos = (self.screen.get_width() - hi_score_surface.get_width()) // 2
        hi_score_y_pos = 0
        self.screen.blit(hi_score_surface, (hi_score_x_pos, hi_score_y_pos))

    def run_game_loop(self):
        """Run the main game loop."""
        while self.running and self.state == GameState.PLAYING:
            if not self.handle_events():
                break
            self.update()
            self.render()
            self.clock.tick(FPS)

    def run(self):
        """Run the complete game (menu + game loop)."""
        if self.state == GameState.MENU:
            self.run_menu()

        self.run_game_loop()

        pygame.mixer.music.stop()
        pygame.quit()

    def cleanup(self):
        """Clean up pygame resources."""
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        try:
            pygame.quit()
        except Exception:
            pass


def main():
    game = Game(show_menu=True)
    game.run()
    sys.exit()


if __name__ == "__main__":
    main()
