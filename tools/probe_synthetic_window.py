"""Validação manual de captura em uma janela colorida criada pelo próprio teste."""

from PySide6.QtWidgets import QApplication, QWidget

from tibiaenhanced.models import Region
from tibiaenhanced.services.screen_capture import WindowRegionSource, snapshot_window
from tibiaenhanced.services.windowing import enable_per_monitor_dpi_awareness


def _red_fraction(bgra: bytes) -> float:
    return sum(1 for index in range(0, len(bgra), 4)
               if bgra[index + 2] > 200 and bgra[index + 1] < 50 and bgra[index] < 50) / (len(bgra) // 4)


def main() -> None:
    enable_per_monitor_dpi_awareness()
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle("Tibia Enhanced - janela de teste")
    window.setStyleSheet("background-color: rgb(255, 0, 0)")
    window.setGeometry(2200, 180, 260, 180)
    window.show()
    app.processEvents()

    hwnd = int(window.winId())
    region = Region("teste", 20, 20, 100, 70)
    source = WindowRegionSource(hwnd, region)
    try:
        first = source.grab_frame()
        window.move(-1500, 100)
        app.processEvents()
        second = source.grab_frame()
        window.resize(80, 60)
        app.processEvents()
        try:
            source.grab_frame()
        except RuntimeError as exc:
            resize_error = str(exc)
        else:
            raise AssertionError("A redução da janela deveria invalidar o recorte")
        snapshot = snapshot_window(hwnd)
        print({
            "right_monitor_red_fraction": round(_red_fraction(first.bgra), 3),
            "left_monitor_red_fraction": round(_red_fraction(second.bgra), 3),
            "resized_snapshot": (snapshot.width, snapshot.height),
            "resize_error": resize_error,
        })
        if _red_fraction(first.bgra) < 0.9 or _red_fraction(second.bgra) < 0.9:
            raise AssertionError("A imagem colorida não foi capturada corretamente")
    finally:
        source.close()
        window.close()


if __name__ == "__main__":
    main()
