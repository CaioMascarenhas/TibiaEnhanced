"""Legibilidade e geometria com o tema real, incluindo nomes longos."""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QFont
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit

from tibiaenhanced.ui.design import load_fonts, ui_font
from tibiaenhanced.ui.main_window import MainWindow
from tibiaenhanced.ui.palette import BACKGROUND, SURFACE, TEXT, MUTED, PRIMARY
from tibiaenhanced.ui.theme import app_stylesheet
from tibiaenhanced.ui.elided_label import ElidedLabel
from tibiaenhanced.ui.audio_panel import TimerDialog


def contrast(first, second):
    def luminance(color):
        channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
                  for value in channels]
        return sum(weight * value for weight, value in zip((0.2126, 0.7152, 0.0722), linear))
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


class ReadableDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        previous_theme, previous_font = self.app.styleSheet(), self.app.font()
        load_fonts()
        self.app.setFont(ui_font())
        self.app.setStyleSheet(app_stylesheet())
        self.addCleanup(self.app.setFont, previous_font)
        self.addCleanup(self.app.setStyleSheet, previous_theme)
        source = SimpleNamespace(hwnd=42, title="Tibia - " + "W" * 150,
                                 executable="client.exe", class_name="TibiaClient")
        mock_windows = patch("tibiaenhanced.ui.capture_panel.list_windows", return_value=[source])
        mock_windows.start()
        self.addCleanup(mock_windows.stop)
        self.window = MainWindow()
        self.addCleanup(self.close_window)
        self.window.show()
        self.app.processEvents()

    def close_window(self):
        self.window._exiting = True
        self.window.capture_panel.shutdown()
        self.window.audio_panel.ticker.stop()
        self.window.close()

    def test_font_uses_system_rendering_and_text_has_readable_contrast(self):
        self.assertFalse(ui_font().styleStrategy() & QFont.StyleStrategy.NoSubpixelAntialias)
        for background in (BACKGROUND, SURFACE):
            self.assertGreaterEqual(contrast(TEXT, background), 7)
            self.assertGreaterEqual(contrast(MUTED, background), 4.5)
        self.assertGreaterEqual(contrast("#ffffff", PRIMARY), 4.5)

    def test_header_and_page_controls_fit_at_supported_window_sizes(self):
        window = self.window
        window._title_bar.profile_combo.addItem("W" * 24)
        window._title_bar.profile_combo.setCurrentIndex(1)
        for width, height in ((800, 500), (940, 600), (1400, 850)):
            with self.subTest(size=(width, height)):
                window.resize(width, height)
                self.app.processEvents()
                header = window._title_bar
                self.assertTrue(header.rect().contains(header.profile_controls.geometry()))
                self.assertLess(header.profile_controls.geometry().right(), header.maximize_button.x())
                panel = window.capture_panel
                self.assertTrue(panel.rect().contains(panel.add_button.geometry()))
                self.assertTrue(panel.window_combo.rect().contains(panel.window_combo._arrow.geometry()))
                window.navigation_buttons[1].click()
                self.app.processEvents()
                for card in window.audio_panel.cards:
                    self.assertTrue(card.rect().contains(card.start_button.geometry()))
                    self.assertTrue(card.rect().contains(card.shortcut_label.geometry()))
                    self.assertGreaterEqual(card.volume_label.width(),
                                            card.volume_label.fontMetrics().horizontalAdvance("100%"))
                window.navigation_buttons[0].click()

    def test_page_hierarchy_is_clear_and_empty_state_does_not_repeat_status(self):
        panel = self.window.capture_panel
        title = panel.findChild(QLabel, "pageTitle")
        description = panel.findChild(QLabel, "pageDescription")
        self.assertGreater(title.font().pixelSize(), description.font().pixelSize())
        self.assertGreaterEqual(description.font().pixelSize(), 13)
        self.assertFalse(panel.status_label.isVisible())
        self.assertTrue(panel.empty_state.isVisible())

    def test_long_titles_fit_cards_and_settings_without_losing_the_full_name(self):
        panel = self.window.capture_panel
        source_title = panel.window_combo.itemText(0)
        name = "W" * 24
        records = [dict(name=name, source_title=source_title, region=[0, 0, 90, 40],
                        geometry=[0, 0, 200, 100], visible=False, locked=False,
                        fit_mode="stretch", transparency_percent=0) for _ in range(4)]
        self.assertEqual(panel.load_state(records), [])
        audio = self.window.audio_panel
        for card in audio.cards:
            card.timer.name = name
            card.title.setText(name)
        for width in (800, 940, 1400):
            self.window.resize(width, 600)
            self.window.navigation_buttons[0].click()
            self.app.processEvents()
            for card in panel._cards.values():
                self.assertLessEqual(card.geometry().right(), panel.card_scroll.viewport().width())
                for label in card.findChildren(ElidedLabel):
                    self.assertLessEqual(label.fontMetrics().horizontalAdvance(label.text()), label.width())
            self.window.navigation_buttons[1].click()
            self.app.processEvents()
            for card in audio.cards:
                self.assertLessEqual(card.title.fontMetrics().horizontalAdvance(card.title.text()), card.title.width())
                self.assertEqual(card.title.toolTip(), name)
        self.window.navigation_buttons[0].click()
        panel._select_entry(1)
        panel.details_dialog.show()
        self.app.processEvents()
        self.assertLess(panel.details_dialog.width(), 600)
        self.assertEqual(panel.selected_source.toolTip(), "Janela de origem: " + source_title)
        self.assertEqual(panel.selected_name.toolTip(), name)
        panel.details_dialog.close()

    def test_settings_show_selected_volume_and_use_portuguese_shortcut_hint(self):
        dialog = TimerDialog(self.window.audio_panel)
        dialog.show()
        self.addCleanup(dialog.close)
        self.app.processEvents()
        label_width = dialog.volume_label.width()
        for value in (0, 9, 50, 100):
            dialog.volume_input.setValue(value)
            self.assertEqual(dialog.volume_label.text(), f"{value}%")
            self.assertEqual(dialog.volume_label.width(), label_width)
        dialog.shortcut_input.setKeySequence(QKeySequence("F6"))
        dialog.shortcut_input.clear()
        self.assertEqual(dialog.shortcut_input.findChild(QLineEdit).placeholderText(),
                         "Pressione uma tecla")


if __name__ == "__main__":
    unittest.main()
