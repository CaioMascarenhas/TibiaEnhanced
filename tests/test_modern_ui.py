"""Recursos e geometria da interface compacta."""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, Qt  # noqa: E402
from PySide6.QtGui import QFontDatabase  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from tibiaenhanced.ui.design import ASSETS, heading_font, icon, load_fonts  # noqa: E402
from tibiaenhanced.ui.main_window import MainWindow  # noqa: E402


class ModernUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_fonts_and_icons_are_bundled_and_load(self) -> None:
        heading, body = load_fonts()
        self.assertIn(heading, QFontDatabase.families())
        self.assertIn(body, QFontDatabase.families())
        self.assertEqual(heading_font(16).weight(), 900)
        self.assertFalse(icon("monitor").isNull())
        for license_file in ("fonts/EXO-OFL.txt", "fonts/QUICKSAND-OFL.txt", "icons/LICENSE"):
            self.assertTrue((ASSETS / license_file).is_file())

    def test_main_window_has_compact_rounded_chrome(self) -> None:
        window = MainWindow()
        self.assertEqual((window.width(), window.height()), (960, 680))
        self.assertEqual((window.minimumWidth(), window.minimumHeight()), (800, 600))
        self.assertTrue(window.windowFlags() & Qt.WindowType.FramelessWindowHint)
        self.assertFalse(window.windowIcon().isNull())
        self.assertEqual(window._resize_edges(QPoint(1, 1)),
                         Qt.Edge.LeftEdge | Qt.Edge.TopEdge)
        window.show()
        self.assertTrue(window._title_bar.isVisible())
        window._title_bar.maximize_button.click()
        self.assertTrue(window.isMaximized())
        window._title_bar.maximize_button.click()
        self.assertFalse(window.isMaximized())
        window.exit_app()


if __name__ == "__main__":
    unittest.main()
