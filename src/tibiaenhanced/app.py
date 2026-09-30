"""Ponto de entrada único do aplicativo."""

import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow
from .ui.theme import APP_STYLESHEET
from .services.windowing import enable_per_monitor_dpi_awareness


def main() -> int:
    enable_per_monitor_dpi_awareness()
    app = QApplication(sys.argv)
    app.setApplicationName("Tibia Enhanced")
    app.setOrganizationName("Tibia Enhanced")
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(APP_STYLESHEET)

    window = MainWindow()
    window.show()
    return app.exec()
