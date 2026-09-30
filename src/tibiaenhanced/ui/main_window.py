"""Janela de controle e comandos da bandeja do sistema."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEvent, QPoint, QRectF, QSize, Qt
from PySide6.QtGui import QAction, QCloseEvent, QColor, QIcon, QMouseEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QSystemTrayIcon,
    QTabWidget,
    QVBoxLayout,
)

from .design import heading_font, icon
from .capture_panel import CapturePanel
from .audio_panel import AudioPanel


class TitleBar(QFrame):
    def __init__(self, window: MainWindow) -> None:
        super().__init__(window)
        self.window = window
        self._drag_origin: QPoint | None = None
        self.setObjectName("titleBar")
        self.setFixedHeight(44)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 11, 5)
        layout.setSpacing(9)

        emblem = QLabel()
        emblem.setObjectName("brandIcon")
        emblem.setFixedSize(30, 30)
        emblem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        emblem.setPixmap(QPixmap(str(Path(__file__).resolve().parents[1] / "imgs" / "iconapp_no_bg.png"))
                         .scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(emblem)
        brand = QVBoxLayout()
        brand.setSpacing(0)
        title = QLabel("Tibia Enhanced")
        title.setObjectName("brandTitle")
        title.setFont(heading_font(16))
        brand.addWidget(title)
        layout.addLayout(brand)
        layout.addStretch()

        minimize = self._control("minus", "Minimizar")
        minimize.clicked.connect(window.showMinimized)
        layout.addWidget(minimize)
        self.maximize_button = self._control("square", "Maximizar")
        self.maximize_button.clicked.connect(window.toggle_maximized)
        layout.addWidget(self.maximize_button)
        close = self._control("x", "Fechar")
        close.setObjectName("chromeCloseButton")
        close.clicked.connect(window.close)
        layout.addWidget(close)

    def _control(self, name: str, tooltip: str) -> QPushButton:
        button = QPushButton()
        button.setObjectName("chromeButton")
        button.setFixedSize(34, 32)
        button.setIcon(icon(name, "#c8d7e7", 17))
        button.setIconSize(QSize(17, 17))
        button.setToolTip(tooltip)
        return button

    def update_maximize_button(self) -> None:
        maximized = self.window.isMaximized()
        self.maximize_button.setIcon(icon("minimize-2" if maximized else "square", "#c8d7e7", 17))
        self.maximize_button.setToolTip("Restaurar" if maximized else "Maximizar")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and not self.window.isMaximized():
            handle = self.window.windowHandle()
            if handle is None or not handle.startSystemMove():
                self._drag_origin = event.globalPosition().toPoint() - self.window.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_origin is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.window.move(event.globalPosition().toPoint() - self._drag_origin)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_origin = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.window.toggle_maximized()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._exiting = False
        self._tray: QSystemTrayIcon | None = None
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setContentsMargins(7, 7, 7, 7)
        self.setMouseTracking(True)
        self.setWindowTitle("Tibia Enhanced")
        self.setWindowIcon(QIcon(str(Path(__file__).resolve().parents[1] / "imgs" / "iconapp_no_bg.png")))
        self.resize(680, 460)
        self.setMinimumSize(560, 380)
        self._title_bar = TitleBar(self)
        self.setMenuWidget(self._title_bar)

        tabs = QTabWidget()
        tabs.tabBar().setIconSize(QSize(16, 16))
        self.capture_panel = CapturePanel()
        tabs.addTab(self.capture_panel,
                    icon("monitor", "#d5e6f5", 16),
                    "Recortes")
        self.audio_panel = AudioPanel()
        tabs.addTab(
            self.audio_panel,
            icon("bell-ring", "#d5e6f5", 16),
            "Alertas",
        )
        self.setCentralWidget(tabs)
        self.statusBar().setSizeGripEnabled(False)
        self.author_link = QLabel(
            'Feito por <a href="https://github.com/CaioMascarenhas" '
            'style="color: #ff9b31; text-decoration: none;">Mascarenhas</a>'
        )
        self.author_link.setObjectName("footerCredit")
        self.author_link.setOpenExternalLinks(True)
        self.author_link.setTextInteractionFlags(
            Qt.TextInteractionFlag.LinksAccessibleByMouse |
            Qt.TextInteractionFlag.LinksAccessibleByKeyboard
        )
        self.author_link.setContentsMargins(10, 3, 8, 5)
        self.statusBar().addWidget(self.author_link)

        if QSystemTrayIcon.isSystemTrayAvailable():
            self._setup_tray()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        inset = 0 if self.isMaximized() else 6
        radius = 0 if self.isMaximized() else 17
        rect = QRectF(self.rect()).adjusted(inset, inset, -inset, -inset)
        painter.setPen(QPen(QColor("#34363e"), 1))
        painter.setBrush(QColor("#1b1e24"))
        painter.drawRoundedRect(rect, radius, radius)
        super().paintEvent(event)

    def _resize_edges(self, point: QPoint) -> Qt.Edges:
        if self.isMaximized():
            return Qt.Edges()
        edges = Qt.Edges()
        border = 9
        if point.x() < border:
            edges |= Qt.Edge.LeftEdge
        elif point.x() >= self.width() - border:
            edges |= Qt.Edge.RightEdge
        if point.y() < border:
            edges |= Qt.Edge.TopEdge
        elif point.y() >= self.height() - border:
            edges |= Qt.Edge.BottomEdge
        return edges

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            edges = self._resize_edges(event.position().toPoint())
            handle = self.windowHandle()
            if edges and handle is not None and handle.startSystemResize(edges):
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        edges = self._resize_edges(event.position().toPoint())
        if edges in (Qt.Edge.LeftEdge | Qt.Edge.TopEdge, Qt.Edge.RightEdge | Qt.Edge.BottomEdge):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edges in (Qt.Edge.RightEdge | Qt.Edge.TopEdge, Qt.Edge.LeftEdge | Qt.Edge.BottomEdge):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif edges & (Qt.Edge.LeftEdge | Qt.Edge.RightEdge):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edges & (Qt.Edge.TopEdge | Qt.Edge.BottomEdge):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.unsetCursor()
        super().mouseMoveEvent(event)

    def toggle_maximized(self) -> None:
        self.showNormal() if self.isMaximized() else self.showMaximized()

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.WindowStateChange:
            inset = 0 if self.isMaximized() else 7
            self.setContentsMargins(inset, inset, inset, inset)
            if hasattr(self, "_title_bar"):
                self._title_bar.update_maximize_button()
            self.update()
        super().changeEvent(event)

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
