"""Janela de controle e comandos da bandeja do sistema."""

from pathlib import Path

from PySide6.QtGui import QAction, QCloseEvent, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenu,
    QStyle,
    QSystemTrayIcon,
    QTabWidget,
)

from .capture_panel import CapturePanel
from .audio_panel import AudioPanel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._exiting = False
        self._tray: QSystemTrayIcon | None = None
        self.setWindowTitle("Tibia Enhanced")
        self.setWindowIcon(QIcon(str(Path(__file__).resolve().parents[1] / "imgs" / "iconapp_no_bg.png")))
        self.resize(1100, 820)
        self.setMinimumSize(880, 720)

        tabs = QTabWidget()
        self.capture_panel = CapturePanel()
        tabs.addTab(self.capture_panel,
                    self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon),
                    "Recortes")
        self.audio_panel = AudioPanel()
        tabs.addTab(
            self.audio_panel,
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume),
            "Alertas",
        )
        self.setCentralWidget(tabs)
        self.statusBar().showMessage("Pronto para configurar")

        if QSystemTrayIcon.isSystemTrayAvailable():
            self._setup_tray()

    def _setup_tray(self) -> None:
        icon = self.windowIcon()
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
        if not self.capture_panel.shutdown():
            self.statusBar().showMessage("A captura ainda está encerrando. Tente sair novamente.")
            return
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
            self.capture_panel.shutdown()
            event.accept()
