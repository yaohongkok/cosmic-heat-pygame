"""Unit tests for functions.py utility functions.

These tests verify rendering and sound logic for game over and win screens.

Forked Test Compatibility:
    Previous implementation used module-level sys.modules manipulation to mock
    pygame, which failed with `pytest --forked` because:
    - Module-level mocks were applied before forking, but the forked process
      inherited the parent's real pygame module
    - Mock assertions failed because the real pygame was called instead
    
    The fix uses @patch('functions.pygame') decorators on each test method,
    which properly patches pygame within the test's execution context
    regardless of process forking.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestMusicBackground(unittest.TestCase):
    """Tests for background music initialization and playback."""

    @patch('functions.pygame')
    def test_initializes_mixer_when_not_initialized(self, mock_pygame):
        """Initializes pygame mixer if not already initialized."""
        mock_pygame.mixer.get_init.return_value = False
        
        from functions import music_background
        music_background()

        mock_pygame.mixer.init.assert_called_once()

    @patch('functions.pygame')
    def test_skips_init_when_mixer_already_initialized(self, mock_pygame):
        """Skips mixer init if already initialized."""
        mock_pygame.mixer.get_init.return_value = True
        
        from functions import music_background
        music_background()

        mock_pygame.mixer.init.assert_not_called()

    @patch('functions.pygame')
    def test_loads_correct_music_file(self, mock_pygame):
        """Loads the background music file from correct path."""
        mock_pygame.mixer.get_init.return_value = True
        
        from functions import music_background
        music_background()

        mock_pygame.mixer.music.load.assert_called_once_with(
            'game_sounds/background_music.mp3'
        )

    @patch('functions.pygame')
    def test_sets_volume_to_quarter(self, mock_pygame):
        """Sets music volume to 0.25 (25%)."""
        mock_pygame.mixer.get_init.return_value = True
        
        from functions import music_background
        music_background()

        mock_pygame.mixer.music.set_volume.assert_called_once_with(0.25)

    @patch('functions.pygame')
    def test_plays_music_in_infinite_loop(self, mock_pygame):
        """Plays music with infinite loop (loops=-1)."""
        mock_pygame.mixer.get_init.return_value = True
        
        from functions import music_background
        music_background()

        mock_pygame.mixer.music.play.assert_called_once_with(loops=-1)


class TestRenderGameOverScreen(unittest.TestCase):
    """Tests for game over screen rendering."""

    def setUp(self):
        """Set up mock objects for rendering tests."""
        self.mock_screen = MagicMock()
        self.mock_title_font = MagicMock()
        self.mock_score_font = MagicMock()
        self.mock_title_surface = MagicMock()
        self.mock_score_surface = MagicMock()

    def _setup_font_mocks(self, mock_pygame):
        """Configure pygame font mocks for game over screen."""
        mock_pygame.font.SysFont.side_effect = [
            self.mock_title_font,
            self.mock_score_font
        ]
        self.mock_title_font.render.return_value = self.mock_title_surface
        self.mock_score_font.render.return_value = self.mock_score_surface
        self.mock_title_surface.get_rect.return_value = MagicMock()
        self.mock_score_surface.get_rect.return_value = MagicMock()

    @patch('functions.pygame')
    def test_creates_title_and_score_fonts(self, mock_pygame):
        """Creates Impact font at size 50 for title and 30 for score."""
        self._setup_font_mocks(mock_pygame)

        from functions import render_game_over_screen
        render_game_over_screen(self.mock_screen, 1000)

        font_calls = mock_pygame.font.SysFont.call_args_list
        self.assertEqual(font_calls[0], call('Impact', 50))
        self.assertEqual(font_calls[1], call('Impact', 30))

    @patch('functions.pygame')
    def test_renders_game_over_text_in_dark_red(self, mock_pygame):
        """Renders 'GAME OVER' text in dark red color."""
        self._setup_font_mocks(mock_pygame)

        from functions import render_game_over_screen
        render_game_over_screen(self.mock_screen, 1000)

        self.mock_title_font.render.assert_called_once_with(
            "GAME OVER", True, (139, 0, 0)
        )

    @patch('functions.pygame')
    def test_renders_final_score_in_white(self, mock_pygame):
        """Renders final score text in white color."""
        self._setup_font_mocks(mock_pygame)

        from functions import render_game_over_screen
        render_game_over_screen(self.mock_screen, 1000)

        self.mock_score_font.render.assert_called_once_with(
            "Final Score: 1000", True, (255, 255, 255)
        )

    @patch('functions.pygame')
    def test_blits_title_and_score_to_screen(self, mock_pygame):
        """Blits both title and score surfaces to screen."""
        self._setup_font_mocks(mock_pygame)

        from functions import render_game_over_screen
        render_game_over_screen(self.mock_screen, 1000)

        self.assertEqual(self.mock_screen.blit.call_count, 2)

    @patch('functions.pygame')
    def test_flips_display_after_rendering(self, mock_pygame):
        """Flips display to show rendered content."""
        self._setup_font_mocks(mock_pygame)

        from functions import render_game_over_screen
        render_game_over_screen(self.mock_screen, 1000)

        mock_pygame.display.flip.assert_called_once()


class TestPlayGameOverSound(unittest.TestCase):
    """Tests for game over sound playback."""

    @patch('functions.pygame')
    def test_loads_game_over_sound_file(self, mock_pygame):
        """Loads the game over sound from correct path."""
        from functions import play_game_over_sound
        play_game_over_sound()

        mock_pygame.mixer.music.load.assert_called_once_with(
            'game_sounds/gameover.mp3'
        )

    @patch('functions.pygame')
    def test_plays_game_over_sound(self, mock_pygame):
        """Plays the game over sound."""
        from functions import play_game_over_sound
        play_game_over_sound()

        mock_pygame.mixer.music.play.assert_called_once()

    @patch('functions.pygame')
    def test_delays_for_four_seconds(self, mock_pygame):
        """Delays for 4000ms (4 seconds) to let sound play."""
        from functions import play_game_over_sound
        play_game_over_sound()

        mock_pygame.time.delay.assert_called_once_with(4000)


class TestRenderGameWinScreen(unittest.TestCase):
    """Tests for win screen rendering."""

    def setUp(self):
        """Set up mock objects for rendering tests."""
        self.mock_screen = MagicMock()
        self.mock_font = MagicMock()
        self.mock_text_surface = MagicMock()

    @patch('functions.pygame')
    def test_creates_impact_font_at_size_50(self, mock_pygame):
        """Creates Impact font at size 50 for win message."""
        mock_pygame.font.SysFont.return_value = self.mock_font
        self.mock_font.render.return_value = self.mock_text_surface
        self.mock_text_surface.get_rect.return_value = MagicMock()

        from functions import render_game_win_screen
        render_game_win_screen(self.mock_screen)

        mock_pygame.font.SysFont.assert_called_once_with('Impact', 50)

    @patch('functions.pygame')
    def test_renders_win_message_in_white(self, mock_pygame):
        """Renders 'AWESOME! GO ON!' text in white color."""
        mock_pygame.font.SysFont.return_value = self.mock_font
        self.mock_font.render.return_value = self.mock_text_surface
        self.mock_text_surface.get_rect.return_value = MagicMock()

        from functions import render_game_win_screen
        render_game_win_screen(self.mock_screen)

        self.mock_font.render.assert_called_once_with(
            "AWESOME! GO ON!", True, (255, 255, 255)
        )

    @patch('functions.pygame')
    def test_blits_win_message_to_screen(self, mock_pygame):
        """Blits win message surface to screen."""
        mock_pygame.font.SysFont.return_value = self.mock_font
        self.mock_font.render.return_value = self.mock_text_surface
        self.mock_text_surface.get_rect.return_value = MagicMock()

        from functions import render_game_win_screen
        render_game_win_screen(self.mock_screen)

        self.mock_screen.blit.assert_called_once()


class TestPlayGameWinSound(unittest.TestCase):
    """Tests for win sound playback."""

    @patch('functions.pygame')
    def test_loads_win_sound_file(self, mock_pygame):
        """Loads the win sound from correct path."""
        from functions import play_game_win_sound
        play_game_win_sound()

        mock_pygame.mixer.music.load.assert_called_once_with('game_sounds/win.mp3')

    @patch('functions.pygame')
    def test_plays_win_sound(self, mock_pygame):
        """Plays the win sound."""
        from functions import play_game_win_sound
        play_game_win_sound()

        mock_pygame.mixer.music.play.assert_called_once()

    @patch('functions.pygame')
    def test_delays_for_one_second(self, mock_pygame):
        """Delays for 1000ms (1 second) to let sound play."""
        from functions import play_game_win_sound
        play_game_win_sound()

        mock_pygame.time.delay.assert_called_once_with(1000)


class TestShowGameOver(unittest.TestCase):
    """Tests for the complete show_game_over orchestration function."""

    @patch('functions.render_game_over_screen')
    @patch('functions.play_game_over_sound')
    @patch('functions.music_background')
    def test_calls_render_sound_and_music_functions(
        self, mock_music_background, mock_play_sound, mock_render_screen
    ):
        """Calls all component functions in correct order."""
        mock_screen = MagicMock()

        from functions import show_game_over
        show_game_over(1500, screen=mock_screen)

        mock_render_screen.assert_called_once_with(mock_screen, 1500)
        mock_play_sound.assert_called_once()
        mock_music_background.assert_called_once()

    @patch('functions.pygame')
    @patch('functions.render_game_over_screen')
    @patch('functions.play_game_over_sound')
    @patch('functions.music_background')
    def test_gets_display_surface_when_screen_is_none(
        self, mock_music_background, mock_play_sound, mock_render_screen, mock_pygame
    ):
        """Gets current display surface when no screen is provided."""
        mock_pygame.display.get_surface.return_value = MagicMock()
        
        from functions import show_game_over
        show_game_over(1000, screen=None)

        mock_pygame.display.get_surface.assert_called_once()


class TestShowGameWin(unittest.TestCase):
    """Tests for the complete show_game_win orchestration function."""

    @patch('functions.render_game_win_screen')
    @patch('functions.play_game_win_sound')
    @patch('functions.music_background')
    def test_calls_render_sound_and_music_functions(
        self, mock_music_background, mock_play_sound, mock_render_screen
    ):
        """Calls all component functions in correct order."""
        mock_screen = MagicMock()

        from functions import show_game_win
        show_game_win(screen=mock_screen)

        mock_render_screen.assert_called_once_with(mock_screen)
        mock_play_sound.assert_called_once()
        mock_music_background.assert_called_once()

    @patch('functions.pygame')
    @patch('functions.render_game_win_screen')
    @patch('functions.play_game_win_sound')
    @patch('functions.music_background')
    def test_gets_display_surface_when_screen_is_none(
        self, mock_music_background, mock_play_sound, mock_render_screen, mock_pygame
    ):
        """Gets current display surface when no screen is provided."""
        mock_pygame.display.get_surface.return_value = MagicMock()
        
        from functions import show_game_win
        show_game_win(screen=None)

        mock_pygame.display.get_surface.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)