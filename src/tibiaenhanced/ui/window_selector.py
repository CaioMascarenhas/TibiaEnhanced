"""Seletor de janela com largura controlada e títulos completos em tooltip."""

from PySide6.QtCore import QPoint, QSize, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (QApplication, QComboBox, QLabel, QListView,
                               QSizePolicy, QStyle, QStyledItemDelegate,
                               QStyleOptionComboBox, QStyleOptionViewItem,
                               QStylePainter)

from .design import icon
from .palette import MUTED


class _WindowItemDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index) -> QSize:
        return QSize(0, max(27, super().sizeHint(option, index).height()))

    def paint(self, painter: QPainter, option, index) -> None:
        visual = QStyleOptionViewItem(option)
        self.initStyleOption(visual, index)
        visual.text = visual.fontMetrics.elidedText(
            visual.text, Qt.TextElideMode.ElideRight, max(30, visual.rect.width() - 16))
        super().paint(painter, visual, index)


class WindowSelector(QComboBox):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("windowSelector")
        self.setPlaceholderText("Selecione a janela do jogo")
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.setMinimumContentsLength(0)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        view = QListView(self)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setItemDelegate(_WindowItemDelegate(view))
        self.setView(view)
        self._arrow = QLabel(self)
        self._arrow.setFixedSize(16, 16)
        self._arrow.setPixmap(icon("chevron-down", MUTED, 16).pixmap(16, 16))
        self._arrow.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.currentIndexChanged.connect(self._update_tooltip)

    def _update_tooltip(self) -> None:
        self.setToolTip(self.currentText() or "Escolha a janela que será espelhada")

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._arrow.move(self.width() - 25, (self.height() - 16) // 2)

    def paintEvent(self, event) -> None:
        painter = QStylePainter(self)
        option = QStyleOptionComboBox()
        self.initStyleOption(option)
        option.currentText = self.fontMetrics().elidedText(
            self.currentText() or self.placeholderText(),
            Qt.TextElideMode.ElideRight, max(30, self.width() - 48))
        painter.drawComplexControl(QStyle.ComplexControl.CC_ComboBox, option)
        painter.drawControl(QStyle.ControlElement.CE_ComboBoxLabel, option)

    def showPopup(self) -> None:
        super().showPopup()
        popup = self.view().window()
        screen = QApplication.screenAt(self.mapToGlobal(QPoint(0, 0))) or QApplication.primaryScreen()
        left = self.mapToGlobal(QPoint(0, 0)).x()
        if screen is not None:
            bounds = screen.availableGeometry()
            left = max(bounds.left(), min(left, bounds.right() - self.width() + 1))
        popup.setFixedWidth(self.width())
        popup.move(left, popup.y())
