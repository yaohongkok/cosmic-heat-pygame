"""Unit tests for functions.py utility functions.

These tests mock pygame to test rendering and sound logic without requiring a display.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch, call

# Remove pygame from sys.modules to ensure clean mock
for _mod in list(sys.modules.keys()):
    if _mod == 'pygame' or _mod.startswith('pygame.'):
        del sys.modules[_mod]

# Create comprehensive pygame mock
mock_pygame = MagicMock()
mock_pygame.mixer = MagicMock()
mock_pygame.font = MagicMock()
mock_pygame.display = MagicMock()
mock_pygame.time = MagicMock()

sys.modules['pygame'] = mock_pygame
sys.modules['pygame.mixer'] = mock_pygame.mixer
sys.modules['pygame.font'] = mock_pygame.font
sys.modules['pygame.display'] = mock_pygame.display
sys.modules['pygame.time'] = mock_pygame.time

import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions import (
    music_background,
    render_game_over_screen,
    render_game_win_screen,
    play_game_over_sound,
    play_game_win_sound,
    show_game_over,
    show_game_win,
)
from classes.constants import WIDTH, HEIGHT


class TestMusicBackground(unittest.TestCase):
    """Tests for background music function."""

    def setUp(self):
        mock_pygame.mixer.reset_mock()

    def test_music_background_initializes_mixer(self):
        """Music background initializes mixer if not initialized."""
        mock_pygame.mixer.get_init.return_value = False

        music_background()

        mock_pygame.mixer.init.assert_called_once()

    def test_music_background_skips_init_if_already_initialized(self):
        """Music background skips init if already initialized."""
        mock_pygame.mixer.get_init.return_value = True

        music_background()

        mock_pygame.mixer.init.assert_not_called()

    def test_music_background_loads_correct_file(self):
        """Music background loads the correct audio file."""
        mock_pygame.mixer.get_init.return_value = True

        music_background()

        mock_pygame.mixer.music.load.assert_called_once_with(
            'game_sounds/background_music.mp3'
        )

    def test_music_background_sets_volume(self):
        """Music background sets correct volume."""
        mock_pygame.mixer.get_init.return_value = True

        music_background()

        mock_pygame.mixer.music.set_volume.assert_called_once_with(0.25)

    def test_music_background_plays_in_loop(self):
        """Music background plays in infinite loop."""
        mock_pygame.mixer.get_init.return_value = True

        music_background()

        mock_pygame.mixer.music.play.assert_called_once_with(loops=-1)


class TestRenderGameOverScreen(unittest.TestCase):
    """Tests for game over screen rendering."""

    def setUp(self):
        mock_pygame.font.reset_mock()
        mock_pygame.font.SysFont.reset_mock()
        mock_pygame.font.SysFont.side_effect = None
        mock_pygame.display.reset_mock()
        self.mock_screen = MagicMock()
        self.mock_font = MagicMock()
        self.mock_font_small = MagicMock()
        self.mock_text = MagicMock()
        self.mock_score_text = MagicMock()

    def _setup_font_mocks(self):
        """Helper to set up font mocks for game over screen."""
        mock_pygame.font.SysFont.side_effect = [self.mock_font, self.mock_font_small]
        self.mock_font.render.return_value = self.mock_text
        self.mock_font_small.render.return_value = self.mock_score_text
        self.mock_text.get_rect.return_value = MagicMock()
        self.mock_score_text.get_rect.return_value = MagicMock()

    def test_render_game_over_creates_fonts(self):
        """Game over screen creates correct fonts."""
        self._setup_font_mocks()

        render_game_over_screen(self.mock_screen, 1000)

        calls = mock_pygame.font.SysFont.call_args_list
        self.assertEqual(calls[0], call('Impact', 50))
        self.assertEqual(calls[1], call('Impact', 30))

    def test_render_game_over_renders_text(self):
        """Game over screen renders game over text."""
        self._setup_font_mocks()

        render_game_over_screen(self.mock_screen, 1000)

        self.mock_font.render.assert_called_once_with(
            "GAME OVER", True, (139, 0, 0)
        )

    def test_render_game_over_renders_score(self):
        """Game over screen renders score text."""
        self._setup_font_mocks()

        render_game_over_screen(self.mock_screen, 1000)

        self.mock_font_small.render.assert_called_once_with(
            "Final Score: 1000", True, (255, 255, 255)
        )

    def test_render_game_over_blits_to_screen(self):
        """Game over screen blits text to screen."""
        self._setup_font_mocks()

        render_game_over_screen(self.mock_screen, 1000)

        self.assertEqual(self.mock_screen.blit.call_count, 2)

    def test_render_game_over_flips_display(self):
        """Game over screen flips display."""
        self._setup_font_mocks()

        render_game_over_screen(self.mock_screen, 1000)

        mock_pygame.display.flip.assert_called_once()


class TestPlayGameOverSound(unittest.TestCase):
    """Tests for game over sound playback."""

    def setUp(self):
        mock_pygame.mixer.reset_mock()
        mock_pygame.time.reset_mock()

    def test_play_game_over_sound_loads_file(self):
        """Game over sound loads correct file."""
        play_game_over_sound()

        mock_pygame.mixer.music.load.assert_called_once_with(
            'game_sounds/gameover.mp3'
        )

    def test_play_game_over_sound_plays(self):
        """Game over sound plays."""
        play_game_over_sound()

        mock_pygame.mixer.music.play.assert_called_once()

    def test_play_game_over_sound_delays(self):
        """Game over sound delays for 4 seconds."""
        play_game_over_sound()

        mock_pygame.time.delay.assert_called_once_with(4000)


class TestRenderGameWinScreen(unittest.TestCase):
    """Tests for win screen rendering."""

    def setUp(self):
        mock_pygame.font.reset_mock()
        mock_pygame.font.SysFont.reset_mock()
        mock_pygame.font.SysFont.side_effect = None
        mock_pygame.display.reset_mock()
        self.mock_screen = MagicMock()
        self.mock_font = MagicMock()
        self.mock_text = MagicMock()

    def test_render_win_screen_creates_font(self):
        """Win screen creates correct font."""
        mock_pygame.font.SysFont.return_value = self.mock_font
        self.mock_font.render.return_value = self.mock_text
        self.mock_text.get_rect.return_value = MagicMock()

        render_game_win_screen(self.mock_screen)

        mock_pygame.font.SysFont.assert_called_once_with('Impact', 50)

    def test_render_win_screen_renders_text(self):
        """Win screen renders win text."""
        mock_pygame.font.SysFont.return_value = self.mock_font
        self.mock_font.render.return_value = self.mock_text
        self.mock_text.get_rect.return_value = MagicMock()

        render_game_win_screen(self.mock_screen)

        self.mock_font.render.assert_called_once_with(
            "AWESOME! GO ON!", True, (255, 255, 255)
        )

    def test_render_win_screen_blits_to_screen(self):
        """Win screen blits text to screen."""
        mock_pygame.font.SysFont.return_value = self.mock_font
        self.mock_font.render.return_value = self.mock_text
        mock_text_rect = MagicMock()
        self.mock_text.get_rect.return_value = mock_text_rect

        render_game_win_screen(self.mock_screen)

        self.mock_screen.blit.assert_called_once()


class TestPlayGameWinSound(unittest.TestCase):
    """Tests for win sound playback."""

    def setUp(self):
        mock_pygame.mixer.reset_mock()
        mock_pygame.time.reset_mock()

    def test_play_win_sound_loads_file(self):
        """Win sound loads correct file."""
        play_game_win_sound()

        mock_pygame.mixer.music.load.assert_called_once_with('game_sounds/win.mp3')

    def test_play_win_sound_plays(self):
        """Win sound plays."""
        play_game_win_sound()

        mock_pygame.mixer.music.play.assert_called_once()

    def test_play_win_sound_delays(self):
        """Win sound delays for 1 second."""
        play_game_win_sound()

        mock_pygame.time.delay.assert_called_once_with(1000)


class TestShowGameOver(unittest.TestCase):
    """Tests for the complete show_game_over function."""

    def setUp(self):
        mock_pygame.reset_mock()
        mock_pygame.display.get_surface.return_value = MagicMock()

    @patch('functions.render_game_over_screen')
    @patch('functions.play_game_over_sound')
    @patch('functions.music_background')
    def test_show_game_over_calls_all_functions(
        self, mock_music, mock_sound, mock_render
    ):
        """Show game over calls all necessary functions."""
        mock_screen = MagicMock()

        show_game_over(1500, screen=mock_screen)

        mock_render.assert_called_once_with(mock_screen, 1500)
        mock_sound.assert_called_once()
        mock_music.assert_called_once()

    @patch('functions.render_game_over_screen')
    @patch('functions.play_game_over_sound')
    @patch('functions.music_background')
    def test_show_game_over_gets_surface_when_none(
        self, mock_music, mock_sound, mock_render
    ):
        """Show game over gets display surface when screen is None."""
        show_game_over(1000, screen=None)

        mock_pygame.display.get_surface.assert_called_once()


class TestShowGameWin(unittest.TestCase):
    """Tests for the complete show_game_win function."""

    def setUp(self):
        mock_pygame.reset_mock()
        mock_pygame.display.get_surface.return_value = MagicMock()

    @patch('functions.render_game_win_screen')
    @patch('functions.play_game_win_sound')
    @patch('functions.music_background')
    def test_show_game_win_calls_all_functions(
        self, mock_music, mock_sound, mock_render
    ):
        """Show game win calls all necessary functions."""
        mock_screen = MagicMock()

        show_game_win(screen=mock_screen)

        mock_render.assert_called_once_with(mock_screen)
        mock_sound.assert_called_once()
        mock_music.assert_called_once()

    @patch('functions.render_game_win_screen')
    @patch('functions.play_game_win_sound')
    @patch('functions.music_background')
    def test_show_game_win_gets_surface_when_none(
        self, mock_music, mock_sound, mock_render
    ):
        """Show game win gets display surface when screen is None."""
        show_game_win(screen=None)

        mock_pygame.display.get_surface.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)
