"""Contagem e integração dos alertas de áudio."""

import os
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402
from PySide6.QtGui import QKeySequence  # noqa: E402

from tibiaenhanced.services.audio_timer import AudioTimer  # noqa: E402
from tibiaenhanced.ui.audio_panel import AudioPanel, DEFAULT_TIMERS  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
