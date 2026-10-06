"""Escolha de um retângulo sobre uma imagem da janela selecionada."""

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QImage, QMouseEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget

from .dialog_shell import StyledDialog


class _SelectionCanvas(QWidget):
    selection_changed = Signal(QRect)

    def __init__(self, image: QImage) -> None:
        super().__init__()
        self._image = image
        self._start: QPoint | None = None
        self._selection = QRect()
        self.setFixedSize(image.size())
        self.setCursor(Qt.CursorShape.CrossCursor)

    @property
    def selection(self) -> QRect:
        return self._selection

    def _clamp(self, point: QPoint) -> QPoint:
        return QPoint(
            max(0, min(point.x(), self._image.width())),
            max(0, min(point.y(), self._image.height())),
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._start = self._clamp(event.position().toPoint())
            self._selection = QRect()
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._start is not None:
            end = self._clamp(event.position().toPoint())
            self._selection = QRect(
                min(self._start.x(), end.x()),
                min(self._start.y(), end.y()),
                abs(end.x() - self._start.x()),
                abs(end.y() - self._start.y()),
            )
            self.selection_changed.emit(self._selection)
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouseMoveEvent(event)
            self._start = None

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.drawPixmap(0, 0, QPixmap.fromImage(self._image))
        if not self._selection.isEmpty():
            painter.fillRect(self._selection, QColor(44, 140, 255, 65))
            painter.setPen(QPen(QColor(30, 115, 235), 2))
            painter.drawRect(self._selection)


class RegionDialog(StyledDialog):
    def __init__(self, image: QImage, parent: QWidget | None = None) -> None:
        super().__init__(parent, "Selecionar região")
        self.resize(min(image.width() + 40, 1100), min(image.height() + 130, 800))

        layout = self.content_layout
        instruction = QLabel("Arraste sobre a imagem para marcar o recorte. As coordenadas são medidas em pixels da captura.")
        instruction.setWordWrap(True)
        layout.addWidget(instruction)

        self._canvas = _SelectionCanvas(image)
        scroll = QScrollArea()
        scroll.setWidget(self._canvas)
        layout.addWidget(scroll)

        self._coordinates = QLabel("Nenhuma região selecionada")
        layout.addWidget(self._coordinates)
        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(cancel)
        self._ok = QPushButton("Criar recorte")
        self._ok.setObjectName("primaryButton")
        self._ok.setEnabled(False)
        self._ok.clicked.connect(self.accept)
        buttons.addWidget(self._ok)
        layout.addLayout(buttons)
        self._canvas.selection_changed.connect(self._on_selection_changed)

    @property
    def selection(self) -> QRect:
        return self._canvas.selection

    def _on_selection_changed(self, rect: QRect) -> None:
        self._ok.setEnabled(rect.width() >= 4 and rect.height() >= 4)
        self._coordinates.setText(
            f"x={rect.x()}, y={rect.y()}, largura={rect.width()}, altura={rect.height()}"
        )
