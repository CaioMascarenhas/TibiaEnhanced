"""Fontes e ícones compartilhados pela interface."""

from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QFont, QFontDatabase, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


ASSETS = Path(__file__).resolve().parents[1]
HEADING_FAMILY = "Exo"
BODY_FAMILY = "Quicksand"


def load_fonts() -> tuple[str, str]:
    """Registra as fontes distribuídas com o aplicativo."""
    global HEADING_FAMILY, BODY_FAMILY
    for filename, heading in (
        ("Exo[wght].ttf", True),
        ("Quicksand[wght].ttf", False),
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
