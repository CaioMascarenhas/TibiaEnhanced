"""Ponto de entrada único do aplicativo."""

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow
from .ui.design import HoverEffects, InteractionCursors, load_fonts, ui_font
from .ui.theme_manager import theme_manager
from .services.windowing import enable_per_monitor_dpi_awareness
from .services.profiles import ProfileStore


def create_application(argv: list[str]) -> QApplication:
    enable_per_monitor_dpi_awareness()
    app = QApplication(argv)
    app.setApplicationName("Tibia Enhanced")
    app.setOrganizationName("Tibia Enhanced")
    app.setWindowIcon(QIcon(str(Path(__file__).resolve().parent / "imgs" / "iconapp_no_bg.png")))
    app.setStyle("Fusion")
    load_fonts()
    app.setFont(ui_font())
    cursors = InteractionCursors(app)
    app.installEventFilter(cursors)
    hover_effects = HoverEffects(app)
    app.installEventFilter(hover_effects)
    theme_manager().apply("dark")
    app._ui_filters = (cursors, hover_effects)
    return app


def main() -> int:
    app = create_application(sys.argv)
    profiles = ProfileStore()
    warnings = profiles.load()
    window = MainWindow(profiles, warnings)
    window.show()
    return app.exec()
