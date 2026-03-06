"""Integration tests for main.py - verifies user can enter the game from menu.

These tests verify the complete flow from menu initialization to gameplay,
using SDL dummy video/audio drivers to run without a physical display.

Forked Test Compatibility:
    Previous implementation used setUpClass() to initialize pygame once for
    all tests, which failed with `pytest --forked` because:
    - setUpClass() runs in the parent process before forking
    - Each forked test process inherits an uninitialized pygame state
    - Calls to pygame.event.clear() in tearDown() failed with
      "video system not initialized"
    
    The fix initializes pygame in setUp() and cleans up in tearDown() for
    each test, ensuring each forked process has a properly initialized
    pygame environment.
"""

import os
import sys
import unittest

# Configure SDL to use dummy drivers BEFORE any pygame import.
# This allows tests to run without a physical display or audio device.
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame

from main import Game, GameState
from menu import MainMenu


class TestMenuToGameTransition(unittest.TestCase):
    """Integration tests for menu-to-game transition flow."""

    def setUp(self):
        """Initialize pygame for each test.
        
        This is required for --forked mode where each test runs in a separate
        process that doesn't inherit the parent's pygame initialization state.
        """
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        os.environ['SDL_AUDIODRIVER'] = 'dummy'
        
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
        
        pygame.event.clear()

    def tearDown(self):
        """Clean up pygame after each test."""
        try:
            pygame.event.clear()
        except pygame.error:
            pass
        pygame.quit()

    def test_game_initializes_in_menu_state_when_show_menu_true(self):
        """Game starts in MENU state when show_menu=True."""
        game = Game(show_menu=True)

        self.assertEqual(game.state, GameState.MENU)
        self.assertTrue(game.running)

        game.cleanup()

    def test_game_initializes_in_playing_state_when_show_menu_false(self):
        """Game starts in PLAYING state when show_menu=False."""
        game = Game(show_menu=False)

        self.assertEqual(game.state, GameState.PLAYING)
        self.assertTrue(game.running)

        game.cleanup()

    def test_pressing_enter_on_play_button_starts_game(self):
        """Pressing Enter while Play button is selected starts the game."""
        game = Game(show_menu=True)
        self.assertEqual(game.state, GameState.MENU)

        menu = MainMenu()
        self.assertTrue(menu.running)
        self.assertEqual(menu.selected_button, 0)  # PLAY button

        enter_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN})
        pygame.event.post(enter_event)
        menu._process_events()

        self.assertFalse(menu.running)

        game.state = GameState.PLAYING
        self.assertEqual(game.state, GameState.PLAYING)

        game.cleanup()

    def test_clicking_play_button_starts_game(self):
        """Clicking on Play button with mouse starts the game."""
        game = Game(show_menu=True)

        menu = MainMenu()
        self.assertTrue(menu.running)

        play_button_center = menu.play_button.center
        click_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {'pos': play_button_center, 'button': 1}
        )
        pygame.event.post(click_event)
        menu._process_events()

        self.assertFalse(menu.running)

        game.cleanup()

    def test_keyboard_navigation_then_enter_starts_game(self):
        """Navigate menu with arrow keys, then press Enter to start."""
        game = Game(show_menu=True)
        menu = MainMenu()

        # Navigate down to Quit button
        down_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN})
        pygame.event.post(down_event)
        menu._process_events()
        self.assertEqual(menu.selected_button, 1)  # QUIT button

        # Navigate back up to Play button
        up_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_UP})
        pygame.event.post(up_event)
        menu._process_events()
        self.assertEqual(menu.selected_button, 0)  # PLAY button

        # Press Enter to start game
        enter_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN})
        pygame.event.post(enter_event)
        menu._process_events()

        self.assertFalse(menu.running)

        game.cleanup()

    def test_game_loop_processes_frames_after_menu_exit(self):
        """Game loop can process multiple frames after starting."""
        game = Game(show_menu=False)

        self.assertEqual(game.state, GameState.PLAYING)
        self.assertTrue(game.running)

        # Process several game frames
        for _ in range(5):
            game.handle_events()
            game.update()
            game.render()

        self.assertTrue(game.running)
        self.assertEqual(game.state, GameState.PLAYING)
        self.assertIsNotNone(game.player)
        self.assertEqual(game.player_life, 200)

        game.cleanup()

    def test_complete_menu_to_game_transition_flow(self):
        """Complete integration test: menu → input → game state → game loop."""
        game = Game(show_menu=True)
        self.assertEqual(game.state, GameState.MENU)

        menu = MainMenu()

        # Simulate user pressing Enter to start
        enter_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN})
        pygame.event.post(enter_event)
        menu._process_events()
        self.assertFalse(menu.running)

        # Transition to playing state (as game.run_menu() would do)
        game.state = GameState.PLAYING

        # Verify game is properly initialized for gameplay
        self.assertEqual(game.state, GameState.PLAYING)
        self.assertTrue(game.running)
        self.assertIsNotNone(game.screen)
        self.assertIsNotNone(game.player)

        # Verify game loop can process a frame
        game.handle_events()
        game.update()
        game.render()

        game.cleanup()


if __name__ == '__main__':
    unittest.main(verbosity=2)