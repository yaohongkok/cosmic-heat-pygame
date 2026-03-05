import sys
import time

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


class GameLogic:
    """Pure business logic for game state calculations.

    This class contains logic that can be tested without pygame dependencies.
    """

    MAX_HEALTH = 200
    MAX_BULLETS = 200
    REFILL_AMOUNT = 50
    EXTRA_SCORE_VALUE = 20

    # Score thresholds for game progression
    BACKGROUND_2_THRESHOLD = 3000
    BACKGROUND_3_THRESHOLD = 10000
    BACKGROUND_4_THRESHOLD = 15000
    BOSS1_THRESHOLD = 5000
    BOSS2_THRESHOLD = 10000
    BOSS3_THRESHOLD = 15000

    @staticmethod
    def calculate_background_speed(score, base_shift=1):
        """Calculate background scroll speed based on score."""
        if score > 3000:
            return base_shift + 2
        return base_shift

    @staticmethod
    def get_background_index(score):
        """Determine which background image to use based on score.

        Returns:
            int: 0 = initial, 1 = background2, 2 = background3, 3 = background4
        """
        if score >= GameLogic.BACKGROUND_4_THRESHOLD:
            return 3
        elif score >= GameLogic.BACKGROUND_3_THRESHOLD:
            return 2
        elif score >= GameLogic.BACKGROUND_2_THRESHOLD:
            return 1
        return 0

    @staticmethod
    def apply_refill(current_value, refill_amount, max_value):
        """Apply a refill and return new value capped at max."""
        return min(current_value + refill_amount, max_value)

    @staticmethod
    def apply_bullet_refill(current_bullets):
        """Apply bullet refill and return new bullet count."""
        return GameLogic.apply_refill(
            current_bullets, GameLogic.REFILL_AMOUNT, GameLogic.MAX_BULLETS
        )

    @staticmethod
    def apply_health_refill(current_health):
        """Apply health refill and return new health value."""
        return GameLogic.apply_refill(
            current_health, GameLogic.REFILL_AMOUNT, GameLogic.MAX_HEALTH
        )

    @staticmethod
    def apply_double_refill(current_health, current_bullets):
        """Apply double refill (health + bullets) and return new values."""
        new_health = GameLogic.apply_health_refill(current_health)
        new_bullets = GameLogic.apply_bullet_refill(current_bullets)
        return new_health, new_bullets

    @staticmethod
    def calculate_damage(current_health, damage_amount):
        """Calculate health after taking damage."""
        return max(0, current_health - damage_amount)

    @staticmethod
    def is_game_over(player_life):
        """Check if game over condition is met."""
        return player_life <= 0

    @staticmethod
    def update_hi_score(score, hi_score):
        """Update hi-score if current score is higher."""
        return max(score, hi_score)

    @staticmethod
    def should_spawn_boss(score, boss_spawned, threshold):
        """Check if a boss should be spawned."""
        return score >= threshold and not boss_spawned

    @staticmethod
    def calculate_boss_damage(boss_health, damage_per_hit):
        """Calculate boss health after taking damage."""
        return max(0, boss_health - damage_per_hit)

    @staticmethod
    def is_boss_defeated(boss_health):
        """Check if boss is defeated."""
        return boss_health <= 0

    @staticmethod
    def wrap_background_shift(bg_y_shift, height):
        """Wrap background scroll position."""
        if bg_y_shift >= 0:
            return -height
        return bg_y_shift

    @staticmethod
    def should_spawn_by_chance(chance_denominator):
        """Determine if something should spawn based on random chance.

        Args:
            chance_denominator: The denominator for the chance (e.g., 120 means 1/120 chance)

        Returns:
            bool: True if should spawn
        """
        return random.randint(0, chance_denominator) == 0

    @staticmethod
    def should_spawn_enemy2(score, current_count, max_count=2, chance=40):
        """Check if Enemy2 should spawn based on score, count limit, and chance."""
        return (score >= GameLogic.BACKGROUND_2_THRESHOLD and
                current_count < max_count and
                GameLogic.should_spawn_by_chance(chance))

    @staticmethod
    def should_spawn_meteor(score, threshold, chance):
        """Check if a meteor should spawn based on score threshold and chance."""
        return score > threshold and GameLogic.should_spawn_by_chance(chance)


class InputHandler:
    """Handles input event processing and translates to game actions."""

    @staticmethod
    def process_keydown(event, game):
        """Process a KEYDOWN event and return False if game should quit."""
        if event.key == pygame.K_SPACE and not game.paused:
            InputHandler._handle_shoot(game)
            game.is_shooting = True
        elif event.key == pygame.K_ESCAPE:
            game.running = False
            game.state = GameState.QUIT
            return False
        elif event.key == pygame.K_p or event.key == pygame.K_PAUSE:
            game.paused = not game.paused
        elif not game.paused:
            InputHandler._handle_movement_keydown(event, game.player)
        return True

    @staticmethod
    def process_keyup(event, game):
        """Process a KEYUP event."""
        if event.key == pygame.K_SPACE and game.player.original_image is not None:
            game.player.image = game.player.original_image.copy()
            game.is_shooting = False
        elif not game.paused:
            InputHandler._handle_movement_keyup(event, game.player)

    @staticmethod
    def process_joystick_button_down(event, game):
        """Process a JOYBUTTONDOWN event."""
        if event.button == 0 and not game.paused:
            game.is_shooting = True
            if game.bullet_counter > 0:
                bullet = Bullet(game.player.rect.centerx, game.player.rect.top)
                game.bullets.add(bullet)
                game.bullet_counter -= 1
        elif event.button == 7:
            game.paused = not game.paused

    @staticmethod
    def process_joystick_button_up(event, game):
        """Process a JOYBUTTONUP event."""
        if event.button == 0 and game.player.original_image is not None:
            game.is_shooting = False

    @staticmethod
    def _handle_shoot(game):
        """Handle shooting logic."""
        if game.bullet_counter > 0 and pygame.time.get_ticks() - game.last_shot_time > SHOOT_DELAY:
            game.last_shot_time = pygame.time.get_ticks()
            bullet = Bullet(game.player.rect.centerx, game.player.rect.top)
            game.bullets.add(bullet)
            game.bullet_counter -= 1

    @staticmethod
    def _handle_movement_keydown(event, player):
        """Handle movement key press."""
        if event.key == pygame.K_LEFT:
            player.move_left()
        elif event.key == pygame.K_RIGHT:
            player.move_right()
        elif event.key == pygame.K_UP:
            player.move_up()
        elif event.key == pygame.K_DOWN:
            player.move_down()

    @staticmethod
    def _handle_movement_keyup(event, player):
        """Handle movement key release."""
        if event.key == pygame.K_LEFT:
            player.stop_left()
        elif event.key == pygame.K_RIGHT:
            player.stop_right()
        elif event.key == pygame.K_UP:
            player.stop_up()
        elif event.key == pygame.K_DOWN:
            player.stop_down()


class CollisionHandler:
    """Handles collision detection and resolution between game entities."""

    @staticmethod
    def check_player_pickup_collision(player_rect, pickup, on_collect):
        """Check collision between player and a pickup item.

        Args:
            player_rect: Player's rect for collision detection
            pickup: The pickup sprite to check
            on_collect: Callback function to execute on collection

        Returns:
            bool: True if collision occurred
        """
        if player_rect.colliderect(pickup.rect):
            on_collect()
            pickup.kill()
            pickup.sound_effect.play()
            return True
        return False

    @staticmethod
    def check_entity_player_collision(entity, player_rect, damage, on_collision):
        """Check collision between an entity and the player.

        Args:
            entity: The entity sprite to check
            player_rect: Player's rect for collision detection
            damage: Amount of damage to deal
            on_collision: Callback function (entity, damage) -> None

        Returns:
            bool: True if collision occurred
        """
        if entity.rect.colliderect(player_rect):
            on_collision(entity, damage)
            return True
        return False

    @staticmethod
    def check_bullet_collision(entity, bullets, on_hit):
        """Check collision between an entity and bullets.

        Args:
            entity: The entity sprite to check
            bullets: The bullet sprite group
            on_hit: Callback function (entity, collision_count) -> None

        Returns:
            list: List of bullet collisions
        """
        collisions = pygame.sprite.spritecollide(entity, bullets, True)
        if collisions:
            on_hit(entity, len(collisions))
        return collisions


class Game:
    """Main game class that manages the game loop and state."""

    def __init__(self, show_menu=True):
        pygame.init()

        while not pygame.get_init():
            time.sleep(0.1)

        music_background()

        if not pygame.display.get_init():
            pygame.display.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        pygame.font.get_init() or pygame.font.init()

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

        if not pygame.joystick.get_init():
            pygame.joystick.init()

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
                if not InputHandler.process_keydown(event, self):
                    return False
            elif event.type == pygame.KEYUP:
                InputHandler.process_keyup(event, self)
            elif event.type == pygame.JOYBUTTONDOWN:
                InputHandler.process_joystick_button_down(event, self)
            elif event.type == pygame.JOYBUTTONUP:
                InputHandler.process_joystick_button_up(event, self)

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
        self.bg_y_shift += GameLogic.calculate_background_speed(self.score)
        self.bg_y_shift = GameLogic.wrap_background_shift(self.bg_y_shift, HEIGHT)

        bg_index = GameLogic.get_background_index(self.score)
        backgrounds = [
            self.background_img,
            self.background_img2,
            self.background_img3,
            self.background_img4
        ]

        if self.score == 0:
            self.current_image = self.background_img
            self.background_top = self.background_img.copy()
            self.new_background_activated = False
        elif bg_index > 0:
            self.current_image = backgrounds[bg_index]
            self.background_top = backgrounds[bg_index].copy()
            self.new_background_activated = True

    def _spawn_enemies(self):
        """Spawn enemies, bosses, and environmental hazards."""
        self._try_spawn_enemy1()
        self._try_spawn_enemy2()
        self._try_spawn_bosses()
        self._try_spawn_pickups()
        self._try_spawn_hazards()

    def _try_spawn_enemy1(self):
        """Attempt to spawn an Enemy1."""
        if GameLogic.should_spawn_by_chance(120):
            enemy_img = random.choice(self.enemy1_img)
            enemy_object = Enemy1(
                random.randint(100, WIDTH - 50),
                random.randint(-HEIGHT, -50),
                enemy_img,
            )
            self.enemy1_group.add(enemy_object)

    def _try_spawn_enemy2(self):
        """Attempt to spawn an Enemy2 if conditions are met."""
        if GameLogic.should_spawn_enemy2(self.score, len(self.enemy2_group)):
            enemy_img = random.choice(self.enemy2_img)
            enemy2_object = Enemy2(
                random.randint(200, WIDTH - 100),
                random.randint(-HEIGHT, -100),
                enemy_img,
            )
            self.enemy2_group.add(enemy2_object)

    def _try_spawn_bosses(self):
        """Attempt to spawn bosses based on score thresholds."""
        if GameLogic.should_spawn_boss(self.score, self.boss1_spawned, GameLogic.BOSS1_THRESHOLD):
            self._spawn_boss(Boss1, self.boss1_img, self.boss1_group)
            self.boss1_spawned = True

        if GameLogic.should_spawn_boss(self.score, self.boss2_spawned, GameLogic.BOSS2_THRESHOLD):
            self._spawn_boss(Boss2, self.boss2_img, self.boss2_group)
            self.boss2_spawned = True

        if GameLogic.should_spawn_boss(self.score, self.boss3_spawned, GameLogic.BOSS3_THRESHOLD):
            self._spawn_boss(Boss3, self.boss3_img, self.boss3_group)
            self.boss3_spawned = True

    def _spawn_boss(self, boss_class, boss_img, boss_group):
        """Spawn a boss with warning sound."""
        pygame.mixer.Sound('game_sounds/warning.mp3').play()
        boss_object = boss_class(
            random.randint(200, WIDTH - 100),
            random.randint(-HEIGHT, -100),
            boss_img,
        )
        boss_group.add(boss_object)

    def _try_spawn_pickups(self):
        """Attempt to spawn score pickups."""
        if GameLogic.should_spawn_by_chance(60):
            extra_score = ExtraScore(
                random.randint(50, WIDTH - 50),
                random.randint(-HEIGHT, -50 - self.extra_score_img.get_rect().height),
                self.extra_score_img,
            )
            self.extra_score_group.add(extra_score)

    def _try_spawn_hazards(self):
        """Attempt to spawn meteors and black holes."""
        if GameLogic.should_spawn_meteor(self.score, 3000, 100):
            meteor_img = random.choice(self.meteor_imgs)
            meteor_object = Meteors(
                random.randint(0, 50),
                random.randint(0, 50),
                meteor_img,
            )
            self.meteor_group.add(meteor_object)

        if GameLogic.should_spawn_by_chance(90):
            meteor2_img = random.choice(self.meteor2_imgs)
            meteor2_object = Meteors2(
                random.randint(100, WIDTH - 50),
                random.randint(-HEIGHT, -50 - meteor2_img.get_rect().height),
                meteor2_img,
            )
            self.meteor2_group.add(meteor2_object)

        if GameLogic.should_spawn_meteor(self.score, 1000, 500):
            black_hole_img = random.choice(self.black_hole_imgs)
            black_hole_object = BlackHole(
                random.randint(100, WIDTH - 50),
                random.randint(-HEIGHT, -50 - black_hole_img.get_rect().height),
                black_hole_img,
            )
            self.black_hole_group.add(black_hole_object)


    def _update_entities(self):
        """Update all game entities."""
        self._update_pickups_and_hazards()
        self._update_enemies()
        self._update_bosses()
        self._update_effects()
        self._update_bullets()

    def _update_pickups_and_hazards(self):
        """Update pickups and environmental hazards."""
        self.black_hole_group.update()
        self.bullet_refill_group.update()
        self.health_refill_group.update()
        self.extra_score_group.update()
        self.double_refill_group.update()
        self.meteor_group.update()
        self.meteor2_group.update()

    def _update_enemies(self):
        """Update enemy entities."""
        for enemy_object in self.enemy1_group:
            enemy_object.update(self.enemy1_group)

        for enemy2_object in self.enemy2_group:
            enemy2_object.update(self.enemy2_group, self.enemy2_bullets, self.player)

        self.enemy2_bullets.update()

    def _update_bosses(self):
        """Update boss entities and their bullets."""
        for boss1_object in self.boss1_group:
            boss1_object.update(self.boss1_bullets, self.player)
        self.boss1_bullets.update()

        for boss2_object in self.boss2_group:
            boss2_object.update(self.boss2_bullets, self.player)
        self.boss2_bullets.update()

        for boss3_object in self.boss3_group:
            boss3_object.update(self.boss3_bullets, self.player)
        self.boss3_bullets.update()

    def _update_effects(self):
        """Update visual effects."""
        self.explosions.update()
        self.explosions2.update()

    def _update_bullets(self):
        """Update player bullets and handle off-screen cleanup."""
        for bullet in self.bullets:
            bullet.update()
            if bullet.rect.bottom < 0:
                bullet.kill()
                self.bullet_counter -= 1

    def _check_collisions(self):
        """Check all collisions between game entities."""
        self._check_hazard_collisions()
        self._check_pickup_collisions()
        self._check_meteor_collisions()
        self._check_enemy_collisions()
        self._check_boss_collisions()
        self._check_enemy_bullet_collisions()

        if GameLogic.is_game_over(self.player_life):
            self._handle_game_over()

    def _check_hazard_collisions(self):
        """Check collisions with black holes."""
        for black_hole_object in self.black_hole_group:
            if black_hole_object.rect.colliderect(self.player.rect):
                self.player_life -= 1
                black_hole_object.sound_effect.play()

    def _check_pickup_collisions(self):
        """Check collisions with pickups (refills, extra score)."""
        for bullet_refill in self.bullet_refill_group:
            if self.player.rect.colliderect(bullet_refill.rect):
                self.bullet_counter = GameLogic.apply_bullet_refill(self.bullet_counter)
                bullet_refill.kill()
                bullet_refill.sound_effect.play()

        for health_refill in self.health_refill_group:
            if self.player.rect.colliderect(health_refill.rect):
                self.player_life = GameLogic.apply_health_refill(self.player_life)
                health_refill.kill()
                health_refill.sound_effect.play()

        for extra_score in self.extra_score_group:
            if self.player.rect.colliderect(extra_score.rect):
                self.score += GameLogic.EXTRA_SCORE_VALUE
                extra_score.kill()
                extra_score.sound_effect.play()

        for double_refill in self.double_refill_group:
            if self.player.rect.colliderect(double_refill.rect):
                self.player_life, self.bullet_counter = GameLogic.apply_double_refill(
                    self.player_life, self.bullet_counter
                )
                double_refill.kill()
                double_refill.sound_effect.play()

    def _check_meteor_collisions(self):
        """Check collisions with meteors."""
        self._check_meteor_group_collisions(
            self.meteor_group, player_damage=10, collision_score=50, bullet_score=80, drop_chance=10
        )
        self._check_meteor_group_collisions(
            self.meteor2_group, player_damage=10, collision_score=20, bullet_score=40, drop_chance=20
        )

    def _check_meteor_group_collisions(self, meteor_group, player_damage, collision_score, bullet_score, drop_chance):
        """Check collisions for a meteor group."""
        for meteor_object in meteor_group:
            if meteor_object.rect.colliderect(self.player.rect):
                self.player_life -= player_damage
                self._create_explosion(meteor_object.rect.center, self.explosion_images)
                meteor_object.kill()
                self.score += collision_score

            bullet_collisions = pygame.sprite.spritecollide(meteor_object, self.bullets, True)
            for _ in bullet_collisions:
                self._create_explosion(meteor_object.rect.center, self.explosion_images)
                meteor_object.kill()
                self.score += bullet_score
                self._try_drop_double_refill(meteor_object.rect.center, drop_chance)

    def _check_enemy_collisions(self):
        """Check collisions with enemy ships."""
        self._check_enemy1_collisions()
        self._check_enemy2_collisions()

    def _check_enemy1_collisions(self):
        """Check collisions with Enemy1 ships."""
        for enemy_object in self.enemy1_group:
            if enemy_object.rect.colliderect(self.player.rect):
                self.player_life -= 10
                self._create_explosion(enemy_object.rect.center, self.explosion_images)
                enemy_object.kill()
                self.score += 20

            bullet_collisions = pygame.sprite.spritecollide(enemy_object, self.bullets, True)
            for _ in bullet_collisions:
                self._create_explosion(enemy_object.rect.center, self.explosion_images)
                enemy_object.kill()
                self.score += 50
                self._try_drop_bullet_refill(enemy_object.rect.center)
                self._try_drop_health_refill()

    def _check_enemy2_collisions(self):
        """Check collisions with Enemy2 ships."""
        for enemy2_object in self.enemy2_group:
            if enemy2_object.rect.colliderect(self.player.rect):
                self.player_life -= 40
                self._create_explosion2(enemy2_object.rect.center, self.explosion2_images)
                enemy2_object.kill()
                self.score += 20

            bullet_collisions = pygame.sprite.spritecollide(enemy2_object, self.bullets, True)
            for _ in bullet_collisions:
                self._create_explosion2(enemy2_object.rect.center, self.explosion2_images)
                enemy2_object.kill()
                self.score += 80
                self._try_drop_double_refill(enemy2_object.rect.center, 20)

    def _check_enemy_bullet_collisions(self):
        """Check collisions between enemy bullets and player."""
        for enemy2_bullet in self.enemy2_bullets:
            if enemy2_bullet.rect.colliderect(self.player.rect):
                self.player_life -= 10
                self._create_explosion(self.player.rect.center, self.explosion3_images)
                enemy2_bullet.kill()

    def _create_explosion(self, center, images):
        """Create an explosion effect at the given center."""
        explosion = Explosion(center, images)
        self.explosions.add(explosion)

    def _create_explosion2(self, center, images):
        """Create a type 2 explosion effect at the given center."""
        explosion2 = Explosion2(center, images)
        self.explosions2.add(explosion2)

    def _try_drop_double_refill(self, center, chance):
        """Attempt to drop a double refill at the given position."""
        if GameLogic.should_spawn_by_chance(chance):
            double_refill = DoubleRefill(center[0], center[1], self.double_refill_img)
            self.double_refill_group.add(double_refill)

    def _try_drop_bullet_refill(self, center):
        """Attempt to drop a bullet refill at the given position."""
        if GameLogic.should_spawn_by_chance(8):
            bullet_refill = BulletRefill(center[0], center[1], self.bullet_refill_img)
            self.bullet_refill_group.add(bullet_refill)

    def _try_drop_health_refill(self):
        """Attempt to drop a health refill at a random position."""
        if GameLogic.should_spawn_by_chance(8):
            health_refill = HealthRefill(
                random.randint(50, WIDTH - 30),
                random.randint(-HEIGHT, -30),
                self.health_refill_img,
            )
            self.health_refill_group.add(health_refill)


    def _check_boss_collisions(self):
        """Check collisions with all boss entities."""
        self._check_single_boss_collisions(
            self.boss1_group, self.boss1_bullets,
            lambda: self.boss1_health, lambda h: setattr(self, 'boss1_health', h),
            contact_damage=20, bullet_damage=5, defeat_score=400
        )
        self._check_single_boss_collisions(
            self.boss2_group, self.boss2_bullets,
            lambda: self.boss2_health, lambda h: setattr(self, 'boss2_health', h),
            contact_damage=2, bullet_damage=8, defeat_score=800
        )
        self._check_single_boss_collisions(
            self.boss3_group, self.boss3_bullets,
            lambda: self.boss3_health, lambda h: setattr(self, 'boss3_health', h),
            contact_damage=1, bullet_damage=6, defeat_score=1000
        )

    def _check_single_boss_collisions(self, boss_group, boss_bullets, get_health, set_health,
                                       contact_damage, bullet_damage, defeat_score):
        """Check collisions for a single boss type."""
        for boss_object in boss_group:
            # Player contact damage
            if boss_object.rect.colliderect(self.player.rect):
                self.player_life -= contact_damage
                self._create_explosion2(boss_object.rect.center, self.explosion2_images)

            # Bullet hits on boss
            bullet_collisions = pygame.sprite.spritecollide(boss_object, self.bullets, True)
            for _ in bullet_collisions:
                self._create_explosion2(boss_object.rect.center, self.explosion2_images)
                new_health = GameLogic.calculate_boss_damage(get_health(), bullet_damage)
                set_health(new_health)
                if GameLogic.is_boss_defeated(new_health):
                    self._create_explosion(boss_object.rect.center, self.explosion3_images)
                    boss_object.kill()
                    self.score += defeat_score

            # Boss bullets hitting player
            self._check_boss_bullets_hit_player(boss_bullets)

            # Check if boss should be killed
            if GameLogic.is_boss_defeated(get_health()):
                self._create_explosion2(boss_object.rect.center, self.explosion2_images)
                boss_object.kill()

    def _check_boss_bullets_hit_player(self, boss_bullets):
        """Check if boss bullets hit the player."""
        for boss_bullet in boss_bullets:
            if boss_bullet.rect.colliderect(self.player.rect):
                self.player_life -= 20
                self._create_explosion(self.player.rect.center, self.explosion3_images)
                boss_bullet.kill()

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
        self.hi_score = GameLogic.update_hi_score(self.score, self.hi_score)

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
