"""Unit tests for controls.py player movement functions.

These tests verify the control logic for keyboard and joystick input handling.

Forked Test Compatibility:
    Previous implementation used module-level sys.modules manipulation to mock
    pygame, which failed with `pytest --forked` because:
    - Forked processes inherit the parent's module cache
    - The mock key constants (K_LEFT=276) differed from real SDL2 constants
      (K_LEFT=1073741904), causing KeyError when accessing the keys dictionary
    
    The fix uses real pygame key constants when creating test key dictionaries,
    ensuring compatibility regardless of test execution order or forking.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class MockPlayer:
    """Mock player object for testing movement controls.
    
    Tracks which movement methods were called to verify control logic
    without needing a real player sprite.
    """

    def __init__(self, x=100, y=100, width=50, height=50, speed=10):
        self.rect = MagicMock()
        self.rect.x = x
        self.rect.y = y
        self.rect.width = width
        self.rect.height = height
        self.speed = speed
        
        # Movement tracking flags
        self.move_left_called = False
        self.move_right_called = False
        self.move_up_called = False
        self.move_down_called = False
        self.move_up_left_called = False
        self.move_up_right_called = False
        self.move_down_left_called = False
        self.move_down_right_called = False
        self.stop_called = False

    def move_left(self):
        self.move_left_called = True

    def move_right(self):
        self.move_right_called = True

    def move_up(self):
        self.move_up_called = True

    def move_down(self):
        self.move_down_called = True

    def move_up_left(self):
        self.move_up_left_called = True

    def move_up_right(self):
        self.move_up_right_called = True

    def move_down_left(self):
        self.move_down_left_called = True

    def move_down_right(self):
        self.move_down_right_called = True

    def stop(self):
        self.stop_called = True


class TestMovePlayer(unittest.TestCase):
    """Tests for keyboard-based player movement."""

    def _create_keyboard_state(self, left=False, right=False, up=False, down=False):
        """Create a mock keyboard state dictionary using real pygame key constants.
        
        Uses actual pygame.K_* constants to ensure compatibility with the
        controls module, which imports pygame directly.
        """
        import pygame
        return {
            pygame.K_LEFT: left,
            pygame.K_RIGHT: right,
            pygame.K_UP: up,
            pygame.K_DOWN: down,
        }

    def test_move_left(self):
        """Pressing left arrow key calls move_left."""
        from controls import move_player
        player = MockPlayer()
        keyboard_state = self._create_keyboard_state(left=True)

        move_player(keyboard_state, player)

        self.assertTrue(player.move_left_called)
        self.assertFalse(player.move_right_called)
        self.assertFalse(player.stop_called)

    def test_move_right(self):
        """Pressing right arrow key calls move_right."""
        from controls import move_player
        player = MockPlayer()
        keyboard_state = self._create_keyboard_state(right=True)

        move_player(keyboard_state, player)

        self.assertTrue(player.move_right_called)
        self.assertFalse(player.move_left_called)

    def test_move_up(self):
        """Pressing up arrow key calls move_up."""
        from controls import move_player
        player = MockPlayer()
        keyboard_state = self._create_keyboard_state(up=True)

        move_player(keyboard_state, player)

        self.assertTrue(player.move_up_called)
        self.assertFalse(player.move_down_called)

    def test_move_down(self):
        """Pressing down arrow key calls move_down."""
        from controls import move_player
        player = MockPlayer()
        keyboard_state = self._create_keyboard_state(down=True)

        move_player(keyboard_state, player)

        self.assertTrue(player.move_down_called)
        self.assertFalse(player.move_up_called)

    def test_move_up_left(self):
        """Pressing left + up calls move_up_left for diagonal movement."""
        from controls import move_player
        player = MockPlayer()
        keyboard_state = self._create_keyboard_state(left=True, up=True)

        move_player(keyboard_state, player)

        self.assertTrue(player.move_up_left_called)
        self.assertFalse(player.move_left_called)
        self.assertFalse(player.move_up_called)

    def test_move_up_right(self):
        """Pressing right + up calls move_up_right for diagonal movement."""
        from controls import move_player
        player = MockPlayer()
        keyboard_state = self._create_keyboard_state(right=True, up=True)

        move_player(keyboard_state, player)

        self.assertTrue(player.move_up_right_called)
        self.assertFalse(player.move_right_called)
        self.assertFalse(player.move_up_called)

    def test_move_down_left(self):
        """Pressing left + down calls move_down_left for diagonal movement."""
        from controls import move_player
        player = MockPlayer()
        keyboard_state = self._create_keyboard_state(left=True, down=True)

        move_player(keyboard_state, player)

        self.assertTrue(player.move_down_left_called)
        self.assertFalse(player.move_left_called)
        self.assertFalse(player.move_down_called)

    def test_move_down_right(self):
        """Pressing right + down calls move_down_right for diagonal movement."""
        from controls import move_player
        player = MockPlayer()
        keyboard_state = self._create_keyboard_state(right=True, down=True)

        move_player(keyboard_state, player)

        self.assertTrue(player.move_down_right_called)
        self.assertFalse(player.move_right_called)
        self.assertFalse(player.move_down_called)

    def test_no_keys_pressed_stops_player(self):
        """No movement keys pressed calls stop."""
        from controls import move_player
        player = MockPlayer()
        keyboard_state = self._create_keyboard_state()

        move_player(keyboard_state, player)

        self.assertTrue(player.stop_called)
        self.assertFalse(player.move_left_called)
        self.assertFalse(player.move_right_called)
        self.assertFalse(player.move_up_called)
        self.assertFalse(player.move_down_called)

    def test_left_takes_priority_over_right(self):
        """Left key takes priority when both left and right are pressed."""
        from controls import move_player
        player = MockPlayer()
        keyboard_state = self._create_keyboard_state(left=True, right=True)

        move_player(keyboard_state, player)

        self.assertTrue(player.move_left_called)
        self.assertFalse(player.move_right_called)


class TestMovePlayerWithJoystick(unittest.TestCase):
    """Tests for joystick-based player movement."""

    def _create_mock_joystick(self, x_axis=0.0, y_axis=0.0):
        """Create a mock joystick with specified axis values.
        
        Args:
            x_axis: Horizontal axis value (-1.0 to 1.0)
            y_axis: Vertical axis value (-1.0 to 1.0)
        """
        joystick = MagicMock()
        joystick.get_axis.side_effect = lambda axis: x_axis if axis == 0 else y_axis
        return joystick

    def test_joystick_move_right(self):
        """Joystick tilted right moves player right."""
        from controls import move_player_with_joystick
        player = MockPlayer(x=100, y=100)
        joystick = self._create_mock_joystick(x_axis=0.5)

        move_player_with_joystick(joystick, player)

        expected_x = 100 + 0.5 * player.speed
        self.assertEqual(player.rect.x, expected_x)

    def test_joystick_move_left(self):
        """Joystick tilted left moves player left."""
        from controls import move_player_with_joystick
        player = MockPlayer(x=100, y=100)
        joystick = self._create_mock_joystick(x_axis=-0.5)

        move_player_with_joystick(joystick, player)

        expected_x = 100 + (-0.5) * player.speed
        self.assertEqual(player.rect.x, expected_x)

    def test_joystick_move_down(self):
        """Joystick tilted down moves player down."""
        from controls import move_player_with_joystick
        player = MockPlayer(x=100, y=100)
        joystick = self._create_mock_joystick(y_axis=0.8)

        move_player_with_joystick(joystick, player)

        expected_y = 100 + 0.8 * player.speed
        self.assertEqual(player.rect.y, expected_y)

    def test_joystick_move_up(self):
        """Joystick tilted up moves player up."""
        from controls import move_player_with_joystick
        player = MockPlayer(x=100, y=100)
        joystick = self._create_mock_joystick(y_axis=-0.8)

        move_player_with_joystick(joystick, player)

        expected_y = 100 + (-0.8) * player.speed
        self.assertEqual(player.rect.y, expected_y)

    def test_joystick_ignores_small_x_movement_in_deadzone(self):
        """Small joystick X movement within deadzone is ignored."""
        from controls import move_player_with_joystick
        initial_x = 100
        player = MockPlayer(x=initial_x, y=100)
        joystick = self._create_mock_joystick(x_axis=0.05)

        move_player_with_joystick(joystick, player)

        self.assertEqual(player.rect.x, initial_x)

    def test_joystick_ignores_small_y_movement_in_deadzone(self):
        """Small joystick Y movement within deadzone is ignored."""
        from controls import move_player_with_joystick
        initial_y = 100
        player = MockPlayer(x=100, y=initial_y)
        joystick = self._create_mock_joystick(y_axis=0.05)

        move_player_with_joystick(joystick, player)

        self.assertEqual(player.rect.y, initial_y)

    def test_joystick_clamps_at_left_boundary(self):
        """Player cannot move past left screen boundary."""
        from controls import move_player_with_joystick
        player = MockPlayer(x=5, y=100)
        joystick = self._create_mock_joystick(x_axis=-1.0)

        move_player_with_joystick(joystick, player)

        self.assertEqual(player.rect.x, 0)

    def test_joystick_clamps_at_right_boundary(self):
        """Player cannot move past right screen boundary."""
        from controls import move_player_with_joystick
        from classes.constants import WIDTH
        player = MockPlayer(x=WIDTH - 55, y=100, width=50)
        joystick = self._create_mock_joystick(x_axis=1.0)

        move_player_with_joystick(joystick, player)

        self.assertEqual(player.rect.x, WIDTH - player.rect.width)

    def test_joystick_clamps_at_top_boundary(self):
        """Player cannot move past top screen boundary."""
        from controls import move_player_with_joystick
        player = MockPlayer(x=100, y=5)
        joystick = self._create_mock_joystick(y_axis=-1.0)

        move_player_with_joystick(joystick, player)

        self.assertEqual(player.rect.y, 0)

    def test_joystick_clamps_at_bottom_boundary(self):
        """Player cannot move past bottom screen boundary."""
        from controls import move_player_with_joystick
        from classes.constants import HEIGHT
        player = MockPlayer(x=100, y=HEIGHT - 55, height=50)
        joystick = self._create_mock_joystick(y_axis=1.0)

        move_player_with_joystick(joystick, player)

        self.assertEqual(player.rect.y, HEIGHT - player.rect.height)

    def test_joystick_diagonal_movement(self):
        """Joystick tilted diagonally moves player in both axes."""
        from controls import move_player_with_joystick
        player = MockPlayer(x=100, y=100)
        joystick = self._create_mock_joystick(x_axis=0.5, y_axis=0.5)

        move_player_with_joystick(joystick, player)

        expected_x = 100 + 0.5 * player.speed
        expected_y = 100 + 0.5 * player.speed
        self.assertEqual(player.rect.x, expected_x)
        self.assertEqual(player.rect.y, expected_y)


if __name__ == '__main__':
    unittest.main(verbosity=2)