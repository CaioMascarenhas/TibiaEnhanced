"""Ponto de entrada único do aplicativo."""

import sys
from pathlib import Path

from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow
from .ui.design import load_fonts
from .ui.theme import app_stylesheet
from .services.windowing import enable_per_monitor_dpi_awareness


def main() -> int:
    enable_per_monitor_dpi_awareness()
    app = QApplication(sys.argv)
    app.setApplicationName("Tibia Enhanced")
    app.setOrganizationName("Tibia Enhanced")
    app.setWindowIcon(QIcon(str(Path(__file__).resolve().parent / "imgs" / "iconapp_no_bg.png")))
    app.setStyle("Fusion")
    heading_family, body_family = load_fonts()
    app.setFont(QFont(body_family, 10))
    app.setStyleSheet(app_stylesheet(heading_family, body_family))

    window = MainWindow()
    window.show()
    return app.exec()
