"""Moldura compartilhada pelos diálogos de configuração."""

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from .design import heading_font, icon


class _DialogHeader(QFrame):
    def __init__(self, dialog: QDialog, title: str) -> None:
        super().__init__(dialog)
        self.dialog = dialog
        self._drag_origin: QPoint | None = None
        self.setObjectName("dialogHeader")
        self.setFixedHeight(34)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 5)
        title_label = QLabel(title)
        title_label.setObjectName("dialogTitle")
        title_label.setFont(heading_font(13))
        # Deixe o cabeçalho livre para arrastar inclusive sobre o título.
        title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        row.addWidget(title_label)
        row.addStretch()
        close = QPushButton()
        close.setObjectName("iconButton")
        close.setFixedSize(25, 25)
        close.setIcon(icon("x", "#e9edf6", 15))
        close.setToolTip("Fechar")
        close.setAccessibleName("Fechar")
        close.clicked.connect(dialog.reject)
        row.addWidget(close)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            handle = self.dialog.windowHandle()
            if handle is None or not handle.startSystemMove():
                self._drag_origin = event.globalPosition().toPoint() - self.dialog.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_origin is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.dialog.move(event.globalPosition().toPoint() - self._drag_origin)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_origin = None
        super().mouseReleaseEvent(event)


class StyledDialog(QDialog):
    def __init__(self, parent, title: str) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(7, 7, 7, 7)
        surface = QFrame()
        surface.setObjectName("dialogSurface")
        outer.addWidget(surface)
        self.content_layout = QVBoxLayout(surface)
        self.content_layout.setContentsMargins(16, 11, 16, 14)
        self.content_layout.setSpacing(9)
        self.content_layout.addWidget(_DialogHeader(self, title))
