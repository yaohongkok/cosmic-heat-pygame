"""Pytest configuration for pygame test isolation.

Problem:
    When running tests with `pytest --forked`, each test runs in a separate
    forked process. Tests that mock pygame at the module level can interfere
    with tests that need the real pygame module because:
    
    1. The parent process may have already imported pygame before forking
    2. Module-level sys.modules manipulation doesn't work reliably across
       process boundaries
    3. SDL2 pygame uses different key constants (e.g., K_LEFT = 1073741904)
       than the mocked values tests were using (e.g., K_LEFT = 276)

Solution:
    This conftest reorders test execution to minimize interference:
    1. Pure logic tests (no pygame dependency) run first
    2. Tests using mocked pygame run second  
    3. Integration tests using real pygame run last
    
    Additionally, the test files were refactored to:
    - Use @patch decorators instead of module-level sys.modules manipulation
    - Initialize pygame in setUp() rather than setUpClass() for forked tests
    - Use real pygame key constants when creating test key dictionaries
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def pytest_configure(config):
    """Register custom markers for test categorization."""
    config.addinivalue_line(
        "markers", "mock_pygame: mark test as requiring mocked pygame"
    )
    config.addinivalue_line(
        "markers", "real_pygame: mark test as requiring real pygame"
    )


def pytest_collection_modifyitems(config, items):
    """Reorder tests to ensure proper isolation between mocked and real pygame.
    
    Test execution order:
    1. Pure logic tests (test_unit_main) - no pygame dependency
    2. Mocked pygame tests (test_unit_controls, test_unit_functions, test_unit_menu)
    3. Real pygame tests (test_int_main) - require initialized pygame
    
    This ordering prevents the real pygame module from polluting the module
    cache before mocked tests run, and ensures real pygame tests have a
    clean environment.
    """
    pure_logic_tests = []
    mocked_pygame_tests = []
    real_pygame_tests = []
    
    for item in items:
        module_name = item.module.__name__
        
        if 'test_unit_main' in module_name:
            pure_logic_tests.append(item)
        elif any(name in module_name for name in [
            'test_unit_controls',
            'test_unit_functions',
            'test_unit_menu'
        ]):
            mocked_pygame_tests.append(item)
        elif 'test_int_main' in module_name:
            real_pygame_tests.append(item)
        else:
            pure_logic_tests.append(item)
    
    items[:] = pure_logic_tests + mocked_pygame_tests + real_pygame_tests