# Changelog

## Mar 5, 2026

### Refactoring for Testability

#### main.py
- Added `GameLogic` class containing pure business logic that can be unit tested without pygame:
  - `apply_refill()` - generic refill logic with capping
  - `apply_bullet_refill()` / `apply_health_refill()` / `apply_double_refill()` - refill mechanics
  - `calculate_damage()` / `is_game_over()` - damage and game over logic
  - `update_hi_score()` - score tracking
  - `calculate_background_speed()` / `get_background_index()` / `wrap_background_shift()` - background progression
  - `should_spawn_boss()` / `calculate_boss_damage()` / `is_boss_defeated()` - boss mechanics
  - `should_spawn_by_chance()` / `should_spawn_enemy2()` / `should_spawn_meteor()` - spawn logic
- Added `InputHandler` class to handle input event processing:
  - `process_keydown()` / `process_keyup()` - keyboard event handling
  - `process_joystick_button_down()` / `process_joystick_button_up()` - joystick event handling
- Added `CollisionHandler` class with reusable collision detection methods
- Refactored `Game.handle_events()` to use `InputHandler` for cleaner event processing
- Refactored `Game._spawn_enemies()` into smaller focused methods:
  - `_try_spawn_enemy1()`, `_try_spawn_enemy2()`, `_try_spawn_bosses()`
  - `_spawn_boss()`, `_try_spawn_pickups()`, `_try_spawn_hazards()`
- Refactored `Game._update_entities()` into smaller methods:
  - `_update_pickups_and_hazards()`, `_update_enemies()`, `_update_bosses()`
  - `_update_effects()`, `_update_bullets()`
- Refactored `Game._check_collisions()` into smaller methods:
  - `_check_hazard_collisions()`, `_check_pickup_collisions()`, `_check_meteor_collisions()`
  - `_check_enemy_collisions()`, `_check_enemy1_collisions()`, `_check_enemy2_collisions()`
  - `_check_enemy_bullet_collisions()`, `_check_meteor_group_collisions()`
- Refactored `Game._check_boss_collisions()` into reusable method:
  - `_check_single_boss_collisions()` - handles all boss types with parameters
  - `_check_boss_bullets_hit_player()` - boss bullet collision detection
- Added helper methods for common operations:
  - `_create_explosion()`, `_create_explosion2()` - explosion creation
  - `_try_drop_double_refill()`, `_try_drop_bullet_refill()`, `_try_drop_health_refill()` - drop handling

#### functions.py
- Removed module-level pygame initialization that made testing difficult
- Split `show_game_over()` into testable components:
  - `render_game_over_screen()` - rendering logic
  - `play_game_over_sound()` - sound playback
- Split `show_game_win()` into testable components:
  - `render_game_win_screen()` - rendering logic
  - `play_game_win_sound()` - sound playback
- Added optional `screen` parameter for dependency injection in tests

### New Unit Tests

#### tests/test_unit_main.py (50 tests)
- Tests for generic refill mechanics
- Tests for bullet and health refill mechanics
- Tests for damage calculation and game over detection
- Tests for hi-score tracking
- Tests for background progression (speed, index, wrapping)
- Tests for boss spawning and defeat logic
- Tests for enemy and meteor spawn conditions
- Tests for threshold ordering and value relationships

#### tests/test_unit_controls.py (21 tests)
- Tests for keyboard movement (8 directions + stop)
- Tests for keyboard priority (left vs right)
- Tests for joystick movement (all directions)
- Tests for joystick deadzone
- Tests for joystick boundary clamping

#### tests/test_unit_functions.py (23 tests)
- Tests for background music initialization
- Tests for game over screen rendering
- Tests for game over sound playback
- Tests for win screen rendering
- Tests for win sound playback
- Tests for composite functions (show_game_over, show_game_win)

#### tests/test_unit_menu.py (9 tests)
- Refactored to use proper `@patch` decorators for better test isolation

## Mar 4, 2026
- Refactored main.py into classes
- Moved tests into the 'tests' folder
- Added integration test for main.py
- Improve robustness of source code to make tests less prone to failure

## Mar 2 - Mar 3, 2026
- Refactored menu.py to be a strict class
- Refactored main.py to accommodate for menu.py changes
- Introduced test for menu.py