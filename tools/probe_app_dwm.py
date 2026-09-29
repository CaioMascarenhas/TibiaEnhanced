"""Verifica seleção e espelho DWM do aplicativo com a janela real do Tibia."""

import time
import sys

import mss
from PySide6.QtCore import QPoint, QTimer, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QWidget

from tibiaenhanced.models import Region
from tibiaenhanced.services.screen_capture import Frame, frame_is_blank
from tibiaenhanced.services.windowing import (enable_per_monitor_dpi_awareness,
                                              get_client_area, list_windows)
from tibiaenhanced.ui.dwm_windows import DwmMirrorWindow, DwmRegionDialog


def visible_nonblack(hwnd: int, crop: tuple[int, int, int, int] | None = None) -> bool:
    area = get_client_area(hwnd)
    x, y, width, height = crop or (0, 0, area.width, area.height)
    with mss.MSS() as screen:
        shot = screen.grab({"left": area.left + x, "top": area.top + y,
                            "width": width, "height": height})
    return not frame_is_blank(Frame(shot.bgra, shot.width, shot.height,
                                    time.perf_counter()))


def main() -> None:
    enable_per_monitor_dpi_awareness()
    app = QApplication([])
    synthetic = None
    if "--synthetic" in sys.argv:
        synthetic = QWidget()
        synthetic.setWindowTitle("DWM red source")
        synthetic.setStyleSheet("background: red")
        synthetic.setGeometry(100, 100, 500, 350)
        synthetic.show()
        app.processEvents()
        hwnd = int(synthetic.winId())
    else:
        source = next(item for item in list_windows()
                      if item.title == "Tibia" or item.title.startswith("Tibia -"))
        hwnd = source.hwnd
    dialog = DwmRegionDialog(hwnd)
    dialog.move(1200, 100)

    def select() -> None:
        if dialog._mirror is None:
            raise RuntimeError("DWM não abriu no seletor")
        display = dialog._display
        overlay = dialog._overlay
        if overlay is None:
            raise RuntimeError("Camada de seleção não abriu")
        QTest.mousePress(overlay, Qt.MouseButton.LeftButton,
                         pos=QPoint(20, 20))
        QTest.mouseMove(overlay, QPoint(220, 160))
        QTest.mouseRelease(overlay, Qt.MouseButton.LeftButton,
                           pos=QPoint(220, 160))
        app.processEvents()
        r = dialog._display
        print({"selector_nonblack": visible_nonblack(int(dialog.winId()),
                                                     (r.x()+2, r.y()+2, r.width()-4, r.height()-4)),
               "selection": (dialog.selection.x(), dialog.selection.y(),
                             dialog.selection.width(), dialog.selection.height())}, flush=True)
        dialog.accept()

    QTimer.singleShot(1200, select)
    if dialog.exec() != DwmRegionDialog.DialogCode.Accepted:
        raise RuntimeError("Seleção não aceita")
    rect = dialog.selection
    region = Region("Teste", rect.x(), rect.y(), rect.width(), rect.height())
    mirror = DwmMirrorWindow(hwnd, region)
    mirror.move(1200, 100)
    mirror.show()

    def check() -> None:
        print({"mirror_nonblack": visible_nonblack(int(mirror.winId())),
               "mirror_size": (mirror.width(), mirror.height())}, flush=True)
        mirror.close()
        app.quit()

    QTimer.singleShot(1400, check)
    app.exec()


if __name__ == "__main__":
    main()
