"""Seleção e visualização ao vivo por miniaturas DWM."""

import time

from PySide6.QtCore import QPoint, QRect, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QCloseEvent, QMouseEvent, QPaintEvent, QPainter, QPen
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QMessageBox, QWidget

from tibiaenhanced.models import Region
from tibiaenhanced.services.dwm_mirror import DwmMirror
from tibiaenhanced.services.windowing import get_client_area


class _SelectionOverlay(QWidget):
    def __init__(self, owner: QDialog, bounds: QRect) -> None:
        super().__init__(owner, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.WindowStaysOnTopHint |
                         Qt.WindowType.WindowTransparentForInput)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._selection = QRect()
        self.setGeometry(QRect(owner.mapToGlobal(bounds.topLeft()), bounds.size()))

    def set_selection(self, rect: QRect) -> None:
        self._selection = rect
        self.update()

    def paintEvent(self, _event: QPaintEvent) -> None:
        if self._selection.isEmpty():
            return
        painter = QPainter(self)
        painter.fillRect(self._selection, QColor(44, 140, 255, 75))
        painter.setPen(QPen(QColor(30, 115, 235), 3))
        painter.drawRect(self._selection)


class DwmRegionDialog(QDialog):
    """Mostra o cliente inteiro do jogo e converte o arrasto em pixels de origem."""

    def __init__(self, hwnd: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._hwnd = hwnd
        self._mirror: DwmMirror | None = None
        self._overlay: _SelectionOverlay | None = None
        self._start: QPoint | None = None
        self._selected = QRect()
        self._source_size = (1, 1)
        area = get_client_area(hwnd)
        scale = min(1.0, 1000 / area.width, 650 / area.height)
        self._display = QRect(12, 46, max(100, round(area.width * scale)),
                              max(80, round(area.height * scale)))
        self.setWindowTitle("Selecionar região do Tibia")
        self.setFixedSize(self._display.width() + 24, self._display.bottom() + 92)
        heading = QLabel("Arraste no espelho para marcar o recorte.", self)
        heading.setGeometry(12, 8, self.width() - 24, 32)
        self._coordinates = QLabel("Nenhuma região selecionada", self)
        self._coordinates.setGeometry(12, self._display.bottom() + 8, self.width() - 24, 25)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel, self)
        buttons.setGeometry(12, self._display.bottom() + 38, self.width() - 24, 36)
        self._ok = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self._ok.setEnabled(False)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.setCursor(Qt.CursorShape.CrossCursor)

    @property
    def selection(self) -> QRect:
        return self._selected

    def showEvent(self, event) -> None:
        super().showEvent(event)
        QTimer.singleShot(0, self._attach)

    def _attach(self) -> None:
        try:
            self._mirror = DwmMirror(self._hwnd, int(self.winId()))
            self._update_mirror()
            self._overlay = _SelectionOverlay(self, self._display)
            self._overlay.show()
        except RuntimeError as exc:
            QMessageBox.warning(self, "Espelho indisponível", str(exc))
            self.reject()

    def _update_mirror(self) -> None:
        if self._mirror is None:
            return
        area = get_client_area(self._hwnd)
        self._source_size = (area.width, area.height)
        ratio = self.devicePixelRatioF()
        r = self._display
        self._mirror.update(None, tuple(round(v * ratio) for v in
                                        (r.x(), r.y(), r.width(), r.height())))

    def _on_overlay_selection(self, rect: QRect) -> None:
        r = self._display
        source_w, source_h = self._source_size
        x = round(rect.x() * source_w / r.width())
        y = round(rect.y() * source_h / r.height())
        right = round((rect.x() + rect.width()) * source_w / r.width())
        bottom = round((rect.y() + rect.height()) * source_h / r.height())
        self._selected = QRect(x, y, right - x, bottom - y)
        self._ok.setEnabled(self._selected.width() >= 4 and self._selected.height() >= 4)
        self._coordinates.setText(
            f"x={x}, y={y}, {self._selected.width()} × {self._selected.height()} px")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._display.contains(event.position().toPoint()):
            self._start = event.position().toPoint() - self._display.topLeft()
            if self._overlay is not None:
                self._overlay.set_selection(QRect())
            self._selected = QRect()
            self._ok.setEnabled(False)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._start is None:
            return
        point = event.position().toPoint() - self._display.topLeft()
        point = QPoint(max(0, min(point.x(), self._display.width())),
                       max(0, min(point.y(), self._display.height())))
        rect = QRect(min(self._start.x(), point.x()), min(self._start.y(), point.y()),
                     abs(point.x() - self._start.x()), abs(point.y() - self._start.y()))
        if self._overlay is not None:
            self._overlay.set_selection(rect)
        self._on_overlay_selection(rect)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._start is not None:
            self.mouseMoveEvent(event)
            self._start = None

    def moveEvent(self, event) -> None:
        super().moveEvent(event)
        if self._overlay is not None:
            self._overlay.move(self.mapToGlobal(self._display.topLeft()))

    def done(self, result: int) -> None:
        if self._overlay is not None:
            self._overlay.close()
            self._overlay = None
        if self._mirror is not None:
            self._mirror.close()
            self._mirror = None
        super().done(result)


class DwmMirrorWindow(QWidget):
    stopped = Signal(str)

    def __init__(self, hwnd: int, region: Region) -> None:
        super().__init__()
        self._hwnd = hwnd
        self._region = region
        self._mirror: DwmMirror | None = None
        self._stop_reason = "Espelho fechado"
        self._started = time.perf_counter()
        self.setWindowTitle(f"Tibia Enhanced — {region.name}")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.resize(max(180, region.width), max(120, region.height))
        self.setMinimumSize(100, 80)
        self.setStyleSheet("background: black")
        self._timer = QTimer(self)
        self._timer.setInterval(500)
        self._timer.timeout.connect(self._refresh)

    @property
    def elapsed_seconds(self) -> float:
        return time.perf_counter() - self._started

    def showEvent(self, event) -> None:
        super().showEvent(event)
        QTimer.singleShot(0, self._start)

    def _start(self) -> None:
        if self._mirror is not None:
            return
        try:
            self._mirror = DwmMirror(self._hwnd, int(self.winId()))
            self._refresh()
            self._timer.start()
        except RuntimeError as exc:
            self._stop_reason = str(exc)
            self.close()

    def _refresh(self) -> None:
        if self._mirror is None:
            return
        try:
            ratio = self.devicePixelRatioF()
            self._mirror.update(self._region, (0, 0, round(self.width() * ratio),
                                               round(self.height() * ratio)))
        except RuntimeError as exc:
            self._stop_reason = str(exc)
            self.close()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh()

    def closeEvent(self, event: QCloseEvent) -> None:
        self._timer.stop()
        if self._mirror is not None:
            self._mirror.close()
            self._mirror = None
        self.stopped.emit(self._stop_reason)
        super().closeEvent(event)
