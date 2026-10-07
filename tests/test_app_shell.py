"""Testes do fluxo mínimo da issue #1, sem capturar o jogo."""

import os
import time
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEventLoop, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication, QStackedWidget  # noqa: E402

from tibiaenhanced.services.capture import CaptureService  # noqa: E402
from tibiaenhanced.ui.main_window import MainWindow  # noqa: E402


class _SlowFrameSource:
    def grab_frame(self) -> object:
        time.sleep(0.03)
        return object()

    def close(self) -> None:
        pass


class AppShellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_main_window_has_expected_sections(self) -> None:
        window = MainWindow()
        window.show()
        self.assertTrue(window.isVisible())
        self.assertIsInstance(window.pages, QStackedWidget)
        self.assertEqual([button.text() for button in window.navigation_buttons],
                         ["Recortes", "Alertas", "Tools", "Apoiar"])
        for index, page in enumerate((window.capture_panel, window.audio_panel, window.tools_panel, window.donate_panel)):
            window.navigation_buttons[index].click()
            self.assertIs(window.pages.currentWidget(), page)
            self.assertTrue(window.navigation_buttons[index].isChecked())
            self.assertEqual(sum(button.isChecked() for button in window.navigation_buttons), 1)
        window.exit_app()

    def test_capture_worker_keeps_event_loop_responsive(self) -> None:
        service = CaptureService()
        loop = QEventLoop()
        ticks = 0
        frames = 0
        stopped = False

        def tick() -> None:
            nonlocal ticks
            ticks += 1

        def on_frame(_frame: object) -> None:
            nonlocal frames
            frames += 1

        def on_stopped() -> None:
            nonlocal stopped
            stopped = True
            loop.quit()

        timer = QTimer()
        timer.timeout.connect(tick)
        service.frame_ready.connect(on_frame)
        service.stopped.connect(on_stopped)
        timer.start(10)
        service.start(_SlowFrameSource)
        QTimer.singleShot(200, service.stop)
        QTimer.singleShot(2000, loop.quit)
        loop.exec()
        timer.stop()
        service.stop()

        self.assertTrue(stopped, "A thread de captura não parou")
        self.assertGreaterEqual(ticks, 5)
        self.assertGreaterEqual(frames, 2)
        self.assertFalse(service.running)


if __name__ == "__main__":
    unittest.main()
