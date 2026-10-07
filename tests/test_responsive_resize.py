"""Redimensionamento preserva a janela e só reorganiza cards quando necessário."""

import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QObject, QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from tibiaenhanced.ui.design import load_fonts
from tibiaenhanced.ui.main_window import MainWindow
from tibiaenhanced.ui.theme_manager import theme_manager


class VisibilityWatch(QObject):
    def __init__(self):
        super().__init__()
        self.hides = 0

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Hide:
            self.hides += 1
        return False


class ResponsiveResizeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        load_fonts()

    def setUp(self):
        theme_manager().apply("dark")
        source = SimpleNamespace(hwnd=42, title="Tibia - Teste", executable="client.exe", class_name="TibiaClient")
        with patch("tibiaenhanced.ui.capture_panel.list_windows", return_value=[source]):
            self.window = MainWindow()
        self.window.capture_panel.load_state([
            dict(name=name, source_title=source.title, region=[10, 10, 120, 60],
                 geometry=[0, 0, 200, 100], visible=False, locked=False,
                 fit_mode="stretch", transparency_percent=0)
            for name in ("Vida", "Mana", "Battle", "Skills")])
        self.window.show()
        self.app.processEvents()
        self.addCleanup(self.close_window)

    def close_window(self):
        self.window._exiting = True
        self.window.capture_panel.shutdown()
        self.window.audio_panel.ticker.stop()
        self.window.close()

    def test_resize_within_same_columns_does_not_remove_and_readd_cards(self):
        for index in (0, 1, 3):
            self.window.navigation_buttons[index].click()
            self.window.resize(940, 600)
            self.app.processEvents()
            panel = self.window.pages.currentWidget()
            layout = (panel.card_grid if index == 0 else
                      panel.card_layout if index == 1 else panel.cards_layout)
            with patch.object(layout, "addWidget", wraps=layout.addWidget) as add:
                for width in range(945, 976, 5):
                    self.window.resize(width, 600)
                    self.app.processEvents()
                self.assertEqual(add.call_count, 0)

    def test_resize_crossing_columns_preserves_visibility_cards_and_live_timer(self):
        self.assertFalse(self.window.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground))
        self.assertEqual(self.window.grab().toImage().pixelColor(10, 10).alpha(), 255)
        observer = VisibilityWatch()
        self.window.installEventFilter(observer)
        timer_card = self.window.audio_panel.cards[0]
        timer_card.timer.start()
        timer_card.volume.setValue(37)
        for index in (0, 1, 3):
            self.window.navigation_buttons[index].click()
            panel = self.window.pages.currentWidget()
            cards = (list(panel._cards.values()) if index == 0 else panel.cards
                     if index == 1 else [panel.details_card, panel.qr_card])
            layout = (panel.card_grid if index == 0 else panel.card_layout
                      if index == 1 else panel.cards_layout)
            for width, height in ((1400, 850), (940, 600), (800, 500), (940, 600)) * 2:
                self.window.resize(width, height)
                self.app.processEvents()
                self.assertTrue(self.window.isVisible())
                self.assertEqual(layout.count(), len(cards) + (1 if index == 0 else 0))
                for first, second in zip(cards, cards[1:]):
                    self.assertFalse(first.geometry().intersects(second.geometry()))
                if index < 2:
                    self.assertGreaterEqual(layout.parentWidget().minimumHeight(),
                                            max(card.geometry().bottom() + 1 for card in cards))
                self.assertEqual((panel.scroll if index == 3 else panel.card_scroll)
                                 .horizontalScrollBar().maximum(), 0)
        self.assertEqual(observer.hides, 0)
        self.assertIs(self.window.audio_panel.cards[0], timer_card)
        self.assertTrue(timer_card.timer.running)
        self.assertEqual(timer_card.volume.value(), 37)

    def test_theme_switch_works_with_mouse_and_keyboard_without_moving_pages(self):
        switch = self.window.theme_switch
        self.assertTrue(switch.isChecked())
        self.assertTrue(switch.rect().contains(QPoint(switch.width() - 2, switch.height() // 2)))
        QTest.mouseClick(switch, Qt.MouseButton.LeftButton,
                         pos=QPoint(switch.width() - 2, switch.height() // 2))
        self.assertEqual(theme_manager().mode, "light")
        self.assertFalse(switch.isChecked())
        switch.setFocus()
        QTest.keyClick(switch, Qt.Key.Key_Space)
        self.assertEqual(theme_manager().mode, "dark")
        self.assertTrue(switch.isChecked())
        self.assertEqual(self.window.pages.currentIndex(), 0)


if __name__ == "__main__":
    unittest.main()
