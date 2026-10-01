"""Seleção e visualização ao vivo por miniaturas DWM."""

import ctypes
import time
from ctypes import wintypes

from PySide6.QtCore import QPoint, QRect, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QCloseEvent, QContextMenuEvent, QCursor, QMouseEvent, QPaintEvent, QPainter, QPainterPath, QPen, QRegion, QWheelEvent
from PySide6.QtWidgets import (QApplication, QDialog, QDialogButtonBox, QLabel, QLineEdit,
                               QMenu, QMessageBox, QPushButton, QWidget)

from .design import icon

from tibiaenhanced.models import Region
from tibiaenhanced.services.dwm_mirror import DwmMirror
from tibiaenhanced.services.windowing import get_client_area


_user32 = ctypes.WinDLL("user32", use_last_error=True)
_user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
_user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
_user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]
_user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t
_user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
_user32.SetWindowPos.restype = wintypes.BOOL

_GWL_EXSTYLE = -20
_WS_EX_TRANSPARENT = 0x00000020
_WS_EX_LAYERED = 0x00080000
_WS_EX_NOACTIVATE = 0x08000000
_LOCK_STYLES = _WS_EX_TRANSPARENT | _WS_EX_LAYERED | _WS_EX_NOACTIVATE
_SWP_NOSIZE = 0x0001
_SWP_NOMOVE = 0x0002
_SWP_NOZORDER = 0x0004
_SWP_NOACTIVATE = 0x0010
_SWP_FRAMECHANGED = 0x0020


def destination_rect(source: tuple[int, int], target: tuple[int, int],
                     fit_mode: str) -> tuple[int, int, int, int]:
    """Calcula a área da miniatura em pixels, com bordas pretas quando necessário."""
    source_w, source_h = source
    target_w, target_h = target
    if min(source_w, source_h, target_w, target_h) < 1:
        raise ValueError("Dimensões do espelho precisam ser positivas")
    if fit_mode == "stretch":
        return (0, 0, target_w, target_h)
    if fit_mode != "contain":
        raise ValueError(f"Modo de ajuste desconhecido: {fit_mode}")
    scale = min(target_w / source_w, target_h / source_h)
    width = max(1, round(source_w * scale))
    height = max(1, round(source_h * scale))
    return ((target_w - width) // 2, (target_h - height) // 2, width, height)


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

    def __init__(self, hwnd: int, parent: QWidget | None = None, *,
                 suggested_name: str = "Recorte 1",
                 source_title: str = "Janela selecionada") -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint)
        self._drag_origin: QPoint | None = None
        self._hwnd = hwnd
        self._mirror: DwmMirror | None = None
        self._overlay: _SelectionOverlay | None = None
        self._start: QPoint | None = None
        self._selected = QRect()
        area = get_client_area(hwnd)
        self._source_size = (area.width, area.height)
        self._zoom = 1.0
        self._view_x = 0.0
        self._view_y = 0.0
        self._pan_origin: QPoint | None = None
        self._pan_view = (0.0, 0.0)
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        available = screen.availableGeometry() if screen else QRect(0, 0, 1280, 800)
        max_width = max(300, min(1000, available.width() - 80))
        max_height = max(180, min(650, available.height() - 250))
        scale = min(1.0, max_width / area.width, max_height / area.height)
        self._display = QRect(12, 46, max(100, round(area.width * scale)),
                              max(80, round(area.height * scale)))
        self.setWindowTitle("Novo recorte")
        self.setObjectName("dwmRegionDialog")
        self.setFixedSize(self._display.width() + 24, self._display.bottom() + 188)
        outline = QPainterPath()
        outline.addRoundedRect(self.rect().adjusted(0, 0, -1, -1), 12, 12)
        self.setMask(QRegion(outline.toFillPolygon().toPolygon()))
        self.setStyleSheet("QDialog#dwmRegionDialog { background: #292c40; color: #f1f3f8; }")
        heading = QLabel("Arraste na imagem para marcar o recorte.", self)
        heading.setGeometry(12, 4, self.width() - 58, 20)
        heading.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        close = QPushButton(self)
        close.setObjectName("iconButton")
        close.setGeometry(self.width() - 35, 5, 25, 25)
        close.setIcon(icon("x", "#e9edf6", 15))
        close.setToolTip("Fechar")
        close.setAccessibleName("Fechar")
        close.clicked.connect(self.reject)
        source = QLabel(f"Janela de origem: {source_title}", self)
        source.setObjectName("mutedText")
        source.setGeometry(12, 25, self.width() - 24, 18)
        source.setToolTip(source_title)
        source.setText(source.fontMetrics().elidedText(
            f"Janela de origem: {source_title}", Qt.TextElideMode.ElideRight, source.width()))
        controls_y = self._display.bottom() + 8
        zoom_label = QLabel("Zoom", self)
        zoom_label.setGeometry(12, controls_y, 42, 28)
        self.zoom_out = QPushButton("−", self)
        self.zoom_out.setGeometry(57, controls_y, 28, 28)
        self.zoom_out.setToolTip("Reduzir zoom")
        self.zoom_out.clicked.connect(lambda: self._set_zoom(self._zoom / 1.25))
        self.zoom_value = QLabel("100%", self)
        self.zoom_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_value.setGeometry(89, controls_y, 53, 28)
        self.zoom_value.setToolTip("Use Ctrl + roda do mouse para ampliar; botão do meio para mover")
        self.zoom_in = QPushButton("+", self)
        self.zoom_in.setGeometry(146, controls_y, 28, 28)
        self.zoom_in.setToolTip("Ampliar zoom")
        self.zoom_in.clicked.connect(lambda: self._set_zoom(self._zoom * 1.25))
        self.zoom_out.setEnabled(False)
        pan_hint = QLabel("Meio: mover", self)
        pan_hint.setObjectName("mutedText")
        pan_hint.setGeometry(181, controls_y, self.width() - 193, 28)
        pan_hint.setToolTip("Use a roda do mouse para zoom e arraste com o botão do meio para mover a imagem")
        self._coordinates = QLabel("Nenhuma área selecionada", self)
        self._coordinates.setGeometry(12, self._display.bottom() + 44, self.width() - 24, 25)
        name_label = QLabel("Nome do recorte", self)
        name_label.setGeometry(12, self._display.bottom() + 75, self.width() - 24, 20)
        self.name_input = QLineEdit(self)
        self.name_input.setText(suggested_name)
        self.name_input.setGeometry(12, self._display.bottom() + 97,
                                    self.width() - 24, 32)
        self.name_input.textChanged.connect(self._update_ok_state)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel, self)
        buttons.setGeometry(12, self._display.bottom() + 140, self.width() - 24, 36)
        self._ok = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self._ok.setText("Criar espelho")
        self._ok.setEnabled(False)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.setCursor(Qt.CursorShape.CrossCursor)

    @property
    def selection(self) -> QRect:
        return self._selected

    @property
    def name(self) -> str:
        return self.name_input.text().strip()

    def _update_ok_state(self) -> None:
        self._ok.setEnabled(self._selected.width() >= 4 and
                            self._selected.height() >= 4 and bool(self.name))

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
        region = self._view_region()
        ratio = self.devicePixelRatioF()
        r = self._display
        self._mirror.update(region, tuple(round(v * ratio) for v in
                                          (r.x(), r.y(), r.width(), r.height())))

    def _view_region(self) -> Region:
        source_w, source_h = self._source_size
        width = max(1, round(source_w / self._zoom))
        height = max(1, round(source_h / self._zoom))
        x = max(0, min(round(self._view_x), source_w - width))
        y = max(0, min(round(self._view_y), source_h - height))
        return Region("Zoom", x, y, width, height)

    def _set_zoom(self, zoom: float, anchor: QPoint | None = None) -> None:
        new_zoom = max(1.0, min(8.0, zoom))
        if new_zoom == self._zoom:
            return
        view = self._view_region()
        if anchor is None:
            anchor = QPoint(self._display.width() // 2, self._display.height() // 2)
        fx = max(0.0, min(1.0, anchor.x() / self._display.width()))
        fy = max(0.0, min(1.0, anchor.y() / self._display.height()))
        source_x = view.x + fx * view.width
        source_y = view.y + fy * view.height
        self._zoom = new_zoom
        source_w, source_h = self._source_size
        width = max(1, round(source_w / new_zoom))
        height = max(1, round(source_h / new_zoom))
        self._view_x = max(0.0, min(source_x - fx * width, source_w - width))
        self._view_y = max(0.0, min(source_y - fy * height, source_h - height))
        self.zoom_value.setText(f"{round(new_zoom * 100)}%")
        self.zoom_out.setEnabled(new_zoom > 1.0)
        self.zoom_in.setEnabled(new_zoom < 8.0)
        self._update_mirror()
        self._sync_overlay_selection()

    def _sync_overlay_selection(self) -> None:
        if self._overlay is None:
            return
        if self._selected.isEmpty():
            self._overlay.set_selection(QRect())
            return
        view = self._view_region()
        r = self._display
        left = round((self._selected.left() - view.x) * r.width() / view.width)
        top = round((self._selected.top() - view.y) * r.height() / view.height)
        right = round((self._selected.x() + self._selected.width() - view.x) * r.width() / view.width)
        bottom = round((self._selected.y() + self._selected.height() - view.y) * r.height() / view.height)
        self._overlay.set_selection(QRect(left, top, right - left, bottom - top).intersected(
            QRect(0, 0, r.width(), r.height())))

    def _on_overlay_selection(self, rect: QRect) -> None:
        r = self._display
        view = self._view_region()
        x = view.x + round(rect.x() * view.width / r.width())
        y = view.y + round(rect.y() * view.height / r.height())
        right = view.x + round((rect.x() + rect.width()) * view.width / r.width())
        bottom = view.y + round((rect.y() + rect.height()) * view.height / r.height())
        self._selected = QRect(x, y, right - x, bottom - y)
        self._update_ok_state()
        self._coordinates.setText(
            f"x={x}, y={y}, {self._selected.width()} × {self._selected.height()} px")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton and self._display.contains(event.position().toPoint()):
            self._pan_origin = event.position().toPoint()
            self._pan_view = (self._view_x, self._view_y)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 25:
            handle = self.windowHandle()
            if handle is None or not handle.startSystemMove():
                self._drag_origin = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._display.contains(event.position().toPoint()):
            self._start = event.position().toPoint() - self._display.topLeft()
            if self._overlay is not None:
                self._overlay.set_selection(QRect())
            self._selected = QRect()
            self._coordinates.setText("Nenhuma área selecionada")
            self._update_ok_state()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._pan_origin is not None and event.buttons() & Qt.MouseButton.MiddleButton:
            delta = event.position().toPoint() - self._pan_origin
            view = self._view_region()
            source_w, source_h = self._source_size
            self._view_x = max(0.0, min(self._pan_view[0] - delta.x() * view.width / self._display.width(), source_w - view.width))
            self._view_y = max(0.0, min(self._pan_view[1] - delta.y() * view.height / self._display.height(), source_h - view.height))
            self._update_mirror()
            self._sync_overlay_selection()
            event.accept()
            return
        if self._drag_origin is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_origin)
            event.accept()
            return
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
        if event.button() == Qt.MouseButton.MiddleButton and self._pan_origin is not None:
            self._pan_origin = None
            self.setCursor(Qt.CursorShape.CrossCursor)
            event.accept()
            return
        self._drag_origin = None
        if event.button() == Qt.MouseButton.LeftButton and self._start is not None:
            self.mouseMoveEvent(event)
            self._start = None

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self._display.contains(event.position().toPoint()):
            steps = event.angleDelta().y() / 120
            if steps:
                self._set_zoom(self._zoom * (1.25 ** steps), event.position().toPoint() - self._display.topLeft())
            event.accept()
            return
        super().wheelEvent(event)

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
    action_requested = Signal(str)

    def __init__(self, hwnd: int, region: Region, *, fit_mode: str = "contain") -> None:
        super().__init__()
        self._hwnd = hwnd
        self._region = region
        self._fit_mode = fit_mode
        self._locked = False
        self._opacity_percent = 100
        self._original_exstyle: int | None = None
        self._drag_origin: QPoint | None = None
        self._drag_geometry: QRect | None = None
        self._resize_edges = Qt.Edges()
        self._mirror: DwmMirror | None = None
        self._stop_reason = "Espelho fechado"
        self._started = time.perf_counter()
        self.setWindowTitle(f"Tibia Enhanced — {region.name}")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.resize(max(32, region.width), max(32, region.height))
        self.setMinimumSize(24, 24)
        self.setStyleSheet("background: black")
        self.setMouseTracking(True)
        self._timer = QTimer(self)
        self._timer.setInterval(500)
        self._timer.timeout.connect(self._refresh)

    @property
    def elapsed_seconds(self) -> float:
        return time.perf_counter() - self._started

    @property
    def active(self) -> bool:
        return self._mirror is not None

    @property
    def locked(self) -> bool:
        return self._locked

    @property
    def opacity_percent(self) -> int:
        return self._opacity_percent

    def rename(self, name: str) -> None:
        self._region = Region(name, self._region.x, self._region.y,
                              self._region.width, self._region.height)
        self.setWindowTitle(f"Tibia Enhanced — {name}")

    def set_fit_mode(self, mode: str) -> None:
        if mode not in ("contain", "stretch"):
            raise ValueError(f"Modo de ajuste desconhecido: {mode}")
        self._fit_mode = mode
        self._refresh()

    def set_locked(self, locked: bool) -> None:
        self._locked = locked
        if self.isVisible():
            self._apply_lock_style()

    def set_opacity_percent(self, percent: int) -> None:
        if not 10 <= percent <= 100:
            raise ValueError("A transparência deve estar entre 10% e 100%")
        self._opacity_percent = percent
        self.setWindowOpacity(percent / 100)
        if self.isVisible():
            self._apply_lock_style()

    def _apply_lock_style(self) -> None:
        hwnd = int(self.winId())
        current = _user32.GetWindowLongPtrW(hwnd, _GWL_EXSTYLE)
        if self._original_exstyle is None:
            self._original_exstyle = current
        if self._locked:
            desired = current | _LOCK_STYLES
        else:
            desired = current & ~(_WS_EX_TRANSPARENT | _WS_EX_NOACTIVATE)
            if self._opacity_percent == 100 and not self._original_exstyle & _WS_EX_LAYERED:
                desired &= ~_WS_EX_LAYERED
        if desired != current:
            ctypes.set_last_error(0)
            previous = _user32.SetWindowLongPtrW(hwnd, _GWL_EXSTYLE, desired)
            if previous == 0 and ctypes.get_last_error():
                raise RuntimeError("Não foi possível alterar o bloqueio do espelho")
            if not _user32.SetWindowPos(hwnd, None, 0, 0, 0, 0,
                                        _SWP_NOSIZE | _SWP_NOMOVE | _SWP_NOZORDER |
                                        _SWP_NOACTIVATE | _SWP_FRAMECHANGED):
                raise RuntimeError("Não foi possível atualizar o bloqueio do espelho")

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._stop_reason = "Espelho fechado"
        self._started = time.perf_counter()
        QTimer.singleShot(0, self._start)

    def _start(self) -> None:
        if self._mirror is not None:
            return
        try:
            self._apply_lock_style()
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
            target = (round(self.width() * ratio), round(self.height() * ratio))
            box = destination_rect((self._region.width, self._region.height),
                                   target, self._fit_mode)
            self._mirror.update(self._region, box)
        except RuntimeError as exc:
            self._stop_reason = str(exc)
            self.close()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh()

    def _edges_at(self, point: QPoint) -> Qt.Edges:
        margin = min(9, max(4, min(self.width(), self.height()) // 6))
        edges = Qt.Edges()
        if point.x() < margin:
            edges |= Qt.Edge.LeftEdge
        elif point.x() >= self.width() - margin:
            edges |= Qt.Edge.RightEdge
        if point.y() < margin:
            edges |= Qt.Edge.TopEdge
        elif point.y() >= self.height() - margin:
            edges |= Qt.Edge.BottomEdge
        return edges

    def _update_edge_cursor(self, edges: Qt.Edges) -> None:
        if edges in (Qt.Edge.LeftEdge | Qt.Edge.TopEdge,
                     Qt.Edge.RightEdge | Qt.Edge.BottomEdge):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edges in (Qt.Edge.RightEdge | Qt.Edge.TopEdge,
                       Qt.Edge.LeftEdge | Qt.Edge.BottomEdge):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif edges & (Qt.Edge.LeftEdge | Qt.Edge.RightEdge):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edges & (Qt.Edge.TopEdge | Qt.Edge.BottomEdge):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.setCursor(Qt.CursorShape.SizeAllCursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton or self._locked:
            return
        edges = self._edges_at(event.position().toPoint())
        self._resize_edges = edges
        handle = self.windowHandle()
        if handle is not None:
            started = handle.startSystemResize(edges) if edges else handle.startSystemMove()
            if started:
                event.accept()
                return
        self._drag_origin = event.globalPosition().toPoint()
        self._drag_geometry = self.geometry()
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_origin is None or self._drag_geometry is None:
            if not self._locked:
                self._update_edge_cursor(self._edges_at(event.position().toPoint()))
            return
        delta = event.globalPosition().toPoint() - self._drag_origin
        initial = self._drag_geometry
        if not self._resize_edges:
            self.move(initial.topLeft() + delta)
            return
        left, top, right, bottom = initial.left(), initial.top(), initial.right(), initial.bottom()
        if self._resize_edges & Qt.Edge.LeftEdge:
            left = min(left + delta.x(), right - self.minimumWidth() + 1)
        if self._resize_edges & Qt.Edge.RightEdge:
            right = max(right + delta.x(), left + self.minimumWidth() - 1)
        if self._resize_edges & Qt.Edge.TopEdge:
            top = min(top + delta.y(), bottom - self.minimumHeight() + 1)
        if self._resize_edges & Qt.Edge.BottomEdge:
            bottom = max(bottom + delta.y(), top + self.minimumHeight() - 1)
        self.setGeometry(QRect(QPoint(left, top), QPoint(right, bottom)))

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_origin = None
            self._drag_geometry = None
            self._resize_edges = Qt.Edges()

    def _context_menu(self) -> QMenu:
        menu = QMenu(self)
        menu.addAction("Ocultar espelho", lambda: self.action_requested.emit("hide"))
        menu.addAction("Bloquear cliques", lambda: self.action_requested.emit("lock"))
        menu.addSeparator()
        menu.addAction("Excluir recorte", lambda: self.action_requested.emit("delete"))
        return menu

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        if self._locked:
            return
        menu = self._context_menu()
        menu.exec(event.globalPos())
        menu.deleteLater()
        event.accept()

    def closeEvent(self, event: QCloseEvent) -> None:
        self._timer.stop()
        if self._mirror is not None:
            self._mirror.close()
            self._mirror = None
        self.stopped.emit(self._stop_reason)
        super().closeEvent(event)
