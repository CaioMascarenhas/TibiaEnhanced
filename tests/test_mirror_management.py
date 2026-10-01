"""Ciclo de vida de vários espelhos no painel, sem abrir o cliente do jogo."""

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, Signal  # noqa: E402
from PySide6.QtWidgets import QApplication, QPushButton, QSlider  # noqa: E402

from tibiaenhanced.models import Region  # noqa: E402
from tibiaenhanced.ui.capture_panel import CapturePanel, MirrorEntry  # noqa: E402


class _FakeWindow(QObject):
    stopped = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.active = False
        self.locked = False
        self.fit_mode = "contain"
        self.opacity_percent = 100

    def show(self) -> None:
        self.active = True

    def close(self) -> None:
        self.active = False
        self.stopped.emit("Espelho fechado")

    def set_locked(self, value: bool) -> None:
        self.locked = value

    def set_fit_mode(self, mode: str) -> None:
        self.fit_mode = mode

    def set_opacity_percent(self, percent: int) -> None:
        self.opacity_percent = percent

    def rename(self, _name: str) -> None:
        pass


class MirrorManagementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_two_regions_from_same_source_are_independent(self) -> None:
        with patch("tibiaenhanced.ui.capture_panel.list_windows", return_value=[]):
            panel = CapturePanel()
        first_window = _FakeWindow()
        second_window = _FakeWindow()
        first_window.stopped.connect(lambda message: panel._on_mirror_stopped(1, message))
        second_window.stopped.connect(lambda message: panel._on_mirror_stopped(2, message))
        panel._entries = {
            1: MirrorEntry(1, 42, "Tibia", Region("HP", 0, 0, 100, 40), first_window),
            2: MirrorEntry(2, 42, "Tibia", Region("Mana", 120, 0, 100, 40), second_window),
        }
        panel._refresh_cards(1)
        panel._show_entry(panel._entries[1])
        panel._show_entry(panel._entries[2])
        self.assertTrue(first_window.active)
        self.assertTrue(second_window.active)

        self.assertEqual(set(panel._cards), {1, 2})
        panel._cards[1].findChildren(QPushButton)[2].click()
        self.assertTrue(first_window.locked)
        self.assertFalse(second_window.locked)
        panel._cards[1].findChild(QSlider).setValue(55)
        self.assertEqual(first_window.opacity_percent, 55)
        self.assertEqual(second_window.opacity_percent, 100)
        panel._cards[1].findChildren(QPushButton)[1].click()
        self.assertFalse(first_window.active)
        self.assertTrue(second_window.active)

        panel._cards[2].findChildren(QPushButton)[3].click()
        self.assertFalse(second_window.active)
        self.assertEqual([entry.region.name for entry in panel.entries], ["HP"])
        panel.shutdown()

    def test_mirror_menu_actions_update_panel_entry(self) -> None:
        with patch("tibiaenhanced.ui.capture_panel.list_windows", return_value=[]):
            panel = CapturePanel()
        window = _FakeWindow()
        window.stopped.connect(lambda message: panel._on_mirror_stopped(1, message))
        panel._entries[1] = MirrorEntry(1, 42, "Tibia", Region("HP", 0, 0, 100, 40), window)
        panel._show_entry(panel._entries[1])
        panel._mirror_action(1, "lock")
        self.assertTrue(panel._entries[1].locked)
        panel._mirror_action(1, "hide")
        self.assertFalse(panel._entries[1].visible)
        panel._mirror_action(1, "delete")
        self.assertFalse(panel._entries)
        panel.shutdown()


if __name__ == "__main__":
    unittest.main()
