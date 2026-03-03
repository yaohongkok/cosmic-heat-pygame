"""Unit tests for the MainMenu class.

These tests mock pygame to avoid requiring a display.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch


# Create comprehensive pygame mock before any imports
mock_pygame = MagicMock()
mock_pygame.QUIT = 256
mock_pygame.MOUSEBUTTONDOWN = 1025
mock_pygame.KEYDOWN = 768
mock_pygame.JOYBUTTONDOWN = 1539
mock_pygame.JOYHATMOTION = 1538
mock_pygame.K_UP = 273
mock_pygame.K_DOWN = 274
mock_pygame.K_RETURN = 13
mock_pygame.SRCALPHA = 65536

# Mock Rect class
class MockRect:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.width, self.height = x, y, w, h
        self.center = (x + w // 2, y + h // 2)
    
    def collidepoint(self, pos):
        x, y = pos
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)

mock_pygame.Rect = MockRect

# Mock Surface
class MockSurface:
    def __init__(self, *args, **kwargs):
        pass
    def get_width(self):
        return 100
    def get_height(self):
        return 100
    def get_rect(self, **kwargs):
        return MockRect(0, 0, 100, 100)
    def convert(self):
        return self
    def convert_alpha(self):
        return self
    def blit(self, *args):
        pass
    def fill(self, *args):
        pass

mock_pygame.Surface = MockSurface

# Install mocks
sys.modules['pygame'] = mock_pygame
sys.modules['pygame.mixer'] = MagicMock()
sys.modules['pygame.joystick'] = MagicMock()
sys.modules['pygame.display'] = MagicMock()
sys.modules['pygame.font'] = MagicMock()
sys.modules['pygame.image'] = MagicMock()
sys.modules['pygame.draw'] = MagicMock()
sys.modules['pygame.time'] = MagicMock()
sys.modules['pygame.event'] = MagicMock()

# Mock the image loading
mock_pygame.image.load.return_value = MockSurface()
mock_pygame.transform.scale.return_value = MockSurface()
mock_pygame.display.set_mode.return_value = MockSurface()
mock_pygame.font.SysFont.return_value = MagicMock()
mock_pygame.joystick.get_count.return_value = 0

# Set up path for imports
sys.path.insert(0, '/tmp/inputs/cosmic-heat-pygame')

# Import menu module (safe now since no module-level execution)
from menu import MenuButton, MainMenu


class TestMenuButton(unittest.TestCase):
    """Test the MenuButton enum."""
    
    def test_enum_values(self):
        """Test that MenuButton has correct values."""
        self.assertEqual(MenuButton.PLAY, 0)
        self.assertEqual(MenuButton.QUIT, 1)


class TestMainMenuClass(unittest.TestCase):
    """Test the MainMenu class methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        mock_pygame.event.get.return_value = []

    def test_menu_initialization(self):
        """Test MainMenu initializes with correct state."""
        menu = MainMenu()
        
        self.assertEqual(menu.selected_button, MenuButton.PLAY)
        self.assertTrue(menu.running)

    def test_start_game_sets_running_false(self):
        """Test _start_game() sets running to False."""
        menu = MainMenu()
        menu.explosion_sound = MagicMock()
        menu.background = MockSurface()
        
        menu._start_game()
        
        self.assertFalse(menu.running)
        menu.explosion_sound.play.assert_called_once()

    def test_execute_play_action(self):
        """Test _execute_selected_action() with PLAY selected."""
        menu = MainMenu()
        menu.selected_button = MenuButton.PLAY
        menu.explosion_sound = MagicMock()
        menu.background = MockSurface()
        
        menu._execute_selected_action()
        
        self.assertFalse(menu.running)

    @patch('menu.pygame.quit')
    @patch('menu.sys.exit')
    def test_execute_quit_action(self, mock_exit, mock_quit):
        """Test _execute_selected_action() with QUIT selected."""
        menu = MainMenu()
        menu.selected_button = MenuButton.QUIT
        
        menu._execute_selected_action()
        
        mock_quit.assert_called_once()
        mock_exit.assert_called_once()

    def test_keyboard_navigation_up(self):
        """Test keyboard UP selects PLAY button."""
        menu = MainMenu()
        menu.selected_button = MenuButton.QUIT
        
        event = MagicMock()
        event.key = mock_pygame.K_UP
        
        menu._handle_keyboard(event)
        
        self.assertEqual(menu.selected_button, MenuButton.PLAY)

    def test_keyboard_navigation_down(self):
        """Test keyboard DOWN selects QUIT button."""
        menu = MainMenu()
        menu.selected_button = MenuButton.PLAY
        
        event = MagicMock()
        event.key = mock_pygame.K_DOWN
        
        menu._handle_keyboard(event)
        
        self.assertEqual(menu.selected_button, MenuButton.QUIT)

    def test_mouse_click_play_button(self):
        """Test mouse click on Play button starts game."""
        menu = MainMenu()
        menu.explosion_sound = MagicMock()
        menu.background = MockSurface()
        
        # Click position within play button
        menu.play_button = MockRect(500, 375, 205, 50)
        
        menu._handle_mouse_click((550, 400))
        
        self.assertFalse(menu.running)

    def test_joystick_hat_navigation(self):
        """Test joystick hat motion changes selection."""
        menu = MainMenu()
        
        # Hat up
        event = MagicMock()
        event.value = (0, 1)
        menu._handle_joystick_hat(event)
        self.assertEqual(menu.selected_button, MenuButton.PLAY)
        
        # Hat down
        event.value = (0, -1)
        menu._handle_joystick_hat(event)
        self.assertEqual(menu.selected_button, MenuButton.QUIT)


if __name__ == '__main__':
    unittest.main(verbosity=2)
