"""Janela de controle e comandos da bandeja do sistema."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEvent, QObject, QPoint, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QColor, QEnterEvent, QIcon, QMouseEvent, QPainter, QPainterPath, QPen, QPixmap, QRegion
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
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
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .design import ThemeSwitch, heading_font, medieval_cursor, set_icon
from .capture_panel import CapturePanel
from .audio_panel import AudioPanel
from .donate_panel import DonatePanel
from .tools_panel import ToolsPanel
from .palette import current_palette
from .theme_manager import theme_manager
from .dialog_shell import StyledDialog
from ..services.profiles import ProfileStore
from ..services.window_frame import request_rounded_corners
from ..models import NAME_MAX_LENGTH
from .window_selector import WindowSelector


class _ResizeCursorTracker(QObject):
    """Atualiza o cursor da janela mesmo quando um filho recebe o mouse."""

    def __init__(self, window) -> None:
        super().__init__(window)
        self._window = window

    def eventFilter(self, watched, event) -> bool:
        if (event.type() in (QEvent.Type.Enter, QEvent.Type.MouseMove)
                and isinstance(event, (QEnterEvent, QMouseEvent))
                and isinstance(watched, QWidget)
                and QWidget.window(watched) is self._window):
            point = self._window.mapFromGlobal(event.globalPosition().toPoint())
            self._window._update_resize_cursor(point)
        return False


class TitleBar(QFrame):
    def __init__(self, window: MainWindow) -> None:
        super().__init__(window)
        self.window = window
        self._drag_origin: QPoint | None = None
        self.setObjectName("titleBar")
        self.setFixedHeight(60)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(17, 7, 12, 7)
        layout.setSpacing(0)

        emblem = QLabel()
        emblem.setObjectName("brandIcon")
        emblem.setFixedSize(34, 34)
        emblem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        emblem.setPixmap(QPixmap(str(Path(__file__).resolve().parents[1] / "imgs" / "iconapp_no_bg.png"))
                         .scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(emblem)
        layout.addSpacing(9)
        brand = QVBoxLayout()
        brand.setSpacing(0)
        title = QLabel("Tibia Enhanced")
        title.setObjectName("brandTitle")
        title.setFont(heading_font(12))
        brand.addWidget(title)
        layout.addLayout(brand)
        layout.addStretch()

        self.profile_controls = QFrame()
        self.profile_controls.setObjectName("profileControls")
        self.profile_controls.setFixedHeight(36)
        self._profile_sizes = None
        profile_row = QHBoxLayout(self.profile_controls)
        profile_row.setContentsMargins(7, 2, 4, 2)
        profile_row.setSpacing(3)
        profile_label = QLabel("Perfil")
        profile_label.setObjectName("profileLabel")
        profile_label.setMinimumWidth(34)
        profile_row.addWidget(profile_label)
        self.profile_combo = WindowSelector()
        self.profile_combo.setObjectName("profileSelector")
        self.profile_combo.setFixedWidth(145)
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
        set_icon(create_profile, "plus", size=16)
        create_profile.setToolTip("Criar perfil")
        create_profile.setAccessibleName("Criar perfil")
        create_profile.clicked.connect(window._create_profile)
        profile_row.addWidget(create_profile)
        manage_profile = QPushButton()
        manage_profile.setObjectName("iconButton")
        manage_profile.setFixedSize(24, 27)
        set_icon(manage_profile, "pencil", size=15)
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
        # Grow the profile name without crowding the brand or window controls.
        scale = min(1.0, max(0.0, (self.window.width() - 800) / 800))
        sizes = (round(145 + 125 * scale), round(24 + 6 * scale),
                 round(27 + 4 * scale), round(2 * scale))
        if sizes == self._profile_sizes:
            return
        self._profile_sizes = sizes
        self.profile_combo.setFixedWidth(sizes[0])
        for button, name, base_size in self._profile_actions:
            button.setFixedSize(sizes[1], sizes[2])
            size = base_size + sizes[3]
            set_icon(button, name, size=size)
            button.setIconSize(QSize(size, size))

    def _control(self, name: str, tooltip: str) -> QPushButton:
        button = QPushButton()
        button.setObjectName("chromeButton")
        button.setFixedSize(34, 32)
        set_icon(button, name, size=17)
        button.setIconSize(QSize(17, 17))
        button.setToolTip(tooltip)
        return button

    def update_maximize_button(self) -> None:
        maximized = self.window.isMaximized()
        set_icon(self.maximize_button, "minimize-2" if maximized else "square", size=17)
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
        # A layered, per-pixel-alpha window can lose its backing store during
        # native Windows resize. The shell is opaque; DWM clips its corners.
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self._native_corner_handle = None
        self._native_corners = False
        self.setContentsMargins(1, 1, 1, 1)
        self.setMouseTracking(True)
        self.setWindowTitle("Tibia Enhanced")
        self.setWindowIcon(QIcon(str(Path(__file__).resolve().parents[1] / "imgs" / "iconapp_no_bg.png")))
        self.resize(940, 600)
        self.setMinimumSize(800, 500)
        self._title_bar = TitleBar(self)
        self.setMenuWidget(self._title_bar)

        workspace = QWidget()
        workspace.setObjectName("appWorkspace")
        workspace_row = QHBoxLayout(workspace)
        workspace_row.setContentsMargins(0, 0, 0, 0)
        workspace_row.setSpacing(0)
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(164)
        navigation = QVBoxLayout(sidebar)
        navigation.setContentsMargins(10, 21, 10, 18)
        navigation.setSpacing(6)
        navigation_label = QLabel("FERRAMENTAS")
        navigation_label.setObjectName("navigationLabel")
        navigation.addWidget(navigation_label)
        navigation.addSpacing(5)
        self.pages = QStackedWidget()
        self.pages.setObjectName("pages")
        self.capture_panel = CapturePanel()
        self.audio_panel = AudioPanel()
        self.tools_panel = ToolsPanel()
        self.donate_panel = DonatePanel()
        self.navigation_buttons = []
        self._navigation_group = QButtonGroup(self)
        for index, (page, name, symbol) in enumerate((
            (self.capture_panel, "Recortes", "monitor"),
            (self.audio_panel, "Alertas", "bell-ring"),
            (self.tools_panel, "Tools", "tools"),
            (self.donate_panel, "Apoiar", "heart"),
        )):
            self.pages.addWidget(page)
            button = QPushButton(name)
            button.setObjectName("navigationButton")
            button.setCheckable(True)
            set_icon(button, symbol, size=18)
            button.setIconSize(QSize(18, 18))
            button.setAccessibleName(name)
            button.clicked.connect(lambda checked=False, target=index: self.pages.setCurrentIndex(target))
            self._navigation_group.addButton(button, index)
            self.navigation_buttons.append(button)
            navigation.addWidget(button)
        navigation.addStretch()
        appearance = QFrame()
        appearance.setObjectName("appearanceControls")
        appearance_layout = QVBoxLayout(appearance)
        appearance_layout.setContentsMargins(0, 10, 0, 0)
        self.theme_switch = ThemeSwitch()
        self.theme_switch.toggled.connect(self._set_dark_theme)
        appearance_layout.addWidget(self.theme_switch, 0, Qt.AlignmentFlag.AlignLeft)
        navigation.addWidget(appearance)
        workspace_row.addWidget(sidebar)
        workspace_row.addWidget(self.pages, 1)
        self.pages.currentChanged.connect(self._update_navigation)
        self._update_navigation(0)
        self.setCentralWidget(workspace)
        self.capture_panel.changed.connect(self._schedule_save)
        self.audio_panel.changed.connect(self._schedule_save)
        self._refresh_profile_combo()
        if self._profiles_enabled:
            warnings = (startup_warnings or []) + self._load_active_profile()
            if warnings:
                QTimer.singleShot(0, lambda: self._show_profile_warnings(warnings))
        self.statusBar().setSizeGripEnabled(False)
        self.author_link = QLabel()
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
        self._cursor_tracker = _ResizeCursorTracker(self)
        QApplication.instance().installEventFilter(self._cursor_tracker)
        self._theme_manager = theme_manager()
        self._theme_manager.changed.connect(self._on_theme_changed)
        if self._profiles_enabled:
            self._theme_manager.apply(self._profile_store.data.get("theme", "dark"))
        self._refresh_theme()

    def _set_dark_theme(self, checked: bool) -> None:
        self._theme_manager.apply("dark" if checked else "light")

    def _on_theme_changed(self, mode: str) -> None:
        if self._profiles_enabled and not self._exiting:
            self._profile_store.data["theme"] = mode
            self._schedule_save()

    def _refresh_theme(self) -> None:
        colors = current_palette()
        self._update_navigation(self.pages.currentIndex())
        self.author_link.setText(
            'Feito por <a href="https://github.com/CaioMascarenhas" '
            f'style="color: {colors["ACCENT_LIGHT"]}; text-decoration: none;">Mascarenhas</a>')
        light = theme_manager().mode == "light"
        if self.theme_switch.isChecked() == light:
            self.theme_switch.blockSignals(True)
            self.theme_switch.setChecked(not light)
            self.theme_switch.blockSignals(False)
            self.theme_switch._animate_to_state(not light)
        self.theme_switch.setAccessibleName("Tema claro" if light else "Tema escuro")
        self.theme_switch.setToolTip("Ativar tema escuro" if light else "Ativar tema claro")

    def _update_navigation(self, index: int) -> None:
        for position, (button, symbol) in enumerate(zip(
                self.navigation_buttons, ("monitor", "bell-ring", "tools", "heart"))):
            selected = position == index
            button.setChecked(selected)
            set_icon(button, symbol, role="ACCENT_LIGHT" if selected else "ICON", size=18)

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
        colors = current_palette()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(colors["BACKGROUND"]))
        radius = 0 if self.isMaximized() else 12
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        painter.setPen(QPen(QColor(colors["BORDER"]), 1))
        painter.setBrush(QColor(colors["BACKGROUND"]))
        painter.drawRoundedRect(rect, radius, radius)
        super().paintEvent(event)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if QApplication.instance().platformName() == "windows":
            handle = int(self.winId())
            if handle != self._native_corner_handle:
                self._native_corner_handle = handle
                self._native_corners = request_rounded_corners(handle)
            self._update_window_shape()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_window_shape()

    def _update_window_shape(self) -> None:
        if QApplication.instance().platformName() != "windows":
            return
        if self.isMaximized() or self._native_corners:
            if not self.mask().isEmpty():
                self.clearMask()
        else:
            # Windows 10 fallback: a binary clipping region still keeps the
            # window opaque and avoids layered-window uploads while resizing.
            path = QPainterPath()
            path.addRoundedRect(QRectF(self.rect()), 12, 12)
            self.setMask(QRegion(path.toFillPolygon().toPolygon()))

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

    def _update_resize_cursor(self, point: QPoint) -> None:
        edges = self._resize_edges(point)
        if edges in (Qt.Edge.LeftEdge | Qt.Edge.TopEdge, Qt.Edge.RightEdge | Qt.Edge.BottomEdge):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edges in (Qt.Edge.RightEdge | Qt.Edge.TopEdge, Qt.Edge.LeftEdge | Qt.Edge.BottomEdge):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif edges & (Qt.Edge.LeftEdge | Qt.Edge.RightEdge):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edges & (Qt.Edge.TopEdge | Qt.Edge.BottomEdge):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.setCursor(medieval_cursor(ratio=self.devicePixelRatioF()))

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self._update_resize_cursor(event.position().toPoint())
        super().mouseMoveEvent(event)

    def leaveEvent(self, event) -> None:
        self.setCursor(medieval_cursor(ratio=self.devicePixelRatioF()))
        super().leaveEvent(event)

    def toggle_maximized(self) -> None:
        self.showNormal() if self.isMaximized() else self.showMaximized()

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.WindowStateChange:
            self.setCursor(medieval_cursor(ratio=self.devicePixelRatioF()))
            inset = 0 if self.isMaximized() else 1
            self.setContentsMargins(inset, inset, inset, inset)
            self._update_window_shape()
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
