"""Alternância de tema sem perder estado e preferência local compatível com perfis antigos."""

import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QPushButton
from tibiaenhanced.services.profiles import ProfileStore
from tibiaenhanced.ui.audio_panel import TimerDialog
from tibiaenhanced.ui.design import load_fonts
from tibiaenhanced.ui.dwm_windows import DwmRegionDialog
from tibiaenhanced.ui.main_window import MainWindow
from tibiaenhanced.ui.palette import DARK, LIGHT, current_palette
from tibiaenhanced.ui.theme_manager import theme_manager
from test_readable_design import contrast


class ColorThemeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        load_fonts()

    def test_both_palettes_have_readable_text_and_primary_actions(self):
        self.assertEqual(DARK.keys(), LIGHT.keys())
        for colors in (DARK, LIGHT):
            for surface in ("BACKGROUND", "SURFACE", "INPUT", "SIDEBAR"):
                self.assertGreaterEqual(contrast(colors["TEXT"], colors[surface]), 7)
                self.assertGreaterEqual(contrast(colors["MUTED"], colors[surface]), 4.5)
            self.assertGreaterEqual(contrast(colors["PRIMARY_TEXT"], colors["PRIMARY"]), 4.5)
            self.assertGreaterEqual(contrast(colors["DANGER_TEXT"], colors["DANGER_BACKGROUND"]), 4.5)

    def test_toggle_preserves_live_state_updates_existing_dialogs_and_restores_preference(self):
        manager = theme_manager()
        manager.apply("dark")
        self.addCleanup(manager.apply, "dark")
        with tempfile.TemporaryDirectory() as folder, patch(
                "tibiaenhanced.ui.capture_panel.list_windows", return_value=[
                    SimpleNamespace(hwnd=42, title="Tibia - Teste", executable="client.exe", class_name="TibiaClient")]):
            store = ProfileStore(Path(folder) / "profiles.json")
            window = MainWindow(store)
            try:
                window.show()
                window.navigation_buttons[1].click()
                card = window.audio_panel.cards[0]
                card.volume.setValue(33)
                card.loop_check.setChecked(True)
                card.timer.start()
                self.app.processEvents()
                timer_dialog = TimerDialog(window.audio_panel, card.timer)
                self.addCleanup(timer_dialog.close)
                with patch("tibiaenhanced.ui.dwm_windows.get_client_area",
                           return_value=SimpleNamespace(width=800, height=600)):
                    selection_dialog = DwmRegionDialog(42)
                self.addCleanup(selection_dialog.close)
                close_button = timer_dialog.findChildren(QPushButton)[0]
                old_icon = close_button.icon().pixmap(16, 16).toImage()
                arrow = window.capture_panel.window_combo._arrow
                old_arrow = arrow.pixmap().toImage()
                card_identity, volume_width, geometry = id(card), card.volume.width(), window.size()
                self.assertTrue(window.theme_switch.isChecked())
                window.theme_switch.click()
                self.app.processEvents()
                self.assertEqual(manager.mode, "light")
                self.assertEqual(current_palette(), LIGHT)
                self.assertFalse(window.theme_switch.isChecked())
                self.assertEqual(window.pages.currentIndex(), 1)
                self.assertEqual(window.size(), geometry)
                self.assertEqual(id(window.audio_panel.cards[0]), card_identity)
                self.assertTrue(card.timer.running)
                self.assertTrue(card.timer.loop)
                self.assertEqual(card.volume.value(), 33)
                self.assertEqual(card.volume.width(), volume_width)
                self.assertEqual(card.volume.accent, LIGHT["ACCENT"])
                self.assertEqual(timer_dialog.volume_input.accent, LIGHT["ACCENT"])
                self.assertNotEqual(arrow.pixmap().toImage(), old_arrow)
                self.assertNotEqual(close_button.icon().pixmap(16, 16).toImage(), old_icon)
                self.assertIn(LIGHT["SURFACE"], selection_dialog.styleSheet())
                self.assertIn(LIGHT["TEXT"], selection_dialog.styleSheet())
                self.assertEqual(self.app.palette().color(QPalette.ColorRole.Text).name(), LIGHT["TEXT"])
                self.assertTrue(window._save_profile())
                saved = json.loads(store.path.read_text(encoding="utf-8"))
                self.assertEqual(saved["theme"], "light")
                window.theme_switch.click()
                self.app.processEvents()
                self.assertEqual(manager.mode, "dark")
                self.assertEqual(card.volume.accent, DARK["ACCENT"])
                self.assertTrue(card.timer.running)
                self.assertTrue(window.theme_switch.isChecked())
                window._save_timer.stop()
                restored = ProfileStore(store.path)
                self.assertEqual(restored.load(), [])
                restored_window = MainWindow(restored)
                try:
                    self.assertEqual(manager.mode, "light")
                    self.assertFalse(restored_window.theme_switch.isChecked())
                finally:
                    restored_window._exiting = True
                    restored_window.capture_panel.shutdown()
                    restored_window.close()
            finally:
                window._exiting = True
                window.capture_panel.shutdown()
                window.audio_panel.ticker.stop()
                window.close()

    def test_legacy_and_invalid_theme_settings_fall_back_to_dark(self):
        with tempfile.TemporaryDirectory() as folder:
            store = ProfileStore(Path(folder) / "profiles.json")
            payload = dict(store.data)
            payload.pop("theme")
            for mode in (None, "unknown", "light", "dark"):
                data = {**payload, **({"theme": mode} if mode is not None else {})}
                store.path.write_text(json.dumps(data), encoding="utf-8")
                self.assertEqual(store.load(), [])
                self.assertEqual(store.data["theme"], mode if mode in ("light", "dark") else "dark")


if __name__ == "__main__":
    unittest.main()
