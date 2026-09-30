"""Recursos e geometria da interface compacta."""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QPoint, Qt  # noqa: E402
from PySide6.QtGui import QFontDatabase  # noqa: E402
from PySide6.QtWidgets import QApplication, QFrame, QPushButton  # noqa: E402
from tibiaenhanced.ui.dialog_shell import StyledDialog  # noqa: E402
from tibiaenhanced.ui.audio_panel import TimerDialog, AudioPanel  # noqa: E402
from tibiaenhanced.ui.capture_panel import CapturePanel  # noqa: E402
from tibiaenhanced.ui.design import CompactSlider  # noqa: E402

from tibiaenhanced.ui.design import ASSETS, HoverEffects, InteractionCursors, heading_font, icon, load_fonts  # noqa: E402
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
        self.assertEqual(body, "Inter")
        for license_file in ("fonts/EXO-OFL.txt", "fonts/INTER-OFL.txt", "icons/LICENSE"):
            self.assertTrue((ASSETS / license_file).is_file())

    def test_main_window_has_compact_rounded_chrome(self) -> None:
        window = MainWindow()
        self.assertEqual((window.width(), window.height()), (680, 460))
        self.assertEqual((window.minimumWidth(), window.minimumHeight()), (560, 380))
        self.assertIn("https://github.com/CaioMascarenhas", window.author_link.text())
        self.assertTrue(window.author_link.openExternalLinks())
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

    def test_dynamic_buttons_have_pointer_and_disabled_buttons_arrow(self) -> None:
        cursors = InteractionCursors(self.app)
        self.app.installEventFilter(cursors)
        button = QPushButton("Novo")
        button.ensurePolished()
        self.assertEqual(button.cursor().shape(), Qt.CursorShape.PointingHandCursor)
        button.setEnabled(False)
        self.assertEqual(button.cursor().shape(), Qt.CursorShape.ArrowCursor)
        button.setEnabled(True)
        self.assertEqual(button.cursor().shape(), Qt.CursorShape.PointingHandCursor)
        self.app.removeEventFilter(cursors)

    def test_settings_dialogs_share_rounded_chrome_and_audio_uses_blue(self) -> None:
        panel = AudioPanel()
        timer_dialog = TimerDialog(panel, panel.cards[0].timer)
        self.assertIsInstance(timer_dialog, StyledDialog)
        self.assertTrue(timer_dialog.windowFlags() & Qt.WindowType.FramelessWindowHint)
        self.assertEqual(timer_dialog.volume_input.accent, "#4ba6ff")
        self.assertEqual(panel.master_volume.accent, "#4ba6ff")
        capture = CapturePanel()
        self.assertIsInstance(capture.details_dialog, StyledDialog)
        self.assertTrue(capture.details_dialog.windowFlags() & Qt.WindowType.FramelessWindowHint)
        self.assertIsInstance(capture.transparency_slider, CompactSlider)
        self.assertEqual(capture.transparency_slider.accent, "#5a9dff")
        panel.close()
        capture.close()

    def test_primary_buttons_and_cards_receive_hover_elevation(self) -> None:
        effects = HoverEffects(self.app)
        self.app.installEventFilter(effects)
        for widget, name in ((QPushButton("Criar"), "primaryButton"),
                             (QFrame(), "timerCard")):
            widget.setObjectName(name)
            widget.ensurePolished()
            self.assertIsNotNone(widget.graphicsEffect())
            QApplication.sendEvent(widget, QEvent(QEvent.Type.Enter))
            self.assertIn(widget, effects._animations)
            widget.close()
        self.app.removeEventFilter(effects)


if __name__ == "__main__":
    unittest.main()
