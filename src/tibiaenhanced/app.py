"""Ponto de entrada único do aplicativo."""

import sys

from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow
from .services.windowing import enable_per_monitor_dpi_awareness


def main() -> int:
    enable_per_monitor_dpi_awareness()
    app = QApplication(sys.argv)
    app.setApplicationName("Tibia Enhanced")
    app.setOrganizationName("Tibia Enhanced")

    window = MainWindow()
    window.show()
    return app.exec()
