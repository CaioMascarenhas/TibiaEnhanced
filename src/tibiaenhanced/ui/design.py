"""Fontes e ícones compartilhados pela interface."""

from functools import lru_cache
from pathlib import Path
from weakref import WeakKeyDictionary

from PySide6.QtCore import QByteArray, QEasingCurve, QEvent, QObject, QPointF, QRectF, QSize, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QFont, QFontDatabase, QIcon, QPainter, QPen, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QCheckBox, QFrame, QGraphicsDropShadowEffect,
                               QPushButton, QSlider, QStyle, QStyleOptionSlider)


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


class HoverEffects(QObject):
    """Elevação suave nos cards e nas ações principais."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._animations = WeakKeyDictionary()

    def eventFilter(self, watched, event) -> bool:
        kind = event.type()
        if kind == QEvent.Type.Polish:
            is_card = isinstance(watched, QFrame) and watched.objectName() == "timerCard"
            is_primary = isinstance(watched, QPushButton) and watched.objectName() == "primaryButton"
            if (is_card or is_primary) and watched not in self._animations:
                effect = QGraphicsDropShadowEffect(watched)
                effect.setBlurRadius(2)
                effect.setOffset(0, 0)
                effect.setColor(QColor(59, 130, 246, 0))
                watched.setGraphicsEffect(effect)
                animation = QVariantAnimation(watched)
                animation.setDuration(170)
                animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                animation.valueChanged.connect(
                    lambda value, shadow=effect: self._draw_shadow(shadow, float(value)))
                self._animations[watched] = animation
        elif watched in self._animations:
            if kind == QEvent.Type.Enter:
                self._animate(watched, 1.0)
            elif kind == QEvent.Type.Leave:
                self._animate(watched, 0.0)
            elif kind == QEvent.Type.MouseButtonPress:
                self._animate(watched, 0.35)
            elif kind == QEvent.Type.MouseButtonRelease:
                self._animate(watched, 1.0 if watched.underMouse() else 0.0)
        return False

    @staticmethod
    def _draw_shadow(effect: QGraphicsDropShadowEffect, progress: float) -> None:
        effect.setBlurRadius(2 + 18 * progress)
        effect.setOffset(0, 2 * progress)
        effect.setColor(QColor(59, 130, 246, round(72 * progress)))

    def _animate(self, watched, target: float) -> None:
        animation = self._animations[watched]
        current = float(animation.currentValue() or 0.0)
        animation.stop()
        animation.setStartValue(current)
        animation.setEndValue(target)
        animation.start()


class CompactSlider(QSlider):
    """Trilho arredondado, mantendo teclado, arraste e acessibilidade do Qt."""

    def __init__(self, orientation, parent=None, *, accent: str = "#5a9dff") -> None:
        super().__init__(orientation, parent)
        self.accent = accent
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self._hover = 0.0
        self._hover_animation = QVariantAnimation(self)
        self._hover_animation.setDuration(140)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hover_animation.valueChanged.connect(self._set_hover)

    def _set_hover(self, value: float) -> None:
        self._hover = float(value)
        self.update()

    def _animate_hover(self, target: float) -> None:
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover)
        self._hover_animation.setEndValue(target)
        self._hover_animation.start()

    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        self._animate_hover(1.0)

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        self._animate_hover(0.0)

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
        if self.isEnabled():
            accent = accent.lighter(round(100 + 14 * self._hover))
        painter.setPen(QPen(accent, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        origin = right if option.upsideDown else left
        painter.drawLine(QPointF(origin, y), QPointF(x, y))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(accent)
        radius = 5 + 1.5 * self._hover
        painter.drawEllipse(QPointF(x, y), radius, radius)
        if self.hasFocus():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(accent.lighter(140), 1))
            painter.drawEllipse(QPointF(x, y), radius + 2, radius + 2)


class ToggleCheckBox(QCheckBox):
    """Interruptor animado com interação e acessibilidade de checkbox."""

    def __init__(self, text: str, parent=None) -> None:
        super().__init__(text, parent)
        self.setObjectName("loopSwitch")
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self._position = 1.0 if self.isChecked() else 0.0
        self._pressed = False
        self._animation = QVariantAnimation(self)
        self._animation.setDuration(170)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._set_position)
        self.toggled.connect(self._animate_to_state)

    def _set_position(self, value: float) -> None:
        self._position = float(value)
        self.update()

    def _animate_to_state(self, checked: bool) -> None:
        self._animation.stop()
        target = 1.0 if checked else 0.0
        if not self.isVisible():
            self._set_position(target)
            return
        self._animation.setStartValue(self._position)
        self._animation.setEndValue(target)
        self._animation.start()

    def sizeHint(self) -> QSize:
        return QSize(46 + self.fontMetrics().horizontalAdvance(self.text()), 26)

    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        self.update()

    def mousePressEvent(self, event) -> None:
        self._pressed = True
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._pressed = False
        super().mouseReleaseEvent(event)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        track = QRectF(3, (self.height() - 20) / 2, 36, 20)
        painter.setPen(Qt.PenStyle.NoPen)
        if self.isEnabled() and (self.underMouse() or self.hasFocus()):
            painter.setBrush(QColor(59, 130, 246, 45 if self.hasFocus() else 25))
            painter.drawRoundedRect(track.adjusted(-3, -3, 3, 3), 13, 13)
        painter.setBrush(QColor("#334155" if self.isEnabled() else "#303747"))
        painter.drawRoundedRect(track, 10, 10)
        if self._position:
            active = QColor("#60a5fa" if self.underMouse() else "#3b82f6")
            active.setAlpha(round(255 * self._position) if self.isEnabled() else 60)
            painter.setBrush(active)
            painter.drawRoundedRect(track, 10, 10)
        cx = 13 + 16 * self._position
        radius = 6.4 if self._pressed else 7.2
        painter.setBrush(QColor(0, 0, 0, 50))
        painter.drawEllipse(QPointF(cx + 0.5, self.height() / 2 + 1.2), radius, radius)
        painter.setBrush(QColor("#f8fafc" if self.isEnabled() else "#94a3b8"))
        painter.drawEllipse(QPointF(cx, self.height() / 2), radius, radius)
        painter.setPen(QColor("#e2e8f0" if self.isEnabled() else "#94a3b8"))
        painter.setFont(self.font())
        painter.drawText(QRectF(46, 0, self.width() - 46, self.height()),
                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.text())
