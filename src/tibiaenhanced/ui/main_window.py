"""Janela de controle e comandos da bandeja do sistema."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QStyle,
    QSystemTrayIcon,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._exiting = False
        self._tray: QSystemTrayIcon | None = None
        self.setWindowTitle("Tibia Enhanced")
        self.resize(760, 500)

        tabs = QTabWidget()
        tabs.addTab(
            self._placeholder(
                "Recortes",
                "Seleção e espelhamento de regiões serão implementados nas issues #2 e #3.",
            ),
            "Recortes",
        )
        tabs.addTab(
            self._placeholder(
                "Alertas",
                "Temporizadores e sons personalizados serão implementados na issue #4.",
            ),
            "Alertas",
        )
        self.setCentralWidget(tabs)
        self.statusBar().showMessage("Pronto para configurar")

        if QSystemTrayIcon.isSystemTrayAvailable():
            self._setup_tray()

    @staticmethod
    def _placeholder(title: str, description: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        heading = QLabel(title)
        heading.setStyleSheet("font-size: 20px; font-weight: 600;")
        message = QLabel(description)
        message.setWordWrap(True)
        layout.addWidget(heading)
        layout.addWidget(message)
        layout.addStretch()
        return page

    def _setup_tray(self) -> None:
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.setWindowIcon(icon)
        self._tray = QSystemTrayIcon(icon, self)
        self._tray.setToolTip("Tibia Enhanced")

        menu = QMenu(self)
        show_action = QAction("Mostrar", self)
        show_action.triggered.connect(self.show_window)
        hide_action = QAction("Ocultar", self)
        hide_action.triggered.connect(self.hide)
        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.exit_app)
        menu.addAction(show_action)
        menu.addAction(hide_action)
        menu.addSeparator()
        menu.addAction(exit_action)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()
        QApplication.instance().setQuitOnLastWindowClosed(False)

    def show_window(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.show_window()

    def exit_app(self) -> None:
        self._exiting = True
        if self._tray is not None:
            self._tray.hide()
        self.close()
        QApplication.instance().quit()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._tray is not None and not self._exiting:
            self.hide()
            event.ignore()
        else:
            event.accept()
