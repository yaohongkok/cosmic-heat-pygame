"""Unit tests for main.py GameLogic class.

These tests cover the pure business logic extracted from the Game class,
which can be tested without pygame dependencies.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import GameLogic


class TestGameLogicRefills(unittest.TestCase):
    """Tests for refill/pickup mechanics."""

    def test_apply_refill_adds_amount(self):
        """Generic refill adds the specified amount."""
        result = GameLogic.apply_refill(100, 50, 200)
        self.assertEqual(result, 150)

    def test_apply_refill_caps_at_max(self):
        """Generic refill cannot exceed max value."""
        result = GameLogic.apply_refill(180, 50, 200)
        self.assertEqual(result, 200)

    def test_apply_refill_from_zero(self):
        """Generic refill from zero adds the amount."""
        result = GameLogic.apply_refill(0, 50, 200)
        self.assertEqual(result, 50)

    def test_apply_bullet_refill_from_zero(self):
        """Bullet refill from zero adds refill amount."""
        result = GameLogic.apply_bullet_refill(0)
        self.assertEqual(result, GameLogic.REFILL_AMOUNT)

    def test_apply_bullet_refill_partial(self):
        """Bullet refill from partial adds refill amount."""
        result = GameLogic.apply_bullet_refill(100)
        self.assertEqual(result, 100 + GameLogic.REFILL_AMOUNT)

    def test_apply_bullet_refill_caps_at_max(self):
        """Bullet refill cannot exceed max bullets."""
        result = GameLogic.apply_bullet_refill(GameLogic.MAX_BULLETS - 10)
        self.assertEqual(result, GameLogic.MAX_BULLETS)

    def test_apply_bullet_refill_at_max(self):
        """Bullet refill at max stays at max."""
        result = GameLogic.apply_bullet_refill(GameLogic.MAX_BULLETS)
        self.assertEqual(result, GameLogic.MAX_BULLETS)

    def test_apply_health_refill_from_zero(self):
        """Health refill from zero adds refill amount."""
        result = GameLogic.apply_health_refill(0)
        self.assertEqual(result, GameLogic.REFILL_AMOUNT)

    def test_apply_health_refill_partial(self):
        """Health refill from partial adds refill amount."""
        result = GameLogic.apply_health_refill(120)
        self.assertEqual(result, 120 + GameLogic.REFILL_AMOUNT)

    def test_apply_health_refill_caps_at_max(self):
        """Health refill cannot exceed max health."""
        result = GameLogic.apply_health_refill(GameLogic.MAX_HEALTH - 10)
        self.assertEqual(result, GameLogic.MAX_HEALTH)

    def test_apply_health_refill_at_max(self):
        """Health refill at max stays at max."""
        result = GameLogic.apply_health_refill(GameLogic.MAX_HEALTH)
        self.assertEqual(result, GameLogic.MAX_HEALTH)

    def test_apply_double_refill(self):
        """Double refill increases both health and bullets."""
        health, bullets = GameLogic.apply_double_refill(100, 100)
        self.assertEqual(health, 100 + GameLogic.REFILL_AMOUNT)
        self.assertEqual(bullets, 100 + GameLogic.REFILL_AMOUNT)

    def test_apply_double_refill_caps_both(self):
        """Double refill caps both values at max."""
        health, bullets = GameLogic.apply_double_refill(
            GameLogic.MAX_HEALTH - 10, GameLogic.MAX_BULLETS - 5
        )
        self.assertEqual(health, GameLogic.MAX_HEALTH)
        self.assertEqual(bullets, GameLogic.MAX_BULLETS)


class TestGameLogicDamage(unittest.TestCase):
    """Tests for damage calculation mechanics."""

    def test_calculate_damage_normal(self):
        """Damage reduces health normally."""
        result = GameLogic.calculate_damage(200, 50)
        self.assertEqual(result, 150)

    def test_calculate_damage_to_zero(self):
        """Damage can reduce health to zero."""
        result = GameLogic.calculate_damage(50, 50)
        self.assertEqual(result, 0)

    def test_calculate_damage_floors_at_zero(self):
        """Damage cannot reduce health below zero."""
        result = GameLogic.calculate_damage(30, 100)
        self.assertEqual(result, 0)

    def test_is_game_over_when_zero(self):
        """Game over when health is zero."""
        self.assertTrue(GameLogic.is_game_over(0))

    def test_is_game_over_when_negative(self):
        """Game over when health is negative."""
        self.assertTrue(GameLogic.is_game_over(-10))

    def test_not_game_over_when_positive(self):
        """Not game over when health is positive."""
        self.assertFalse(GameLogic.is_game_over(1))
        self.assertFalse(GameLogic.is_game_over(100))


class TestGameLogicScore(unittest.TestCase):
    """Tests for score-related mechanics."""

    def test_update_hi_score_new_high(self):
        """Hi-score updates when current score is higher."""
        result = GameLogic.update_hi_score(1000, 500)
        self.assertEqual(result, 1000)

    def test_update_hi_score_same(self):
        """Hi-score stays same when scores are equal."""
        result = GameLogic.update_hi_score(500, 500)
        self.assertEqual(result, 500)

    def test_update_hi_score_lower(self):
        """Hi-score stays same when current score is lower."""
        result = GameLogic.update_hi_score(300, 500)
        self.assertEqual(result, 500)


class TestGameLogicBackground(unittest.TestCase):
    """Tests for background progression mechanics."""

    def test_background_speed_below_threshold(self):
        """Background speed is base at low scores."""
        result = GameLogic.calculate_background_speed(0)
        self.assertEqual(result, 1)

        result = GameLogic.calculate_background_speed(3000)
        self.assertEqual(result, 1)

    def test_background_speed_above_threshold(self):
        """Background speed increases at high scores."""
        result = GameLogic.calculate_background_speed(3001)
        self.assertEqual(result, 3)

        result = GameLogic.calculate_background_speed(10000)
        self.assertEqual(result, 3)

    def test_background_speed_custom_base(self):
        """Background speed uses custom base shift."""
        result = GameLogic.calculate_background_speed(0, base_shift=2)
        self.assertEqual(result, 2)

        result = GameLogic.calculate_background_speed(5000, base_shift=2)
        self.assertEqual(result, 4)

    def test_get_background_index_initial(self):
        """Initial background for low scores."""
        self.assertEqual(GameLogic.get_background_index(0), 0)
        self.assertEqual(GameLogic.get_background_index(2999), 0)

    def test_get_background_index_second(self):
        """Second background at threshold."""
        self.assertEqual(GameLogic.get_background_index(GameLogic.BACKGROUND_2_THRESHOLD), 1)
        self.assertEqual(GameLogic.get_background_index(9999), 1)

    def test_get_background_index_third(self):
        """Third background at threshold."""
        self.assertEqual(GameLogic.get_background_index(GameLogic.BACKGROUND_3_THRESHOLD), 2)
        self.assertEqual(GameLogic.get_background_index(14999), 2)

    def test_get_background_index_fourth(self):
        """Fourth background at highest threshold."""
        self.assertEqual(GameLogic.get_background_index(GameLogic.BACKGROUND_4_THRESHOLD), 3)
        self.assertEqual(GameLogic.get_background_index(99999), 3)

    def test_wrap_background_shift_normal(self):
        """Background shift returns unchanged when not at boundary."""
        result = GameLogic.wrap_background_shift(-400, 800)
        self.assertEqual(result, -400)

    def test_wrap_background_shift_wraps_at_zero(self):
        """Background shift wraps when reaching zero."""
        result = GameLogic.wrap_background_shift(0, 800)
        self.assertEqual(result, -800)

    def test_wrap_background_shift_wraps_positive(self):
        """Background shift wraps when positive."""
        result = GameLogic.wrap_background_shift(10, 800)
        self.assertEqual(result, -800)


class TestGameLogicBoss(unittest.TestCase):
    """Tests for boss spawning and damage mechanics."""

    def test_should_spawn_boss_below_threshold(self):
        """Boss should not spawn below threshold."""
        self.assertFalse(GameLogic.should_spawn_boss(4999, False, 5000))

    def test_should_spawn_boss_at_threshold(self):
        """Boss should spawn at threshold."""
        self.assertTrue(GameLogic.should_spawn_boss(5000, False, 5000))

    def test_should_spawn_boss_above_threshold(self):
        """Boss should spawn above threshold."""
        self.assertTrue(GameLogic.should_spawn_boss(6000, False, 5000))

    def test_should_spawn_boss_already_spawned(self):
        """Boss should not spawn if already spawned."""
        self.assertFalse(GameLogic.should_spawn_boss(5000, True, 5000))
        self.assertFalse(GameLogic.should_spawn_boss(10000, True, 5000))

    def test_calculate_boss_damage(self):
        """Boss health decreases when hit."""
        result = GameLogic.calculate_boss_damage(150, 5)
        self.assertEqual(result, 145)

    def test_calculate_boss_damage_multiple_hits(self):
        """Boss health decreases correctly over multiple calculations."""
        health = 100
        health = GameLogic.calculate_boss_damage(health, 10)
        self.assertEqual(health, 90)
        health = GameLogic.calculate_boss_damage(health, 10)
        self.assertEqual(health, 80)

    def test_calculate_boss_damage_floors_at_zero(self):
        """Boss health cannot go below zero."""
        result = GameLogic.calculate_boss_damage(3, 10)
        self.assertEqual(result, 0)

    def test_is_boss_defeated_zero(self):
        """Boss is defeated when health is zero."""
        self.assertTrue(GameLogic.is_boss_defeated(0))

    def test_is_boss_defeated_positive(self):
        """Boss is not defeated when health is positive."""
        self.assertFalse(GameLogic.is_boss_defeated(1))
        self.assertFalse(GameLogic.is_boss_defeated(100))


class TestGameLogicSpawning(unittest.TestCase):
    """Tests for spawn logic."""

    def test_should_spawn_enemy2_below_threshold(self):
        """Enemy2 should not spawn below score threshold."""
        self.assertFalse(GameLogic.should_spawn_enemy2(2999, 0))

    def test_should_spawn_enemy2_at_max_count(self):
        """Enemy2 should not spawn when at max count."""
        self.assertFalse(GameLogic.should_spawn_enemy2(5000, 2, max_count=2, chance=0))

    def test_should_spawn_enemy2_conditions_met(self):
        """Enemy2 can spawn when all conditions are met (chance=0 means always)."""
        result = GameLogic.should_spawn_enemy2(5000, 0, max_count=2, chance=0)
        self.assertTrue(result)

    def test_should_spawn_meteor_below_threshold(self):
        """Meteor should not spawn below score threshold."""
        self.assertFalse(GameLogic.should_spawn_meteor(1000, 3000, 0))

    def test_should_spawn_meteor_above_threshold(self):
        """Meteor can spawn above threshold (chance=0 means always)."""
        result = GameLogic.should_spawn_meteor(5000, 3000, 0)
        self.assertTrue(result)


class TestGameLogicThresholds(unittest.TestCase):
    """Tests for threshold ordering and relationships."""

    def test_background_thresholds_are_ordered(self):
        """Background thresholds should be in ascending order."""
        self.assertLess(GameLogic.BACKGROUND_2_THRESHOLD, GameLogic.BACKGROUND_3_THRESHOLD)
        self.assertLess(GameLogic.BACKGROUND_3_THRESHOLD, GameLogic.BACKGROUND_4_THRESHOLD)

    def test_boss_thresholds_are_ordered(self):
        """Boss thresholds should be in ascending order."""
        self.assertLess(GameLogic.BOSS1_THRESHOLD, GameLogic.BOSS2_THRESHOLD)
        self.assertLess(GameLogic.BOSS2_THRESHOLD, GameLogic.BOSS3_THRESHOLD)

    def test_refill_amount_is_positive(self):
        """Refill amount should be positive."""
        self.assertGreater(GameLogic.REFILL_AMOUNT, 0)

    def test_max_values_are_positive(self):
        """Max health and bullets should be positive."""
        self.assertGreater(GameLogic.MAX_HEALTH, 0)
        self.assertGreater(GameLogic.MAX_BULLETS, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)