"""Janela de controle e comandos da bandeja do sistema."""

from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QStyle,
    QSystemTrayIcon,
    QTabWidget,
    QFrame,
    QVBoxLayout,
    QWidget,
)

from .capture_panel import CapturePanel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._exiting = False
        self._tray: QSystemTrayIcon | None = None
        self.setWindowTitle("Tibia Enhanced")
        self.resize(1100, 820)
        self.setMinimumSize(880, 720)

        tabs = QTabWidget()
        self.capture_panel = CapturePanel()
        tabs.addTab(self.capture_panel,
                    self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon),
                    "Recortes")
        tabs.addTab(
            self._placeholder(
                "Alertas",
                "Em breve: temporizadores iniciados por você e sons personalizados. "
                "Esta área será implementada na issue #4.",
            ),
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume),
            "Alertas",
        )
        self.setCentralWidget(tabs)
        self.statusBar().showMessage("Pronto para configurar")

        if QSystemTrayIcon.isSystemTrayAvailable():
            self._setup_tray()

    @staticmethod
    def _placeholder(title: str, description: str) -> QWidget:
        page = QWidget()
        page.setObjectName("placeholderPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        intro = QLabel("Controle o que precisa lembrar, sem automatizar ações no jogo.")
        intro.setObjectName("mutedText")
        layout.addWidget(heading)
        layout.addWidget(intro)
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_title = QLabel("Alertas de áudio")
        card_title.setObjectName("sectionTitle")
        message = QLabel(description)
        message.setWordWrap(True)
        message.setObjectName("mutedText")
        card_layout.addWidget(card_title)
        card_layout.addWidget(message)
        layout.addWidget(card)
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
