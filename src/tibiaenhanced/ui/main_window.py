"""Janela de controle e comandos da bandeja do sistema."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEvent, QPoint, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QColor, QIcon, QMouseEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSystemTrayIcon,
    QTabWidget,
    QVBoxLayout,
)

from .design import heading_font, icon
from .capture_panel import CapturePanel
from .audio_panel import AudioPanel
from .palette import ACCENT_LIGHT, BACKGROUND, BORDER
from .dialog_shell import StyledDialog
from ..services.profiles import ProfileStore
from ..models import NAME_MAX_LENGTH
from .window_selector import WindowSelector


class TitleBar(QFrame):
    def __init__(self, window: MainWindow) -> None:
        super().__init__(window)
        self.window = window
        self._drag_origin: QPoint | None = None
        self.setObjectName("titleBar")
        self.setFixedHeight(44)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 11, 5)
        layout.setSpacing(0)

        emblem = QLabel()
        emblem.setObjectName("brandIcon")
        emblem.setFixedSize(30, 30)
        emblem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        emblem.setPixmap(QPixmap(str(Path(__file__).resolve().parents[1] / "imgs" / "iconapp_no_bg.png"))
                         .scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(emblem)
        layout.addSpacing(9)
        brand = QVBoxLayout()
        brand.setSpacing(0)
        title = QLabel("Tibia Enhanced")
        title.setObjectName("brandTitle")
        title.setFont(heading_font(16))
        brand.addWidget(title)
        layout.addLayout(brand)
        layout.addStretch()

        self.profile_controls = QFrame()
        self.profile_controls.setObjectName("profileControls")
        self.profile_controls.setFixedHeight(32)
        self._profile_scale = -1.0
        profile_row = QHBoxLayout(self.profile_controls)
        profile_row.setContentsMargins(7, 2, 4, 2)
        profile_row.setSpacing(3)
        profile_label = QLabel("Perfil")
        profile_label.setObjectName("profileLabel")
        profile_label.setFixedWidth(30)
        profile_row.addWidget(profile_label)
        self.profile_combo = WindowSelector()
        self.profile_combo.setObjectName("profileSelector")
        self.profile_combo.setFixedWidth(115)
        self.profile_combo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.profile_combo.setToolTip("Perfil local de recortes e alertas")
        self.profile_combo.currentTextChanged.connect(window._switch_profile)
        profile_row.addWidget(self.profile_combo)
        divider = QFrame()
        divider.setObjectName("profileDivider")
        divider.setFixedSize(1, 16)
        profile_row.addWidget(divider)
        create_profile = QPushButton()
        create_profile.setObjectName("iconButton")
        create_profile.setFixedSize(24, 27)
        create_profile.setIcon(icon("plus", size=16))
        create_profile.setToolTip("Criar perfil")
        create_profile.setAccessibleName("Criar perfil")
        create_profile.clicked.connect(window._create_profile)
        profile_row.addWidget(create_profile)
        manage_profile = QPushButton()
        manage_profile.setObjectName("iconButton")
        manage_profile.setFixedSize(24, 27)
        manage_profile.setIcon(icon("pencil", size=15))
        manage_profile.setToolTip("Gerenciar perfil")
        manage_profile.setAccessibleName("Gerenciar perfil")
        self.profile_menu = QMenu(manage_profile)
        self._profile_actions = ((create_profile, "plus", 16), (manage_profile, "pencil", 15))
        self.profile_menu.addAction("Renomear perfil", window._rename_profile)
        self.delete_profile_action = self.profile_menu.addAction("Excluir perfil", window._delete_profile)
        manage_profile.clicked.connect(lambda: self.profile_menu.popup(
            manage_profile.mapToGlobal(QPoint(0, manage_profile.height()))))
        profile_row.addWidget(manage_profile)
        layout.addWidget(self.profile_controls)
        layout.addStretch()
        layout.addSpacing(16)
        chrome = QHBoxLayout()
        chrome.setSpacing(0)

        minimize = self._control("minus", "Minimizar")
        minimize.clicked.connect(window.showMinimized)
        chrome.addWidget(minimize)
        self.maximize_button = self._control("square", "Maximizar")
        self.maximize_button.clicked.connect(window.toggle_maximized)
        chrome.addWidget(self.maximize_button)
        close = self._control("x", "Fechar")
        close.setObjectName("chromeCloseButton")
        close.clicked.connect(window.close)
        chrome.addWidget(close)
        layout.addLayout(chrome)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        # Preserve the compact opening size, then grow within a bounded range.
        scale = min(1.0, max(0.0, (self.window.width() - 680) / 720))
        if scale == self._profile_scale:
            return
        self._profile_scale = scale
        self.profile_combo.setFixedWidth(round(115 + 165 * scale))
        self.profile_controls.setFixedHeight(round(32 + 4 * scale))
        self.setFixedHeight(round(44 + 4 * scale))
        for button, name, base_size in self._profile_actions:
            button.setFixedSize(round(24 + 6 * scale), round(27 + 4 * scale))
            size = round(base_size + 2 * scale)
            button.setIcon(icon(name, size=size))
            button.setIconSize(QSize(size, size))

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
    def __init__(self, profile_store: ProfileStore | None = None,
                 startup_warnings: list[str] | None = None) -> None:
        super().__init__()
        self._profile_store = profile_store or ProfileStore()
        self._profiles_enabled = profile_store is not None
        self._profile_loading = False
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(350)
        self._save_timer.timeout.connect(self._save_profile)
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
        self.capture_panel.changed.connect(self._schedule_save)
        self.audio_panel.changed.connect(self._schedule_save)
        self._refresh_profile_combo()
        if self._profiles_enabled:
            warnings = (startup_warnings or []) + self._load_active_profile()
            if warnings:
                QTimer.singleShot(0, lambda: self._show_profile_warnings(warnings))
        self.statusBar().setSizeGripEnabled(False)
        self.author_link = QLabel(
            'Feito por <a href="https://github.com/CaioMascarenhas" '
            f'style="color: {ACCENT_LIGHT}; text-decoration: none;">Mascarenhas</a>'
        )
        self.author_link.setObjectName("footerCredit")
        self.author_link.setOpenExternalLinks(True)
        self.author_link.setTextInteractionFlags(
            Qt.TextInteractionFlag.LinksAccessibleByMouse |
            Qt.TextInteractionFlag.LinksAccessibleByKeyboard
        )
        self.author_link.setContentsMargins(10, 3, 8, 5)
        self.statusBar().addPermanentWidget(self.author_link)

        if QSystemTrayIcon.isSystemTrayAvailable():
            self._setup_tray()

    def _refresh_profile_combo(self) -> None:
        combo = self._title_bar.profile_combo
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(self._profile_store.data["profiles"])
        combo.setCurrentText(self._profile_store.active_name)
        combo.setToolTip(f"Perfil local: {self._profile_store.active_name}")
        combo.blockSignals(False)
        self._title_bar.delete_profile_action.setEnabled(len(self._profile_store.data["profiles"]) > 1)

    def _load_active_profile(self) -> list[str]:
        self._profile_loading = True
        try:
            profile = self._profile_store.active
            warnings = self.audio_panel.load_state(profile.get("audio", {}))
            warnings.extend(self.capture_panel.load_state(profile.get("recortes", [])))
            return warnings
        finally:
            self._profile_loading = False

    def _schedule_save(self) -> None:
        if self._profiles_enabled and not self._profile_loading:
            self._save_timer.start()

    def _save_profile(self) -> bool:
        if not self._profiles_enabled or self._profile_loading:
            return True
        self._save_timer.stop()
        profile = self._profile_store.active
        profile["audio"] = self.audio_panel.export_state()
        profile["recortes"] = self.capture_panel.export_state()
        try:
            self._profile_store.save()
            return True
        except OSError as exc:
            QMessageBox.warning(self, "Perfil não salvo", f"Não foi possível salvar o perfil: {exc}")
            return False

    def _show_profile_warnings(self, warnings: list[str]) -> None:
        QMessageBox.warning(self, "Perfil restaurado com avisos", "\n".join(dict.fromkeys(warnings)))

    def _switch_profile(self, name: str) -> None:
        if (not self._profiles_enabled or not name or name == self._profile_store.active_name):
            return
        if not self._save_profile():
            self._refresh_profile_combo()
            return
        try:
            self._profile_store.select(name)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Perfil indisponível", str(exc))
            self._refresh_profile_combo()
            return
        warnings = self._load_active_profile()
        if warnings:
            self._show_profile_warnings(warnings)
        self.statusBar().showMessage(f"Perfil '{name}' ativado.", 5000)

    def _create_profile(self) -> None:
        if not self._profiles_enabled:
            return
        name = self._ask_profile_name("Novo perfil", "", "Criar perfil")
        if name is None or not self._save_profile():
            return
        try:
            self._profile_store.create(name)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Perfil não criado", str(exc))
            return
        self._refresh_profile_combo()
        self._load_active_profile()
        self.statusBar().showMessage(f"Perfil '{self._profile_store.active_name}' criado.", 5000)

    def _ask_profile_name(self, title: str, initial: str, action: str) -> str | None:
        dialog = StyledDialog(self, title)
        dialog.setMinimumWidth(330)
        field = QLineEdit(initial)
        field.setMaxLength(NAME_MAX_LENGTH)
        field.setToolTip(f"Máximo de {NAME_MAX_LENGTH} caracteres")
        field.setPlaceholderText("Nome do perfil ou personagem")
        dialog.content_layout.addWidget(field)
        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(dialog.reject)
        create = QPushButton(action)
        create.setObjectName("primaryButton")
        create.clicked.connect(dialog.accept)
        actions.addWidget(cancel)
        actions.addWidget(create)
        dialog.content_layout.addLayout(actions)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        return field.text()

    def _rename_profile(self) -> None:
        if not self._profiles_enabled:
            return
        previous = self._profile_store.active_name
        name = self._ask_profile_name("Renomear perfil", previous, "Salvar")
        if name is None or not self._save_profile():
            return
        try:
            self._profile_store.rename(previous, name)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Perfil não renomeado", str(exc))
            return
        self._refresh_profile_combo()
        self.statusBar().showMessage(f"Perfil renomeado para '{self._profile_store.active_name}'.", 5000)

    def _delete_profile(self) -> None:
        if not self._profiles_enabled or len(self._profile_store.data["profiles"]) < 2:
            return
        name = self._profile_store.active_name
        dialog = StyledDialog(self, "Excluir perfil")
        dialog.setMinimumWidth(350)
        message = QLabel(f"Excluir o perfil '{name}' e suas configurações?")
        message.setWordWrap(True)
        dialog.content_layout.addWidget(message)
        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(dialog.reject)
        delete = QPushButton("Excluir perfil")
        delete.setObjectName("dangerButton")
        delete.clicked.connect(dialog.accept)
        actions.addWidget(cancel)
        actions.addWidget(delete)
        dialog.content_layout.addLayout(actions)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._save_timer.stop()
        try:
            self._profile_store.delete(name)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Perfil não excluído", str(exc))
            return
        self._refresh_profile_combo()
        warnings = self._load_active_profile()
        if warnings:
            self._show_profile_warnings(warnings)
        self.statusBar().showMessage(f"Perfil '{name}' excluído. '{self._profile_store.active_name}' ativado.", 5000)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        inset = 0 if self.isMaximized() else 6
        radius = 0 if self.isMaximized() else 17
        rect = QRectF(self.rect()).adjusted(inset, inset, -inset, -inset)
        painter.setPen(QPen(QColor(BORDER), 1))
        painter.setBrush(QColor(BACKGROUND))
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
        if not self._save_profile():
            return
        if not self.capture_panel.shutdown():
            self.statusBar().showMessage("A captura ainda está encerrando. Tente sair novamente.")
            return
        self._exiting = True
        if self._tray is not None:
            self._tray.hide()
        self.close()
        QApplication.instance().quit()

    def _ask_close_action(self) -> str | None:
        dialog = StyledDialog(self, "Fechar Tibia Enhanced")
        dialog.setMinimumWidth(450)
        message = QLabel("Deseja encerrar o aplicativo ou mantê-lo na bandeja do sistema?")
        message.setWordWrap(True)
        dialog.content_layout.addWidget(message)
        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(dialog.reject)
        minimize = QPushButton("Minimizar para a bandeja")
        minimize.setEnabled(self._tray is not None)
        if self._tray is None:
            minimize.setToolTip("A bandeja do sistema não está disponível.")
        minimize.clicked.connect(lambda: dialog.done(2))
        close = QPushButton("Fechar aplicativo")
        close.setObjectName("primaryButton")
        close.clicked.connect(dialog.accept)
        actions.addWidget(cancel)
        actions.addWidget(minimize)
        actions.addWidget(close)
        dialog.content_layout.addLayout(actions)
        result = dialog.exec()
        if result == 2:
            return "tray"
        return "exit" if result == QDialog.DialogCode.Accepted else None

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._exiting:
            event.accept()
            return
        action = self._ask_close_action()
        if action is None or not self._save_profile():
            event.ignore()
            return
        if action == "tray":
            self.hide()
            event.ignore()
            return
        if not self.capture_panel.shutdown():
            event.ignore()
            return
        self._exiting = True
        if self._tray is not None:
            self._tray.hide()
        event.accept()
        QApplication.instance().quit()
