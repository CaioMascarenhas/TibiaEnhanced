"""Ponto de entrada único do aplicativo."""

import os
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow
from .ui.design import HoverEffects, InteractionCursors, load_fonts, ui_font
from .ui.theme import app_stylesheet
from .services.windowing import enable_per_monitor_dpi_awareness
from .services.profiles import ProfileStore


def create_application(argv: list[str]) -> QApplication:
    enable_per_monitor_dpi_awareness()
    if sys.platform == "win32":
        # The native font engine can ignore NoSubpixelAntialias. FreeType
        # honors it without changing the user's Windows ClearType settings.
        os.environ.setdefault("QT_QPA_PLATFORM", "windows:fontengine=freetype")
    app = QApplication(argv)
    app.setApplicationName("Tibia Enhanced")
    app.setOrganizationName("Tibia Enhanced")
    app.setWindowIcon(QIcon(str(Path(__file__).resolve().parent / "imgs" / "iconapp_no_bg.png")))
    app.setStyle("Fusion")
    heading_family, body_family = load_fonts()
    app.setFont(ui_font())
    cursors = InteractionCursors(app)
    app.installEventFilter(cursors)
    hover_effects = HoverEffects(app)
    app.installEventFilter(hover_effects)
    app.setStyleSheet(app_stylesheet(heading_family, body_family))
    app._ui_filters = (cursors, hover_effects)
    return app


def main() -> int:
    app = create_application(sys.argv)
    profiles = ProfileStore()
    warnings = profiles.load()
    window = MainWindow(profiles, warnings)
    window.show()
    return app.exec()
