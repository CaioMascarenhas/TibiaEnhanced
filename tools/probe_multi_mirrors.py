"""Teste manual de dois recortes DWM e clique através de janela bloqueada."""

import ctypes
import time

import mss
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from tibiaenhanced.models import Region
from tibiaenhanced.services.windowing import enable_per_monitor_dpi_awareness, get_client_area
from tibiaenhanced.ui.dwm_windows import DwmMirrorWindow


class ColorSource(QWidget):
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(0, 0, 200, 240, QColor("red"))
        painter.fillRect(200, 0, 200, 240, QColor("blue"))


def center_color(hwnd: int) -> tuple[int, int, int]:
    area = get_client_area(hwnd)
    with mss.MSS() as screen:
        shot = screen.grab({"left": area.left, "top": area.top,
                            "width": area.width, "height": area.height})
    return shot.pixel(shot.width // 2, shot.height // 2)


def main() -> None:
    enable_per_monitor_dpi_awareness()
    app = QApplication([])
    source = ColorSource()
    source.setWindowTitle("DWM synthetic source")
    source.setGeometry(100, 100, 400, 240)
    source.show()

    clicks = 0
    underlay = QPushButton("UNDERLAY")
    underlay.setGeometry(1200, 100, 220, 150)

    def clicked() -> None:
        nonlocal clicks
        clicks += 1

    underlay.clicked.connect(clicked)
    underlay.show()
    app.processEvents()

    red = DwmMirrorWindow(int(source.winId()), Region("red", 0, 0, 200, 240))
    red.setGeometry(1200, 100, 220, 150)
    red.show()
    blue = DwmMirrorWindow(int(source.winId()), Region("blue", 200, 0, 200, 240))
    blue.setGeometry(1500, 100, 220, 150)
    blue.show()

    def check() -> None:
        user32 = ctypes.WinDLL("user32")
        print({"red": center_color(int(red.winId())),
               "blue": center_color(int(blue.winId())),
               "active": (red.active, blue.active)}, flush=True)
        red.set_locked(True)
        QTest.qWait(200)
        print({"red_locked": center_color(int(red.winId())),
               "locked": red.locked}, flush=True)
        user32.SetCursorPos(1310, 175)
        user32.mouse_event(0x0002, 0, 0, 0, 0)
        user32.mouse_event(0x0004, 0, 0, 0, 0)
        QTest.qWait(200)
        print({"underlay_clicks": clicks}, flush=True)
        red.close()
        print({"after_hiding_one": (red.active, blue.active)}, flush=True)
        blue.close()
        print({"after_hiding_all": (red.active, blue.active)}, flush=True)
        app.quit()

    QTimer.singleShot(1200, check)
    app.exec()


if __name__ == "__main__":
    main()
