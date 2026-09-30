"""Contagem e integração dos alertas de áudio."""

import os
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton  # noqa: E402
from PySide6.QtGui import QKeySequence  # noqa: E402
from PySide6.QtCore import QAbstractAnimation  # noqa: E402

from tibiaenhanced.services.audio_timer import AudioTimer  # noqa: E402
from tibiaenhanced.ui.audio_panel import AudioPanel, DEFAULT_TIMERS, TimerDialog  # noqa: E402
from tibiaenhanced.ui.design import ToggleCheckBox  # noqa: E402


class AudioTimerTests(unittest.TestCase):
    def test_pause_resume_and_single_completion(self) -> None:
        now = [100.0]
        timer = AudioTimer("Teste", 10, Path("test.mp3"), clock=lambda: now[0])
        timer.start()
        now[0] = 104.2
        timer.pause()
        self.assertEqual(timer.remaining(), 6)
        now[0] = 200.0
        self.assertEqual(timer.remaining(), 6)
        timer.start()
        now[0] = 205.8
        self.assertTrue(timer.tick())
        self.assertFalse(timer.tick())
        self.assertEqual(timer.remaining(), 0)
        timer.reset()
        self.assertEqual(timer.remaining(), 10)

    def test_independent_timers_and_resume_after_suspend(self) -> None:
        now = [0.0]
        food = AudioTimer("Food", 3600, Path("food.mp3"), clock=lambda: now[0])
        potion = AudioTimer("Potion", 600, Path("potion.mp3"), clock=lambda: now[0])
        food.start()
        potion.start()
        now[0] = 601.0
        self.assertTrue(potion.tick())
        self.assertFalse(food.tick())
        self.assertEqual(food.remaining(), 2999)

    def test_loop_alerts_once_then_starts_new_cycle(self) -> None:
        now = [0.0]
        timer = AudioTimer("Loop", 10, Path("test.mp3"), loop=True, clock=lambda: now[0])
        timer.start()
        now[0] = 35.0  # simula suspensão por mais de um ciclo
        self.assertTrue(timer.tick())
        self.assertTrue(timer.running)
        self.assertEqual(timer.remaining(), 10)
        self.assertFalse(timer.tick())
        now[0] = 45.0
        self.assertTrue(timer.tick())
        timer.pause()
        self.assertFalse(timer.tick())


class AudioPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_defaults_have_expected_media_and_duration(self) -> None:
        panel = AudioPanel()
        self.assertEqual([card.timer.duration_seconds for card in panel.cards], [3600, 600])
        for _, _, sound, images in DEFAULT_TIMERS:
            self.assertTrue(sound.is_file())
            self.assertTrue(images)
            self.assertTrue(all(image.is_file() for image in images))
        self.assertTrue(all(not card.art.pixmap().isNull() for card in panel.cards))
        self.assertTrue(all(not card.shortcut_binding.isEnabled() for card in panel.cards))
        self.assertTrue(all(not card.removable for card in panel.cards))
        self.assertTrue(all(isinstance(card.loop_check, ToggleCheckBox) for card in panel.cards))
        self.assertTrue(all(not any(button.toolTip() == "Excluir temporizador"
                                    for button in card.findChildren(QPushButton))
                            for card in panel.cards))
        panel.close()

    def test_default_timers_cannot_be_deleted_but_custom_timer_can(self) -> None:
        panel = AudioPanel()
        defaults = tuple(panel.cards)
        for card in defaults:
            panel.remove_card(card)
        self.assertEqual(tuple(panel.cards), defaults)
        custom = panel.add_timer(AudioTimer("Personalizado", 120, DEFAULT_TIMERS[0][2]))
        self.assertTrue(custom.removable)
        self.assertTrue(any(button.toolTip() == "Excluir temporizador"
                            for button in custom.findChildren(QPushButton)))
        custom.loop_check.click()
        self.assertTrue(custom.timer.loop)
        panel.remove_card(custom)
        self.assertEqual(tuple(panel.cards), defaults)
        dialog = TimerDialog(panel, defaults[0].timer)
        self.assertIsInstance(dialog.loop_input, ToggleCheckBox)
        panel.close()

    def test_shortcut_restarts_timer_and_detects_conflict(self) -> None:
        panel = AudioPanel()
        card = panel.cards[0]
        card.timer.shortcut = "F6"
        card._update_shortcut()
        self.assertTrue(panel.shortcut_conflict(QKeySequence("F6")))
        self.assertFalse(panel.shortcut_conflict(QKeySequence("F6"), card.timer))
        card.timer.start()
        card.shortcut_binding.activated.emit()
        self.assertTrue(card.timer.running)
        self.assertGreater(card.timer.remaining(), 0)
        panel.close()

    def test_small_window_scrolls_cards_without_overlap(self) -> None:
        panel = AudioPanel()
        panel.resize(540, 260)
        panel.show()
        self.app.processEvents()
        first, second = panel.cards
        self.assertGreater(second.y(), first.y() + first.height())
        self.assertGreaterEqual(panel.card_layout.parentWidget().minimumHeight(),
                                second.y() + second.height())
        first.start_button.click()
        self.assertTrue(first.timer.running)
        self.assertFalse(second.timer.running)
        first.loop_check.click()
        self.assertTrue(first.timer.loop)
        panel.close()

    def test_loop_switch_animates_when_visible(self) -> None:
        panel = AudioPanel()
        panel.show()
        self.app.processEvents()
        switch = panel.cards[0].loop_check
        switch.click()
        self.assertTrue(switch.isChecked())
        self.assertEqual(switch._animation.state(), QAbstractAnimation.State.Running)
        switch._animation.setCurrentTime(85)
        self.assertGreater(switch._position, 0.0)
        self.assertLess(switch._position, 1.0)
        switch._animation.setCurrentTime(170)
        self.assertAlmostEqual(switch._position, 1.0)
        panel.close()

    def test_volume_tracks_keep_their_width_as_percentages_change(self) -> None:
        panel = AudioPanel()
        panel.show()
        self.app.processEvents()
        card = panel.cards[0]
        master_width = panel.master_volume.width()
        card_width = card.volume.width()
        for percent in (0, 9, 50, 100):
            panel.master_volume.setValue(percent)
            card.volume.setValue(percent)
            self.app.processEvents()
            self.assertEqual(panel.master_volume.width(), master_width)
            self.assertEqual(card.volume.width(), card_width)
        panel.close()


if __name__ == "__main__":
    unittest.main()
