"""Unit tests for controls.py player movement functions.

These tests mock pygame to test the control logic without requiring a display.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

# Remove pygame from sys.modules to ensure clean mock
for _mod in list(sys.modules.keys()):
    if _mod == 'pygame' or _mod.startswith('pygame.'):
        del sys.modules[_mod]

# Create pygame mock
mock_pygame = MagicMock()
mock_pygame.K_LEFT = 276
mock_pygame.K_RIGHT = 275
mock_pygame.K_UP = 273
mock_pygame.K_DOWN = 274

sys.modules['pygame'] = mock_pygame

import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controls import move_player, move_player_with_joystick
from classes.constants import WIDTH, HEIGHT


class MockPlayer:
    """Mock player object for testing controls."""

    def __init__(self, x=100, y=100, width=50, height=50, speed=10):
        self.rect = MagicMock()
        self.rect.x = x
        self.rect.y = y
        self.rect.width = width
        self.rect.height = height
        self.speed = speed
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


def create_keys_dict(**kwargs):
    """Create a mock keys dictionary with specified keys pressed."""
    keys = {
        mock_pygame.K_LEFT: False,
        mock_pygame.K_RIGHT: False,
        mock_pygame.K_UP: False,
        mock_pygame.K_DOWN: False,
    }
    for key, value in kwargs.items():
        if key == 'left':
            keys[mock_pygame.K_LEFT] = value
        elif key == 'right':
            keys[mock_pygame.K_RIGHT] = value
        elif key == 'up':
            keys[mock_pygame.K_UP] = value
        elif key == 'down':
            keys[mock_pygame.K_DOWN] = value
    return keys


class TestMovePlayer(unittest.TestCase):
    """Tests for keyboard-based player movement."""

    def test_move_left(self):
        """Pressing left calls move_left."""
        player = MockPlayer()
        keys = create_keys_dict(left=True)

        move_player(keys, player)

        self.assertTrue(player.move_left_called)
        self.assertFalse(player.move_right_called)
        self.assertFalse(player.stop_called)

    def test_move_right(self):
        """Pressing right calls move_right."""
        player = MockPlayer()
        keys = create_keys_dict(right=True)

        move_player(keys, player)

        self.assertTrue(player.move_right_called)
        self.assertFalse(player.move_left_called)

    def test_move_up(self):
        """Pressing up calls move_up."""
        player = MockPlayer()
        keys = create_keys_dict(up=True)

        move_player(keys, player)

        self.assertTrue(player.move_up_called)
        self.assertFalse(player.move_down_called)

    def test_move_down(self):
        """Pressing down calls move_down."""
        player = MockPlayer()
        keys = create_keys_dict(down=True)

        move_player(keys, player)

        self.assertTrue(player.move_down_called)
        self.assertFalse(player.move_up_called)

    def test_move_up_left(self):
        """Pressing left + up calls move_up_left."""
        player = MockPlayer()
        keys = create_keys_dict(left=True, up=True)

        move_player(keys, player)

        self.assertTrue(player.move_up_left_called)
        self.assertFalse(player.move_left_called)
        self.assertFalse(player.move_up_called)

    def test_move_up_right(self):
        """Pressing right + up calls move_up_right."""
        player = MockPlayer()
        keys = create_keys_dict(right=True, up=True)

        move_player(keys, player)

        self.assertTrue(player.move_up_right_called)
        self.assertFalse(player.move_right_called)
        self.assertFalse(player.move_up_called)

    def test_move_down_left(self):
        """Pressing left + down calls move_down_left."""
        player = MockPlayer()
        keys = create_keys_dict(left=True, down=True)

        move_player(keys, player)

        self.assertTrue(player.move_down_left_called)
        self.assertFalse(player.move_left_called)
        self.assertFalse(player.move_down_called)

    def test_move_down_right(self):
        """Pressing right + down calls move_down_right."""
        player = MockPlayer()
        keys = create_keys_dict(right=True, down=True)

        move_player(keys, player)

        self.assertTrue(player.move_down_right_called)
        self.assertFalse(player.move_right_called)
        self.assertFalse(player.move_down_called)

    def test_no_keys_pressed_stops(self):
        """No keys pressed calls stop."""
        player = MockPlayer()
        keys = create_keys_dict()

        move_player(keys, player)

        self.assertTrue(player.stop_called)
        self.assertFalse(player.move_left_called)
        self.assertFalse(player.move_right_called)
        self.assertFalse(player.move_up_called)
        self.assertFalse(player.move_down_called)

    def test_left_takes_priority_over_right(self):
        """Left key takes priority over right when both pressed."""
        player = MockPlayer()
        keys = create_keys_dict(left=True, right=True)

        move_player(keys, player)

        self.assertTrue(player.move_left_called)
        self.assertFalse(player.move_right_called)


class TestMovePlayerWithJoystick(unittest.TestCase):
    """Tests for joystick-based player movement."""

    def test_joystick_move_right(self):
        """Joystick tilted right moves player right."""
        player = MockPlayer(x=100, y=100)
        joystick = MagicMock()
        joystick.get_axis.side_effect = lambda axis: 0.5 if axis == 0 else 0.0

        move_player_with_joystick(joystick, player)

        expected_x = 100 + 0.5 * player.speed
        self.assertEqual(player.rect.x, expected_x)

    def test_joystick_move_left(self):
        """Joystick tilted left moves player left."""
        player = MockPlayer(x=100, y=100)
        joystick = MagicMock()
        joystick.get_axis.side_effect = lambda axis: -0.5 if axis == 0 else 0.0

        move_player_with_joystick(joystick, player)

        expected_x = 100 + (-0.5) * player.speed
        self.assertEqual(player.rect.x, expected_x)

    def test_joystick_move_down(self):
        """Joystick tilted down moves player down."""
        player = MockPlayer(x=100, y=100)
        joystick = MagicMock()
        joystick.get_axis.side_effect = lambda axis: 0.8 if axis == 1 else 0.0

        move_player_with_joystick(joystick, player)

        expected_y = 100 + 0.8 * player.speed
        self.assertEqual(player.rect.y, expected_y)

    def test_joystick_move_up(self):
        """Joystick tilted up moves player up."""
        player = MockPlayer(x=100, y=100)
        joystick = MagicMock()
        joystick.get_axis.side_effect = lambda axis: -0.8 if axis == 1 else 0.0

        move_player_with_joystick(joystick, player)

        expected_y = 100 + (-0.8) * player.speed
        self.assertEqual(player.rect.y, expected_y)

    def test_joystick_deadzone_x(self):
        """Small joystick X movement is ignored (deadzone)."""
        player = MockPlayer(x=100, y=100)
        joystick = MagicMock()
        joystick.get_axis.side_effect = lambda axis: 0.05 if axis == 0 else 0.0

        move_player_with_joystick(joystick, player)

        self.assertEqual(player.rect.x, 100)

    def test_joystick_deadzone_y(self):
        """Small joystick Y movement is ignored (deadzone)."""
        player = MockPlayer(x=100, y=100)
        joystick = MagicMock()
        joystick.get_axis.side_effect = lambda axis: 0.05 if axis == 1 else 0.0

        move_player_with_joystick(joystick, player)

        self.assertEqual(player.rect.y, 100)

    def test_joystick_clamps_left_boundary(self):
        """Player cannot move past left boundary."""
        player = MockPlayer(x=5, y=100)
        joystick = MagicMock()
        joystick.get_axis.side_effect = lambda axis: -1.0 if axis == 0 else 0.0

        move_player_with_joystick(joystick, player)

        self.assertEqual(player.rect.x, 0)

    def test_joystick_clamps_right_boundary(self):
        """Player cannot move past right boundary."""
        player = MockPlayer(x=WIDTH - 55, y=100, width=50)
        joystick = MagicMock()
        joystick.get_axis.side_effect = lambda axis: 1.0 if axis == 0 else 0.0

        move_player_with_joystick(joystick, player)

        self.assertEqual(player.rect.x, WIDTH - player.rect.width)

    def test_joystick_clamps_top_boundary(self):
        """Player cannot move past top boundary."""
        player = MockPlayer(x=100, y=5)
        joystick = MagicMock()
        joystick.get_axis.side_effect = lambda axis: -1.0 if axis == 1 else 0.0

        move_player_with_joystick(joystick, player)

        self.assertEqual(player.rect.y, 0)

    def test_joystick_clamps_bottom_boundary(self):
        """Player cannot move past bottom boundary."""
        player = MockPlayer(x=100, y=HEIGHT - 55, height=50)
        joystick = MagicMock()
        joystick.get_axis.side_effect = lambda axis: 1.0 if axis == 1 else 0.0

        move_player_with_joystick(joystick, player)

        self.assertEqual(player.rect.y, HEIGHT - player.rect.height)

    def test_joystick_diagonal_movement(self):
        """Joystick tilted diagonally moves in both axes."""
        player = MockPlayer(x=100, y=100)
        joystick = MagicMock()
        joystick.get_axis.side_effect = lambda axis: 0.5 if axis == 0 else 0.5

        move_player_with_joystick(joystick, player)

        expected_x = 100 + 0.5 * player.speed
        expected_y = 100 + 0.5 * player.speed
        self.assertEqual(player.rect.x, expected_x)
        self.assertEqual(player.rect.y, expected_y)


if __name__ == '__main__':
    unittest.main(verbosity=2)
