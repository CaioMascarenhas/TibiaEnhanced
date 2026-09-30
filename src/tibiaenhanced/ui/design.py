"""Fontes e ícones compartilhados pela interface."""

from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import QByteArray, QEvent, QObject, QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QIcon, QPainter, QPen, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QCheckBox, QSlider, QStyle, QStyleOptionSlider


ASSETS = Path(__file__).resolve().parents[1]
HEADING_FAMILY = "Exo"
BODY_FAMILY = "Inter"


def load_fonts() -> tuple[str, str]:
    """Registra as fontes distribuídas com o aplicativo."""
    global HEADING_FAMILY, BODY_FAMILY
    for filename, heading in (
        ("Exo[wght].ttf", True),
        ("Inter[opsz,wght].ttf", False),
    ):
        font_id = QFontDatabase.addApplicationFont(str(ASSETS / "fonts" / filename))
        families = QFontDatabase.applicationFontFamilies(font_id) if font_id >= 0 else []
        if heading:
            HEADING_FAMILY = families[0] if families else "Segoe UI"
        else:
            BODY_FAMILY = families[0] if families else "Segoe UI"
    return HEADING_FAMILY, BODY_FAMILY


def heading_font(size: int) -> QFont:
    font = QFont(HEADING_FAMILY, size)
    font.setWeight(QFont.Weight.Black)
    return font


@lru_cache(maxsize=128)
def icon(name: str, color: str = "#B8C9DE", size: int = 20) -> QIcon:
    """Renderiza um SVG Lucide com cor fixa para os controles Qt."""
    source = (ASSETS / "icons" / f"{name}.svg").read_text(encoding="utf-8")
    source = source.replace('stroke="currentColor"', f'stroke="{color}"')
    renderer = QSvgRenderer(QByteArray(source.encode("utf-8")))
    pixmap = QPixmap(size * 2, size * 2)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    pixmap.setDevicePixelRatio(2)
    return QIcon(pixmap)


class InteractionCursors(QObject):
    """Inclui controles criados posteriormente, como os botões dos diálogos."""

    def eventFilter(self, watched, event) -> bool:
        from PySide6.QtWidgets import QAbstractButton, QComboBox, QSlider, QTabBar
        if event.type() in (QEvent.Type.Polish, QEvent.Type.EnabledChange):
            if isinstance(watched, (QAbstractButton, QComboBox, QSlider, QTabBar)):
                watched.setCursor(Qt.CursorShape.PointingHandCursor if watched.isEnabled()
                                  else Qt.CursorShape.ArrowCursor)
        return False


class CompactSlider(QSlider):
    """Trilho arredondado, mantendo teclado, arraste e acessibilidade do Qt."""

    def __init__(self, orientation, parent=None, *, accent: str = "#5a9dff") -> None:
        super().__init__(orientation, parent)
        self.accent = accent

    def paintEvent(self, event) -> None:
        option = QStyleOptionSlider()
        self.initStyleOption(option)
        handle = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider, option,
            QStyle.SubControl.SC_SliderHandle, self)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        y = self.height() / 2
        left, right = handle.width() / 2, self.width() - handle.width() / 2
        x = handle.center().x()
        painter.setPen(QPen(QColor("#4b4e5e"), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(QPointF(left, y), QPointF(right, y))
        accent = QColor(self.accent if self.isEnabled() else "#666979")
        painter.setPen(QPen(accent, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        origin = right if option.upsideDown else left
        painter.drawLine(QPointF(origin, y), QPointF(x, y))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(accent)
        painter.drawEllipse(QPointF(x, y), 5, 5)
        if self.hasFocus():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(accent.lighter(140), 1))
            painter.drawEllipse(QPointF(x, y), 7, 7)


class ToggleCheckBox(QCheckBox):
    """Interruptor de loop que preserva clique, teclado e semântica de checkbox."""

    def sizeHint(self) -> QSize:
        return QSize(40 + self.fontMetrics().horizontalAdvance(self.text()), 24)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        track = QRectF(1, (self.height() - 16) / 2, 30, 16)
        if self.isEnabled():
            fill = QColor("#286dcc" if self.isChecked() else "#343b4d")
            outline = QColor("#7bbcff" if self.isChecked() else "#78869f")
            knob = QColor("#ffffff" if self.isChecked() else "#c6d2e3")
        else:
            fill = QColor("#303441")
            outline = QColor("#626b7e")
            knob = QColor("#8e9aac")
        painter.setPen(QPen(outline, 1))
        painter.setBrush(fill)
        painter.drawRoundedRect(track, 8, 8)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(knob)
        painter.drawEllipse(QPointF(22 if self.isChecked() else 10, self.height() / 2), 5.5, 5.5)
        if self.hasFocus():
            painter.setPen(QPen(QColor("#b9dcff"), 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(track.adjusted(-2, -2, 2, 2), 10, 10)
        painter.setPen(QColor("#f1f3f8" if self.isEnabled() else "#8e9aac"))
        painter.setFont(self.font())
        painter.drawText(QRectF(39, 0, self.width() - 39, self.height()),
                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.text())
