"""Utility functions for Cosmic Heat game."""

import pygame
from classes.constants import WIDTH, HEIGHT


def music_background():
    """Start playing background music in a loop."""
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    pygame.mixer.music.load('game_sounds/background_music.mp3')
    pygame.mixer.music.set_volume(0.25)
    pygame.mixer.music.play(loops=-1)


def render_game_over_screen(screen, score):
    """Render game over text and score onto the given screen surface.

    Args:
        screen: The pygame surface to render on.
        score: The final score to display.
    """
    font = pygame.font.SysFont('Impact', 50)
    font_small = pygame.font.SysFont('Impact', 30)
    text = font.render("GAME OVER", True, (139, 0, 0))
    text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 50))
    score_text = font_small.render(f"Final Score: {score}", True, (255, 255, 255))
    score_rect = score_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
    screen.blit(text, text_rect)
    screen.blit(score_text, score_rect)
    pygame.display.flip()


def play_game_over_sound():
    """Play the game over sound and wait for it to finish."""
    pygame.mixer.music.load('game_sounds/gameover.mp3')
    pygame.mixer.music.play()
    pygame.time.delay(4000)


def show_game_over(score, screen=None):
    """Display game over screen with score and play game over sound.

    Args:
        score: The final score to display.
        screen: Optional pygame surface. If None, uses pygame.display.get_surface().
    """
    if screen is None:
        screen = pygame.display.get_surface()
    render_game_over_screen(screen, score)
    play_game_over_sound()
    music_background()


def render_game_win_screen(screen):
    """Render the win message onto the given screen surface.

    Args:
        screen: The pygame surface to render on.
    """
    font = pygame.font.SysFont('Impact', 50)
    text = font.render("AWESOME! GO ON!", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    screen.blit(text, text_rect)
    pygame.display.flip()


def play_game_win_sound():
    """Play the win sound and wait briefly."""
    pygame.mixer.music.load('game_sounds/win.mp3')
    pygame.mixer.music.play()
    pygame.time.delay(1000)


def show_game_win(screen=None):
    """Display win screen and play win sound.

    Args:
        screen: Optional pygame surface. If None, uses pygame.display.get_surface().
    """
    if screen is None:
        screen = pygame.display.get_surface()
    render_game_win_screen(screen)
    play_game_win_sound()
    music_background()
