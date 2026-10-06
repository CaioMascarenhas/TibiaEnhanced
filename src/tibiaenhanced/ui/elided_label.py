"""Rótulo de uma linha que mantém nomes longos dentro do espaço disponível."""

from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import QLabel, QSizePolicy


class ElidedLabel(QLabel):
    def __init__(self, text: str = "", parent=None) -> None:
        self._full_text = text
        super().__init__(parent)
        self.setTextFormat(Qt.TextFormat.PlainText)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.setText(text)

    def setText(self, text: str) -> None:
        self._full_text = text
        self.setToolTip(text)
        self.setAccessibleName(text)
        self._refresh_text()

    def _refresh_text(self) -> None:
        visible = self.fontMetrics().elidedText(
            self._full_text, Qt.TextElideMode.ElideRight, max(0, self.contentsRect().width()))
        super().setText(visible)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh_text()

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        if event.type() in (QEvent.Type.FontChange, QEvent.Type.StyleChange):
            self._refresh_text()
