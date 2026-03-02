"""Main menu module for Cosmic Heat game."""

import sys
import random
from enum import IntEnum
from typing import Optional

import pygame
import pygame.mixer

from classes.constants import WIDTH, HEIGHT, BLACK, WHITE, RED


class MenuButton(IntEnum):
    """Enum representing menu button indices."""
    PLAY = 0
    QUIT = 1


class MainMenu:
    """Main menu screen for the game."""

    BUTTON_WIDTH = 205
    BUTTON_HEIGHT = 50
    ANIMATION_FRAMES = 20
    ANIMATION_SHAKE_RANGE = 5
    MUSIC_VOLUME = 0.25
    NUM_AUDIO_CHANNELS = 20

    def __init__(self):
        self._init_pygame()
        self._load_assets()
        self._init_buttons()
        self._init_joystick()
        self.selected_button = MenuButton.PLAY
        self.running = True

    def _init_pygame(self) -> None:
        """Initialize pygame and audio system."""
        pygame.mixer.init()
        pygame.init()
        pygame.mixer.set_num_channels(self.NUM_AUDIO_CHANNELS)
        for i in range(self.NUM_AUDIO_CHANNELS):
            channel = pygame.mixer.Channel(i)
            channel.set_volume(self.MUSIC_VOLUME)

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Main Menu")
        self.clock = pygame.time.Clock()

    def _load_assets(self) -> None:
        """Load images and sounds."""
        self.background = pygame.image.load('images/mainmenu.jpg').convert()
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))

        self.logo = pygame.image.load('images/ch.png').convert_alpha()
        self.logo_pos = ((WIDTH - self.logo.get_width()) // 2, 50)

        self.explosion_sound = pygame.mixer.Sound('game_sounds/explosions/explosion1.wav')
        self.explosion_sound.set_volume(self.MUSIC_VOLUME)

        self.font = pygame.font.SysFont('Comic Sans MS', 40)

        self._start_music()

    def _start_music(self) -> None:
        """Start playing menu music."""
        pygame.mixer.music.load('game_sounds/menu.mp3')
        pygame.mixer.music.set_volume(self.MUSIC_VOLUME)
        pygame.mixer.music.play(-1)

    def _init_buttons(self) -> None:
        """Initialize menu button rectangles."""
        center_x = WIDTH // 2 - self.BUTTON_WIDTH // 2 + 2
        self.play_button = pygame.Rect(
            center_x,
            HEIGHT // 2 - 25,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT
        )
        self.quit_button = pygame.Rect(
            center_x,
            HEIGHT // 2 + 50,
            self.BUTTON_WIDTH,
            self.BUTTON_HEIGHT
        )

    def _init_joystick(self) -> None:
        """Initialize joystick if available."""
        self.joystick: Optional[pygame.joystick.Joystick] = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

    def _animate_transition(self) -> None:
        """Play screen shake animation before starting game."""
        for _ in range(self.ANIMATION_FRAMES):
            self.screen.blit(self.background, (0, 0))
            pygame.display.flip()
            pygame.time.wait(10)

            offset_x = random.randint(-self.ANIMATION_SHAKE_RANGE, self.ANIMATION_SHAKE_RANGE)
            offset_y = random.randint(-self.ANIMATION_SHAKE_RANGE, self.ANIMATION_SHAKE_RANGE)
            self.screen.blit(self.background, (offset_x, offset_y))
            pygame.display.flip()
            pygame.time.wait(10)

    def _start_game(self) -> None:
        """Transition to the main game."""
        self.explosion_sound.play()
        self._animate_transition()
        self.screen.fill(BLACK)
        self.running = False

    def _quit_game(self) -> None:
        """Exit the application."""
        pygame.quit()
        sys.exit()

    def _execute_selected_action(self) -> None:
        """Execute the action for the currently selected button."""
        if self.selected_button == MenuButton.PLAY:
            self._start_game()
        elif self.selected_button == MenuButton.QUIT:
            self._quit_game()

    def _handle_mouse_click(self, pos: tuple[int, int]) -> None:
        """Handle mouse click events."""
        if self.play_button.collidepoint(pos):
            self._start_game()
        elif self.quit_button.collidepoint(pos):
            self._quit_game()

    def _handle_keyboard(self, event: pygame.event.Event) -> None:
        """Handle keyboard input events."""
        if event.key == pygame.K_UP:
            self.selected_button = MenuButton.PLAY
        elif event.key == pygame.K_DOWN:
            self.selected_button = MenuButton.QUIT
        elif event.key == pygame.K_RETURN:
            self._execute_selected_action()

    def _handle_joystick_button(self, event: pygame.event.Event) -> None:
        """Handle joystick button press events."""
        if event.button == 0:
            self._execute_selected_action()

    def _handle_joystick_hat(self, event: pygame.event.Event) -> None:
        """Handle joystick hat (d-pad) motion events."""
        if event.value[1] == 1:
            self.selected_button = MenuButton.PLAY
        elif event.value[1] == -1:
            self.selected_button = MenuButton.QUIT

    def _process_events(self) -> None:
        """Process all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                self._handle_keyboard(event)
            elif self.joystick:
                if event.type == pygame.JOYBUTTONDOWN:
                    self._handle_joystick_button(event)
                elif event.type == pygame.JOYHATMOTION:
                    self._handle_joystick_hat(event)

    def _draw_button(self, rect: pygame.Rect, text: str, is_selected: bool) -> None:
        """Draw a menu button with optional selection highlight."""
        pygame.draw.rect(self.screen, BLACK, rect, border_radius=10)
        if is_selected:
            pygame.draw.rect(self.screen, RED, rect, border_radius=10, width=4)

        text_surface = self.font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def _render(self) -> None:
        """Render the menu screen."""
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.logo, self.logo_pos)

        self._draw_button(
            self.play_button,
            "Play",
            self.selected_button == MenuButton.PLAY
        )
        self._draw_button(
            self.quit_button,
            "Exit",
            self.selected_button == MenuButton.QUIT
        )

        pygame.display.flip()

    def run(self) -> None:
        """Main menu loop."""
        while self.running:
            self._process_events()
            self._render()
            self.clock.tick(60)


# Module-level state
show_menu = True
_menu_has_run = False


def main() -> None:
    """
    Entry point called by main.py.

    The menu runs automatically when this module is imported.
    This function exists for compatibility with main.py's call to menu.main().
    It's a no-op since the menu has already run.
    """
    pass


# Run menu when module is imported (matches original behavior)
# This executes once when main.py does "import menu"
_menu = MainMenu()
_menu.run()
_menu_has_run = True
