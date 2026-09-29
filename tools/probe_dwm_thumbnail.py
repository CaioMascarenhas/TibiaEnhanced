"""Testa uma miniatura DWM da janela do Tibia em uma janela própria."""

import ctypes
import sys
from ctypes import wintypes

from PySide6.QtCore import QEventLoop, QTimer, Qt
from PySide6.QtWidgets import QApplication, QWidget

from tibiaenhanced.services.screen_capture import Frame, frame_is_blank
from tibiaenhanced.services.windowing import enable_per_monitor_dpi_awareness, get_client_area, list_windows

import mss
import time


class Rect(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG), ("right", wintypes.LONG), ("bottom", wintypes.LONG)]


class ThumbnailProperties(ctypes.Structure):
    _fields_ = [
        ("flags", wintypes.DWORD),
        ("destination", Rect),
        ("source", Rect),
        ("opacity", ctypes.c_ubyte),
        ("visible", wintypes.BOOL),
        ("client_only", wintypes.BOOL),
    ]


def main() -> None:
    source = next(
        (item for item in list_windows() if item.title == "Tibia" or item.title.startswith("Tibia -")),
        None,
    )
    if source is None:
        raise SystemExit("Janela do Tibia não encontrada")
    enable_per_monitor_dpi_awareness()
    app = QApplication([])
    destination = QWidget()
    destination.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
    destination.setWindowTitle("Tibia Enhanced - teste de miniatura DWM")
    destination.setStyleSheet("background: black")
    destination.setGeometry(1200, 100, 600, 400)
    destination.show()
    app.processEvents()
    target = destination
    if "--child" in sys.argv:
        target = QWidget(destination)
        target.setGeometry(20, 20, 500, 300)
        target.setAttribute(__import__("PySide6.QtCore", fromlist=["Qt"]).Qt.WidgetAttribute.WA_NativeWindow)
        target.show()
        app.processEvents()

    dwm = ctypes.WinDLL("dwmapi", use_last_error=True)
    dwm.DwmRegisterThumbnail.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.POINTER(wintypes.HANDLE)]
    dwm.DwmRegisterThumbnail.restype = ctypes.c_long
    dwm.DwmUpdateThumbnailProperties.argtypes = [wintypes.HANDLE, ctypes.POINTER(ThumbnailProperties)]
    dwm.DwmUpdateThumbnailProperties.restype = ctypes.c_long
    dwm.DwmUnregisterThumbnail.argtypes = [wintypes.HANDLE]
    dwm.DwmUnregisterThumbnail.restype = ctypes.c_long

    thumbnail = wintypes.HANDLE()
    result = dwm.DwmRegisterThumbnail(int(target.winId()), source.hwnd, ctypes.byref(thumbnail))
    if result != 0:
        raise RuntimeError(f"DwmRegisterThumbnail falhou: {result:#x}")
    try:
        area = get_client_area(source.hwnd)
        properties = ThumbnailProperties(
            flags=0x1 | 0x2 | 0x4 | 0x8 | 0x10,
            destination=Rect(0, 0, target.width(), target.height()),
            source=Rect(0, 0, area.width, area.height),
            opacity=255,
            visible=True,
            client_only=True,
        )
        result = dwm.DwmUpdateThumbnailProperties(thumbnail, ctypes.byref(properties))
        if result != 0:
            raise RuntimeError(f"DwmUpdateThumbnailProperties falhou: {result:#x}")

        loop = QEventLoop()
        QTimer.singleShot(1500, loop.quit)
        loop.exec()
        own_area = get_client_area(int(target.winId()))
        with mss.MSS() as screen:
            shot = screen.grab({"left": own_area.left, "top": own_area.top, "width": own_area.width, "height": own_area.height})
        frame = Frame(shot.bgra, shot.width, shot.height, time.perf_counter())
        print({"registered": True, "destination_size": (frame.width, frame.height), "thumbnail_blank": frame_is_blank(frame)})
        QTimer.singleShot(180000 if "--inspect" in sys.argv else 3000, app.quit)
        app.exec()
    finally:
        dwm.DwmUnregisterThumbnail(thumbnail)
        destination.close()


if __name__ == "__main__":
    main()
