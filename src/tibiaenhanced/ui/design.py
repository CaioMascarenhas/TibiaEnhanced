"""Fontes e ícones compartilhados pela interface."""

from functools import lru_cache
from pathlib import Path
from weakref import WeakKeyDictionary

from PySide6.QtCore import QByteArray, QEasingCurve, QEvent, QObject, QPointF, QRectF, QSize, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QCursor, QFont, QFontDatabase, QIcon, QPainter, QPen, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QCheckBox, QFrame, QGraphicsDropShadowEffect,
                               QPushButton, QSlider, QStyle, QStyleOptionSlider)

from .palette import ACCENT, ACCENT_HOVER, MUTED, TEXT, TRACK


ASSETS = Path(__file__).resolve().parents[1]
HEADING_FAMILY = "Space Grotesk"
BODY_FAMILY = "DM Sans"


def load_fonts() -> tuple[str, str]:
    """Registra as fontes distribuídas com o aplicativo."""
    global HEADING_FAMILY, BODY_FAMILY
    for filename, heading in (
        ("SpaceGrotesk[wght].ttf", True),
        ("DMSans[opsz,wght].ttf", False),
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
    font.setWeight(QFont.Weight.Bold)
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


@lru_cache(maxsize=16)
def medieval_cursor(action: bool = False, ratio: float = 1.0) -> QCursor:
    """Ponta de aço e guarda dourada; o hotspot coincide com a ponta da lâmina."""
    renderer = QSvgRenderer(str(ASSETS / "icons" /
                                ("cursor-action.svg" if action else "cursor-arrow.svg")))
    pixmap = QPixmap(round(32 * ratio), round(32 * ratio))
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    pixmap.setDevicePixelRatio(ratio)
    return QCursor(pixmap, 3, 2)


class InteractionCursors(QObject):
    """Inclui controles criados posteriormente, como os botões dos diálogos."""

    def eventFilter(self, watched, event) -> bool:
        from PySide6.QtWidgets import QAbstractButton, QComboBox, QSlider, QTabBar, QWidget
        if event.type() in (QEvent.Type.Polish, QEvent.Type.EnabledChange,
                            QEvent.Type.Enter):
            if isinstance(watched, (QAbstractButton, QComboBox, QSlider, QTabBar)):
                watched.setCursor(medieval_cursor(watched.isEnabled(), watched.devicePixelRatioF()))
            elif (isinstance(watched, QWidget) and watched.isWindow()
                  and not watched.testAttribute(Qt.WidgetAttribute.WA_SetCursor)):
                watched.setCursor(medieval_cursor(ratio=watched.devicePixelRatioF()))
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
                effect.setColor(QColor(53, 191, 169, 0))
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
        effect.setColor(QColor(53, 191, 169, round(72 * progress)))

    def _animate(self, watched, target: float) -> None:
        animation = self._animations[watched]
        current = float(animation.currentValue() or 0.0)
        animation.stop()
        animation.setStartValue(current)
        animation.setEndValue(target)
        animation.start()


class CompactSlider(QSlider):
    """Trilho arredondado, mantendo teclado, arraste e acessibilidade do Qt."""

    def __init__(self, orientation, parent=None, *, accent: str = ACCENT) -> None:
        super().__init__(orientation, parent)
        self.accent = accent
        self._drag_offset = None
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

    def _track_geometry(self):
        """Usa os mesmos limites do estilo para desenhar e interpretar o mouse."""
        option = QStyleOptionSlider()
        self.initStyleOption(option)
        horizontal = self.orientation() == Qt.Orientation.Horizontal
        centers = []
        for value in (self.minimum(), self.maximum()):
            option.sliderPosition = value
            handle = self.style().subControlRect(
                QStyle.ComplexControl.CC_Slider, option,
                QStyle.SubControl.SC_SliderHandle, self)
            centers.append(handle.center().x() if horizontal else handle.center().y())
        start, end = sorted(centers)
        position = start + QStyle.sliderPositionFromValue(
            self.minimum(), self.maximum(), self.sliderPosition(),
            end - start, option.upsideDown)
        return start, end, position, option.upsideDown

    def _move_to_pointer(self, event) -> None:
        start, end, _, upside_down = self._track_geometry()
        coordinate = (event.position().x() if self.orientation() == Qt.Orientation.Horizontal
                      else event.position().y())
        position = round(coordinate - self._drag_offset - start)
        self.setSliderPosition(QStyle.sliderValueFromPosition(
            self.minimum(), self.maximum(), position, end - start, upside_down))

    def mousePressEvent(self, event) -> None:
        if not self.isEnabled() or event.button() != Qt.MouseButton.LeftButton:
            event.ignore()
            return
        _, _, position, _ = self._track_geometry()
        coordinate = (event.position().x() if self.orientation() == Qt.Orientation.Horizontal
                      else event.position().y())
        # Segurar a borda do indicador não deve deslocar o valor ao iniciar o arraste.
        self._drag_offset = coordinate - position if abs(coordinate - position) <= 7 else 0
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        self.setSliderDown(True)
        self._move_to_pointer(event)
        event.accept()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_offset is None:
            super().mouseMoveEvent(event)
            return
        self._move_to_pointer(event)
        event.accept()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() != Qt.MouseButton.LeftButton or self._drag_offset is None:
            super().mouseReleaseEvent(event)
            return
        self._move_to_pointer(event)
        self._drag_offset = None
        self.setSliderDown(False)
        if self.value() != self.sliderPosition():
            self.triggerAction(QSlider.SliderAction.SliderMove)
        event.accept()

    def paintEvent(self, event) -> None:
        start, end, position, upside_down = self._track_geometry()
        horizontal = self.orientation() == Qt.Orientation.Horizontal
        def point(coordinate):
            return (QPointF(coordinate, self.height() / 2) if horizontal
                    else QPointF(self.width() / 2, coordinate))
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(TRACK), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(point(start), point(end))
        accent = QColor(self.accent if self.isEnabled() else "#666979")
        if self.isEnabled():
            accent = accent.lighter(round(100 + 14 * self._hover))
        painter.setPen(QPen(accent, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        origin = end if upside_down else start
        painter.drawLine(point(origin), point(position))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(accent)
        radius = 5 + 1.5 * self._hover
        painter.drawEllipse(point(position), radius, radius)
        if self.hasFocus():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(accent.lighter(140), 1))
            painter.drawEllipse(point(position), radius + 2, radius + 2)


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
            painter.setBrush(QColor(53, 191, 169, 45 if self.hasFocus() else 25))
            painter.drawRoundedRect(track.adjusted(-3, -3, 3, 3), 13, 13)
        painter.setBrush(QColor(TRACK if self.isEnabled() else "#354044"))
        painter.drawRoundedRect(track, 10, 10)
        if self._position:
            active = QColor(ACCENT_HOVER if self.underMouse() else ACCENT)
            active.setAlpha(round(255 * self._position) if self.isEnabled() else 60)
            painter.setBrush(active)
            painter.drawRoundedRect(track, 10, 10)
        cx = 13 + 16 * self._position
        radius = 6.4 if self._pressed else 7.2
        painter.setBrush(QColor(0, 0, 0, 50))
        painter.drawEllipse(QPointF(cx + 0.5, self.height() / 2 + 1.2), radius, radius)
        painter.setBrush(QColor(TEXT if self.isEnabled() else "#899a98"))
        painter.drawEllipse(QPointF(cx, self.height() / 2), radius, radius)
        painter.setPen(QColor(MUTED if self.isEnabled() else "#899a98"))
        painter.setFont(self.font())
        painter.drawText(QRectF(46, 0, self.width() - 46, self.height()),
                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.text())
