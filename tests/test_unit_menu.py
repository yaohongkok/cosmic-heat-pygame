"""Unit tests for the MainMenu class.

These tests verify menu initialization, navigation, and action handling.

Forked Test Compatibility:
    Previous implementation used module-level sys.modules manipulation to mock
    pygame, which failed with `pytest --forked` because the forked process
    inherited the parent's module cache with the real pygame already loaded.
    
    The fix uses @patch.dict('sys.modules', ...) within each test method,
    combined with clearing the 'menu' module from sys.modules before import.
    This ensures each test gets a fresh menu module with the mocked pygame.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class MockRect:
    """Mock pygame.Rect for testing menu button collision detection."""
    
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center = (x + width // 2, y + height // 2)
    
    def collidepoint(self, pos):
        """Check if a point is within this rectangle."""
        point_x, point_y = pos
        return (self.x <= point_x <= self.x + self.width and 
                self.y <= point_y <= self.y + self.height)


class MockSurface:
    """Mock pygame.Surface for testing menu rendering."""
    
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


def create_pygame_mock():
    """Create a comprehensive pygame mock with all required constants and methods.
    
    Returns:
        MagicMock: A configured pygame mock object
    """
    mock_pygame = MagicMock()
    
    # Event type constants
    mock_pygame.QUIT = 256
    mock_pygame.MOUSEBUTTONDOWN = 1025
    mock_pygame.KEYDOWN = 768
    mock_pygame.JOYBUTTONDOWN = 1539
    mock_pygame.JOYHATMOTION = 1538
    
    # Key constants
    mock_pygame.K_UP = 273
    mock_pygame.K_DOWN = 274
    mock_pygame.K_RETURN = 13
    
    # Surface flags
    mock_pygame.SRCALPHA = 65536
    
    # Classes
    mock_pygame.Rect = MockRect
    mock_pygame.Surface = MockSurface
    
    # Method return values
    mock_pygame.image.load.return_value = MockSurface()
    mock_pygame.transform.scale.return_value = MockSurface()
    mock_pygame.display.set_mode.return_value = MockSurface()
    mock_pygame.font.SysFont.return_value = MagicMock()
    mock_pygame.joystick.get_count.return_value = 0
    mock_pygame.event.get.return_value = []
    
    return mock_pygame


def clear_menu_module():
    """Remove menu module from cache to ensure fresh import with mocked pygame."""
    if 'menu' in sys.modules:
        del sys.modules['menu']


class TestMenuButton(unittest.TestCase):
    """Tests for the MenuButton enum values."""
    
    @patch.dict('sys.modules', {'pygame': create_pygame_mock()})
    def test_play_button_has_value_zero(self):
        """PLAY button enum value is 0."""
        clear_menu_module()
        from menu import MenuButton
        
        self.assertEqual(MenuButton.PLAY, 0)

    @patch.dict('sys.modules', {'pygame': create_pygame_mock()})
    def test_quit_button_has_value_one(self):
        """QUIT button enum value is 1."""
        clear_menu_module()
        from menu import MenuButton
        
        self.assertEqual(MenuButton.QUIT, 1)


class TestMainMenuInitialization(unittest.TestCase):
    """Tests for MainMenu class initialization."""
    
    @patch.dict('sys.modules', {'pygame': create_pygame_mock()})
    def test_starts_with_play_button_selected(self):
        """Menu initializes with PLAY button selected."""
        clear_menu_module()
        from menu import MainMenu, MenuButton
        
        menu = MainMenu()
        
        self.assertEqual(menu.selected_button, MenuButton.PLAY)

    @patch.dict('sys.modules', {'pygame': create_pygame_mock()})
    def test_starts_in_running_state(self):
        """Menu initializes in running state."""
        clear_menu_module()
        from menu import MainMenu
        
        menu = MainMenu()
        
        self.assertTrue(menu.running)


class TestMainMenuActions(unittest.TestCase):
    """Tests for MainMenu action methods."""
    
    @patch.dict('sys.modules', {'pygame': create_pygame_mock()})
    def test_start_game_sets_running_to_false(self):
        """_start_game() stops the menu loop."""
        clear_menu_module()
        from menu import MainMenu
        
        menu = MainMenu()
        menu.explosion_sound = MagicMock()
        menu.background = MockSurface()
        
        menu._start_game()
        
        self.assertFalse(menu.running)

    @patch.dict('sys.modules', {'pygame': create_pygame_mock()})
    def test_start_game_plays_explosion_sound(self):
        """_start_game() plays the explosion sound effect."""
        clear_menu_module()
        from menu import MainMenu
        
        menu = MainMenu()
        menu.explosion_sound = MagicMock()
        menu.background = MockSurface()
        
        menu._start_game()
        
        menu.explosion_sound.play.assert_called_once()

    @patch.dict('sys.modules', {'pygame': create_pygame_mock()})
    def test_execute_action_with_play_selected_starts_game(self):
        """_execute_selected_action() starts game when PLAY is selected."""
        clear_menu_module()
        from menu import MainMenu, MenuButton
        
        menu = MainMenu()
        menu.selected_button = MenuButton.PLAY
        menu.explosion_sound = MagicMock()
        menu.background = MockSurface()
        
        menu._execute_selected_action()
        
        self.assertFalse(menu.running)

    @patch.dict('sys.modules', {'pygame': create_pygame_mock()})
    def test_execute_action_with_quit_selected_exits(self):
        """_execute_selected_action() quits pygame and exits when QUIT is selected."""
        clear_menu_module()
        from menu import MainMenu, MenuButton
        
        menu = MainMenu()
        menu.selected_button = MenuButton.QUIT
        
        with patch('menu.pygame.quit') as mock_quit:
            with patch('menu.sys.exit') as mock_exit:
                menu._execute_selected_action()
                
                mock_quit.assert_called_once()
                mock_exit.assert_called_once()


class TestMainMenuKeyboardNavigation(unittest.TestCase):
    """Tests for keyboard navigation in MainMenu."""
    
    @patch.dict('sys.modules', {'pygame': create_pygame_mock()})
    def test_up_key_selects_play_button(self):
        """Pressing UP key selects PLAY button."""
        clear_menu_module()
        pygame_mock = create_pygame_mock()
        
        with patch.dict('sys.modules', {'pygame': pygame_mock}):
            from menu import MainMenu, MenuButton
            
            menu = MainMenu()
            menu.selected_button = MenuButton.QUIT
            
            keyboard_event = MagicMock()
            keyboard_event.key = pygame_mock.K_UP
            
            menu._handle_keyboard(keyboard_event)
            
            self.assertEqual(menu.selected_button, MenuButton.PLAY)

    @patch.dict('sys.modules', {'pygame': create_pygame_mock()})
    def test_down_key_selects_quit_button(self):
        """Pressing DOWN key selects QUIT button."""
        clear_menu_module()
        pygame_mock = create_pygame_mock()
        
        with patch.dict('sys.modules', {'pygame': pygame_mock}):
            from menu import MainMenu, MenuButton
            
            menu = MainMenu()
            menu.selected_button = MenuButton.PLAY
            
            keyboard_event = MagicMock()
            keyboard_event.key = pygame_mock.K_DOWN
            
            menu._handle_keyboard(keyboard_event)
            
            self.assertEqual(menu.selected_button, MenuButton.QUIT)


class TestMainMenuMouseInput(unittest.TestCase):
    """Tests for mouse input handling in MainMenu."""
    
    @patch.dict('sys.modules', {'pygame': create_pygame_mock()})
    def test_click_on_play_button_starts_game(self):
        """Clicking on Play button starts the game."""
        clear_menu_module()
        from menu import MainMenu
        
        menu = MainMenu()
        menu.explosion_sound = MagicMock()
        menu.background = MockSurface()
        menu.play_button = MockRect(500, 375, 205, 50)
        
        click_position = (550, 400)  # Within play button bounds
        menu._handle_mouse_click(click_position)
        
        self.assertFalse(menu.running)


class TestMainMenuJoystickInput(unittest.TestCase):
    """Tests for joystick input handling in MainMenu."""
    
    @patch.dict('sys.modules', {'pygame': create_pygame_mock()})
    def test_hat_up_selects_play_button(self):
        """Joystick hat pushed up selects PLAY button."""
        clear_menu_module()
        from menu import MainMenu, MenuButton
        
        menu = MainMenu()
        
        hat_event = MagicMock()
        hat_event.value = (0, 1)  # Up direction
        
        menu._handle_joystick_hat(hat_event)
        
        self.assertEqual(menu.selected_button, MenuButton.PLAY)

    @patch.dict('sys.modules', {'pygame': create_pygame_mock()})
    def test_hat_down_selects_quit_button(self):
        """Joystick hat pushed down selects QUIT button."""
        clear_menu_module()
        from menu import MainMenu, MenuButton
        
        menu = MainMenu()
        
        hat_event = MagicMock()
        hat_event.value = (0, -1)  # Down direction
        
        menu._handle_joystick_hat(hat_event)
        
        self.assertEqual(menu.selected_button, MenuButton.QUIT)


if __name__ == '__main__':
    unittest.main(verbosity=2)