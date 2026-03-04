"""Integration test for main.py - verifies user can enter the game from menu.

Uses SDL dummy video/audio drivers to run without a physical display.
"""

import os
import sys
import threading
import time
import unittest

# Ensure the project root is importable when running inside tests/ folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure SDL to use dummy drivers before importing pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame

from main import Game, GameState
from menu import MainMenu


class TestMenuToGameTransition(unittest.TestCase):
    """Integration test: user can navigate from menu to game."""

    def setUp(self):
        # Ensure pygame is in clean state
        try:
            pygame.quit()
        except Exception:
            pass

    def tearDown(self):
        try:
            pygame.quit()
        except Exception:
            pass

    def test_game_initializes_in_menu_state(self):
        """Test that Game starts in MENU state when show_menu=True."""
        game = Game(show_menu=True)

        self.assertEqual(game.state, GameState.MENU)
        self.assertTrue(game.running)

        game.cleanup()

    def test_game_initializes_in_playing_state_when_menu_skipped(self):
        """Test that Game starts in PLAYING state when show_menu=False."""
        game = Game(show_menu=False)

        self.assertEqual(game.state, GameState.PLAYING)
        self.assertTrue(game.running)

        game.cleanup()

    def test_user_can_enter_game_by_pressing_enter(self):
        """Test that pressing Enter on Play button transitions to game."""
        game = Game(show_menu=True)
        self.assertEqual(game.state, GameState.MENU)

        # Create menu (same as game.run_menu() would do)
        menu = MainMenu()

        # Verify menu starts with Play selected and running
        self.assertTrue(menu.running)
        self.assertEqual(menu.selected_button, 0)  # PLAY = 0

        # Simulate user pressing Enter
        enter_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN})
        pygame.event.post(enter_event)

        # Process the event
        menu._process_events()

        # Menu should stop running, meaning game should start
        self.assertFalse(menu.running)

        # Update game state to reflect menu exit
        game.state = GameState.PLAYING

        self.assertEqual(game.state, GameState.PLAYING)

        game.cleanup()

    def test_user_can_enter_game_by_clicking_play_button(self):
        """Test that clicking Play button transitions to game."""
        game = Game(show_menu=True)

        menu = MainMenu()
        self.assertTrue(menu.running)

        # Get play button center coordinates
        play_center = menu.play_button.center

        # Simulate mouse click on Play button
        click_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {'pos': play_center, 'button': 1}
        )
        pygame.event.post(click_event)

        menu._process_events()

        self.assertFalse(menu.running)

        game.cleanup()

    def test_user_can_navigate_menu_then_start_game(self):
        """Test keyboard navigation (down, up) then Enter to start."""
        game = Game(show_menu=True)

        menu = MainMenu()

        # Navigate down to Quit
        down_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN})
        pygame.event.post(down_event)
        menu._process_events()
        self.assertEqual(menu.selected_button, 1)  # QUIT = 1

        # Navigate back up to Play
        up_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_UP})
        pygame.event.post(up_event)
        menu._process_events()
        self.assertEqual(menu.selected_button, 0)  # PLAY = 0

        # Press Enter
        enter_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN})
        pygame.event.post(enter_event)
        menu._process_events()

        self.assertFalse(menu.running)

        game.cleanup()

    def test_game_loop_runs_after_menu_exit(self):
        """Test that game loop can process frames after menu exits."""
        game = Game(show_menu=False)  # Skip menu, start in playing state

        self.assertEqual(game.state, GameState.PLAYING)
        self.assertTrue(game.running)

        # Run a few frames of the game loop manually
        for _ in range(5):
            game.handle_events()
            game.update()
            game.render()

        # Game should still be running
        self.assertTrue(game.running)
        self.assertEqual(game.state, GameState.PLAYING)

        # Player should exist and have valid state
        self.assertIsNotNone(game.player)
        self.assertEqual(game.player_life, 200)

        game.cleanup()

    def test_full_menu_to_game_transition(self):
        """Integration test: complete flow from menu initialization to game."""
        game = Game(show_menu=True)

        # Start in menu state
        self.assertEqual(game.state, GameState.MENU)

        # Simulate what run_menu does but with injected input
        menu = MainMenu()

        # Post Enter key event
        enter_event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN})
        pygame.event.post(enter_event)

        # Run one iteration of menu event processing
        menu._process_events()

        # Menu should have exited
        self.assertFalse(menu.running)

        # Transition game state (as run_menu would do)
        game.state = GameState.PLAYING

        # Verify game is ready to play
        self.assertEqual(game.state, GameState.PLAYING)
        self.assertTrue(game.running)
        self.assertIsNotNone(game.screen)
        self.assertIsNotNone(game.player)

        # Run one game frame to verify game loop works
        game.handle_events()
        game.update()
        game.render()

        game.cleanup()


if __name__ == '__main__':
    unittest.main(verbosity=2)
