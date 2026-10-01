"""Ponto de entrada único do aplicativo."""

import sys
from pathlib import Path

from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow
from .ui.design import HoverEffects, InteractionCursors, load_fonts
from .ui.theme import app_stylesheet
from .services.windowing import enable_per_monitor_dpi_awareness
from .services.profiles import ProfileStore


def main() -> int:
    enable_per_monitor_dpi_awareness()
    app = QApplication(sys.argv)
    app.setApplicationName("Tibia Enhanced")
    app.setOrganizationName("Tibia Enhanced")
    app.setWindowIcon(QIcon(str(Path(__file__).resolve().parent / "imgs" / "iconapp_no_bg.png")))
    app.setStyle("Fusion")
    heading_family, body_family = load_fonts()
    body_font = QFont(body_family, 9)
    body_font.setWeight(QFont.Weight.Medium)
    app.setFont(body_font)
    cursors = InteractionCursors(app)
    app.installEventFilter(cursors)
    hover_effects = HoverEffects(app)
    app.installEventFilter(hover_effects)
    app.setStyleSheet(app_stylesheet(heading_family, body_family))

    profiles = ProfileStore()
    warnings = profiles.load()
    window = MainWindow(profiles, warnings)
    window.show()
    return app.exec()
