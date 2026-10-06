"""Painel de janelas de origem e seus espelhos DWM."""

from dataclasses import dataclass

from PySide6.QtCore import QEvent, QSize, Qt, QTimer, Signal
from .card_grid import arrange_cards
from PySide6.QtWidgets import (QDialog, QFrame, QGridLayout, QHBoxLayout,
                               QLabel, QLineEdit, QMessageBox,
                               QPushButton, QScrollArea,
                               QSizePolicy, QVBoxLayout, QWidget)

from tibiaenhanced.models import NAME_MAX_LENGTH, Region
from tibiaenhanced.services.windowing import get_client_area, list_windows
from .dwm_windows import DwmMirrorWindow, DwmRegionDialog
from .design import set_icon
from .design import CompactSlider as QSlider
from .dialog_shell import StyledDialog
from .elided_label import ElidedLabel
from .palette import current_palette
from .window_selector import WindowSelector


class _StatusLabel(QLabel):
    def setText(self, text: str) -> None:
        super().setText(text)
        self.setVisible(bool(text))


@dataclass(slots=True)
class MirrorEntry:
    key: int
    source_hwnd: int
    source_title: str
    region: Region
    window: DwmMirrorWindow
    visible: bool = False
    locked: bool = False
    fit_mode: str = "stretch"
    transparency_percent: int = 0
    source_executable: str = ""
    source_class: str = ""
    recovering: bool = False


class CapturePanel(QWidget):
    changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._loading = False
        self._pending_mirrors: list[dict] = []
        self.setObjectName("appPage")
        self._entries: dict[int, MirrorEntry] = {}
        self._selected_key = None
        self._cards = {}
        self._next_key = 1
        self._shutting_down = False
        self._recovery_timer = QTimer(self)
        self._recovery_timer.setInterval(1000)
        self._recovery_timer.timeout.connect(self._poll_sources)
        self._build_ui()
        self.refresh_windows()
        self._update_controls()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        heading = QHBoxLayout()
        heading.setSpacing(16)
        heading_text = QVBoxLayout()
        heading_text.setSpacing(5)
        title = QLabel("Recortes")
        title.setObjectName("pageTitle")
        heading_text.addWidget(title)
        description = QLabel("Mantenha as partes do jogo que você precisa sempre à vista.")
        description.setObjectName("pageDescription")
        description.setWordWrap(True)
        heading_text.addWidget(description)
        heading.addLayout(heading_text, 1)
        self.add_button = QPushButton("Novo recorte")
        self.add_button.setObjectName("primaryButton")
        set_icon(self.add_button, "plus", role="PRIMARY_TEXT", size=16)
        self.add_button.setIconSize(QSize(16, 16))
        self.add_button.setToolTip("Escolher uma área e criar um espelho")
        self.add_button.clicked.connect(self.add_mirror)
        heading.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(heading)

        source_toolbar = QFrame()
        source_toolbar.setObjectName("toolbar")
        source_layout = QVBoxLayout(source_toolbar)
        source_layout.setContentsMargins(14, 12, 14, 12)
        source_layout.setSpacing(8)
        source_heading = QLabel("Janela de origem")
        source_heading.setObjectName("eyebrow")
        source_layout.addWidget(source_heading)
        source_row = QHBoxLayout()
        source_row.setSpacing(8)
        self.window_combo = WindowSelector()
        source_row.addWidget(self.window_combo, 1)
        refresh_button = QPushButton()
        refresh_button.setFixedWidth(38)
        set_icon(refresh_button, "refresh-cw", size=16)
        refresh_button.setIconSize(QSize(16, 16))
        refresh_button.setToolTip("Atualizar a lista de janelas abertas")
        refresh_button.clicked.connect(self.refresh_windows)
        source_row.addWidget(refresh_button)
        self.bind_button = QPushButton("Vincular")
        self.bind_button.setToolTip("Associar um recorte salvo à janela selecionada")
        self.bind_button.clicked.connect(self._bind_pending)
        self.bind_button.hide()
        source_row.addWidget(self.bind_button)
        source_layout.addLayout(source_row)
        layout.addWidget(source_toolbar)
        self.count_label = QLabel("Nenhum recorte criado")
        self.count_label.setObjectName("mutedText")
        self.count_label.hide()
        layout.addWidget(self.count_label)
        scroll = QScrollArea()
        scroll.setObjectName("detailsScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.card_scroll = scroll
        scroll.viewport().installEventFilter(self)
        container = QWidget()
        container.setObjectName("appPage")
        self.card_grid = QGridLayout(container)
        self.card_grid.setContentsMargins(0, 0, 6, 0)
        self.card_grid.setSpacing(12)
        self.empty_state = QFrame()
        self.empty_state.setObjectName("emptyState")
        self.empty_state.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        empty = QVBoxLayout(self.empty_state)
        empty.setContentsMargins(24, 24, 24, 24)
        empty.setSpacing(12)
        empty.addStretch()
        empty_icon = QLabel()
        empty_icon.setObjectName("emptyIcon")
        empty_icon.setFixedSize(56, 56)
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        set_icon(empty_icon, "monitor", role="MUTED", size=36)
        empty.addWidget(empty_icon, alignment=Qt.AlignmentFlag.AlignHCenter)
        empty_title = QLabel("Seu primeiro recorte começa aqui")
        empty_title.setObjectName("emptyTitle")
        empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_title.setWordWrap(True)
        empty.addWidget(empty_title)
        self.empty_label = QLabel("Selecione uma janela acima e clique em Novo recorte.\nVocê escolhe a área que quer acompanhar.")
        self.empty_label.setObjectName("pageDescription")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setWordWrap(True)
        empty.addWidget(self.empty_label)
        empty.addStretch()
        self.card_grid.addWidget(self.empty_state, 0, 0)
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        self.details_dialog = StyledDialog(self, "Configurar recorte")
        self.details_dialog.setMinimumWidth(390)
        dialog_layout = self.details_dialog.content_layout
        detail_card = QFrame()
        detail_card.setObjectName("dialogBody")
        detail_layout = QVBoxLayout(detail_card)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        detail_layout.setSpacing(9)
        self.selected_name = ElidedLabel("Selecione um recorte na lista")
        self.selected_name.setObjectName("selectedTitle")
        detail_layout.addWidget(self.selected_name)
        self.selected_source = ElidedLabel("A origem e os controles aparecerão aqui.")
        self.selected_source.setObjectName("mutedText")
        detail_layout.addWidget(self.selected_source)
        self.selected_coordinates = QLabel("")
        self.selected_coordinates.setObjectName("mutedText")
        detail_layout.addWidget(self.selected_coordinates)
        self.state_label = QLabel("SEM SELEÇÃO")
        self.state_label.setObjectName("stateBadge")
        detail_layout.addWidget(self.state_label)

        actions = QGridLayout()
        actions.setHorizontalSpacing(8)
        actions.setVerticalSpacing(8)
        self.show_button = QPushButton("Mostrar espelho")
        self.show_button.clicked.connect(self.toggle_visibility)
        actions.addWidget(self.show_button, 0, 0)
        self.lock_button = QPushButton("Bloquear cliques")
        set_icon(self.lock_button, "lock-keyhole", size=16)
        self.lock_button.clicked.connect(self.toggle_lock)
        actions.addWidget(self.lock_button, 0, 1)
        self.rename_button = QPushButton("Renomear")
        set_icon(self.rename_button, "pencil", size=16)
        self.rename_button.clicked.connect(self.rename_current)
        actions.addWidget(self.rename_button, 1, 0)
        self.delete_button = QPushButton("Excluir recorte")
        self.delete_button.setObjectName("dangerButton")
        set_icon(self.delete_button, "trash", role="DANGER_TEXT", size=16)
        self.delete_button.clicked.connect(self.delete_current)
        actions.addWidget(self.delete_button, 1, 1)
        detail_layout.addLayout(actions)

        display_heading = QLabel("APARÊNCIA")
        display_heading.setObjectName("eyebrow")
        detail_layout.addWidget(display_heading)
        fit_row = QHBoxLayout()
        fit_row.addWidget(QLabel("Ajuste"))
        self.fit_combo = WindowSelector()
        self.fit_combo.setPlaceholderText("Ajuste da imagem")
        self.fit_combo.addItem("Preservar proporção", "contain")
        self.fit_combo.addItem("Preencher janela", "stretch")
        self.fit_combo.setCurrentIndex(0)
        self.fit_combo.currentIndexChanged.connect(self._change_fit_mode)
        fit_row.addWidget(self.fit_combo, 1)
        detail_layout.addLayout(fit_row)
        self.transparency_label = QLabel("Transparência  0%")
        detail_layout.addWidget(self.transparency_label)
        self.transparency_slider = QSlider(Qt.Orientation.Horizontal)
        self.transparency_slider.setRange(0, 90)
        self.transparency_slider.setSingleStep(5)
        self.transparency_slider.setPageStep(10)
        self.transparency_slider.setTickInterval(10)
        self.transparency_slider.valueChanged.connect(self._change_transparency)
        detail_layout.addWidget(self.transparency_slider)
        hint = QLabel("Arraste a imagem para mover. Use as bordas para redimensionar. "
                      "Bloqueado, o espelho deixa os cliques passarem; desbloqueie aqui.")
        hint.setObjectName("mutedText")
        hint.setWordWrap(True)
        detail_layout.addWidget(hint)
        detail_layout.addStretch()
        dialog_layout.addWidget(detail_card)
        done = QPushButton("Concluir")
        done.setObjectName("primaryButton")
        done.clicked.connect(self.details_dialog.accept)
        dialog_layout.addWidget(done)

        self.status_label = _StatusLabel()
        self.status_label.setObjectName("statusText")
        self.status_label.setWordWrap(True)
        self.status_label.hide()
        layout.addWidget(self.status_label)
        self.window_combo.currentIndexChanged.connect(self._update_controls)

    @property
    def entries(self) -> tuple[MirrorEntry, ...]:
        return tuple(self._entries.values())

    def refresh_windows(self) -> None:
        previous = self.window_combo.currentData()
        try:
            windows = list_windows()
        except Exception as exc:
            self.status_label.setText(f"Não foi possível listar as janelas: {exc}")
            return
        self.window_combo.blockSignals(True)
        self.window_combo.clear()
        for window in windows:
            self.window_combo.addItem(window.title, window.hwnd)
            self.window_combo.setItemData(self.window_combo.count() - 1, window.title,
                                          Qt.ItemDataRole.ToolTipRole)
            self.window_combo.setItemData(self.window_combo.count() - 1,
                                          getattr(window, "executable", ""), Qt.ItemDataRole.UserRole + 1)
            self.window_combo.setItemData(self.window_combo.count() - 1,
                                          getattr(window, "window_class", ""), Qt.ItemDataRole.UserRole + 2)
        if previous is not None:
            index = self.window_combo.findData(previous)
            if index >= 0:
                self.window_combo.setCurrentIndex(index)
            else:
                self.window_combo.setCurrentIndex(-1)
        else:
            self.window_combo.setCurrentIndex(-1)
        self.window_combo.blockSignals(False)
        self.window_combo._update_tooltip()
        self._update_controls()
        if self._pending_mirrors:
            self._restore_pending()
        self._resume_waiting()

    def _poll_sources(self) -> None:
        if not self._shutting_down:
            self.refresh_windows()

    def _update_recovery_timer(self) -> None:
        needed = self._pending_mirrors or any(entry.recovering for entry in self._entries.values())
        if needed and not self._shutting_down:
            self._recovery_timer.start()
        else:
            self._recovery_timer.stop()

    def _source_match(self, title: str, executable: str, window_class: str,
                      preferred_hwnd: int | None = None) -> int | None:
        candidates = [index for index in range(self.window_combo.count())
                      if (not window_class or self.window_combo.itemData(
                          index, Qt.ItemDataRole.UserRole + 2) == window_class)
                      and (self.window_combo.itemData(index, Qt.ItemDataRole.UserRole + 1) == executable
                           if executable else self.window_combo.itemText(index) == title)]
        preferred = [index for index in candidates
                     if self.window_combo.itemData(index) == preferred_hwnd]
        if len(preferred) == 1:
            return preferred[0]
        exact = [index for index in candidates if self.window_combo.itemText(index) == title]
        if len(exact) == 1:
            return exact[0]
        return candidates[0] if len(candidates) == 1 else None

    def _try_resume_entry(self, entry: MirrorEntry, match_override: int | None = None) -> bool:
        match = match_override if match_override is not None else self._source_match(
            entry.source_title, entry.source_executable, entry.source_class, entry.source_hwnd)
        if match is None:
            return False
        hwnd = self.window_combo.itemData(match)
        try:
            area = get_client_area(hwnd)
            if (entry.region.x + entry.region.width > area.width or
                    entry.region.y + entry.region.height > area.height):
                return False
            entry.window.rebind_source(hwnd)
        except RuntimeError:
            return False
        entry.source_hwnd = hwnd
        entry.source_title = self.window_combo.itemText(match)
        entry.source_executable = self.window_combo.itemData(match, Qt.ItemDataRole.UserRole + 1) or ""
        entry.source_class = self.window_combo.itemData(match, Qt.ItemDataRole.UserRole + 2) or ""
        entry.recovering = False
        entry.visible = True
        entry.window.show()
        return True

    def _resume_waiting(self) -> None:
        resumed = False
        for entry in self._entries.values():
            if entry.recovering and self._try_resume_entry(entry):
                resumed = True
                self.status_label.setText(f"{entry.region.name}: espelho recuperado.")
        if resumed:
            self._refresh_cards()
            self._changed()
        self._update_recovery_timer()

    def add_mirror(self) -> None:
        hwnd = self.window_combo.currentData()
        if hwnd is None:
            return
        source_title = self.window_combo.currentText()
        try:
            dialog = DwmRegionDialog(hwnd, self,
                                     suggested_name=f"Recorte {self._next_key}",
                                     source_title=source_title)
        except RuntimeError as exc:
            QMessageBox.warning(self, "Espelho indisponível", str(exc))
            return
        if dialog.exec() != DwmRegionDialog.DialogCode.Accepted:
            return
        rect = dialog.selection
        region = Region(dialog.name, rect.x(), rect.y(), rect.width(), rect.height())
        key = self._next_key
        self._next_key += 1
        mirror = DwmMirrorWindow(hwnd, region)
        mirror.stopped.connect(lambda message, mirror_key=key:
                               self._on_mirror_stopped(mirror_key, message))
        mirror.action_requested.connect(lambda action, mirror_key=key:
                                        self._mirror_action(mirror_key, action))
        mirror.geometry_changed.connect(self._changed)
        mirror.opacity_requested.connect(lambda value, mirror_key=key:
                                          self._mirror_opacity(mirror_key, value))
        mirror.fit_mode_requested.connect(lambda mode, mirror_key=key:
                                          self._mirror_fit_mode(mirror_key, mode))
        index = self.window_combo.currentIndex()
        entry = MirrorEntry(key, hwnd, source_title, region, mirror,
                            source_executable=self.window_combo.itemData(index, Qt.ItemDataRole.UserRole + 1) or "",
                            source_class=self.window_combo.itemData(index, Qt.ItemDataRole.UserRole + 2) or "")
        self._entries[key] = entry
        self._refresh_cards(key)
        self._show_entry(entry)

    def _current_entry(self) -> MirrorEntry | None:
        return self._entries.get(self._selected_key)

    def _select_entry(self, key: int) -> None:
        self._selected_key = key
        self._update_controls()

    def _card_action(self, key: int, action) -> None:
        self._select_entry(key)
        action()

    def _changed(self) -> None:
        if not self._loading:
            self.changed.emit()

    def _mirror_action(self, key: int, action: str) -> None:
        callbacks = {
            "hide": self.toggle_visibility,
            "lock": self.toggle_lock,
            "delete": self.delete_current,
        }
        if key in self._entries and action in callbacks:
            self._card_action(key, callbacks[action])

    def _mirror_opacity(self, key: int, percent: int) -> None:
        if key not in self._entries:
            return
        self._select_entry(key)
        self._change_transparency(100 - percent)
        self._refresh_cards(key)

    def _mirror_fit_mode(self, key: int, mode: str) -> None:
        entry = self._entries.get(key)
        if entry is None:
            return
        entry.window.set_fit_mode(mode)
        entry.fit_mode = mode
        self._select_entry(key)
        self._changed()

    def _edit_entry(self) -> None:
        self.details_dialog.exec()
        self._refresh_cards()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._position_cards()

    def eventFilter(self, watched, event) -> bool:
        if watched is self.card_scroll.viewport() and event.type() == QEvent.Type.Resize:
            self._position_cards()
        return super().eventFilter(watched, event)

    def _position_cards(self) -> None:
        self.card_grid.setAlignment(Qt.AlignmentFlag.AlignTop if self._cards else Qt.AlignmentFlag(0))
        arrange_cards(self.card_scroll, self.card_grid, list(self._cards.values()), 310)

    def _refresh_cards(self, selected_key: int | None = None) -> None:
        # Refresh the card collection after a mirror changes state.
        if selected_key is not None:
            self._selected_key = selected_key
        if self._selected_key not in self._entries:
            self._selected_key = next(iter(self._entries), None)
        for card in self._cards.values():
            self.card_grid.removeWidget(card)
            card.hide()
            card.deleteLater()
        self._cards.clear()
        self.empty_state.setVisible(not self._entries)
        self.empty_label.setText(
            f"{len(self._pending_mirrors)} recorte(s) aguardam uma janela.\n"
            "Selecione a janela acima e clique em Vincular."
            if self._pending_mirrors else
            "Selecione uma janela acima e clique em Novo recorte.\nVocê escolhe a área que quer acompanhar."
        )
        awaiting = bool(self._pending_mirrors) or any(entry.recovering for entry in self._entries.values())
        self.bind_button.setVisible(awaiting)
        self.bind_button.setEnabled(awaiting
                                    and self.window_combo.currentData() is not None)
        for entry in self._entries.values():
            card = QFrame()
            card.setObjectName("timerCard")
            card.setMinimumHeight(116)
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
            box = QVBoxLayout(card)
            box.setContentsMargins(14, 12, 14, 12)
            box.setSpacing(8)
            title = ElidedLabel(entry.region.name)
            title.setObjectName("sectionTitle")
            box.addWidget(title)
            source = ElidedLabel(entry.source_title)
            source.setObjectName("mutedText")
            box.addWidget(source)
            actions = QHBoxLayout()
            actions.setSpacing(4)
            for name, tooltip, callback in (
                ("pencil", "Configurar recorte", self._edit_entry),
                ("eye" if entry.visible else "eye-off",
                 "Cancelar recuperação" if entry.recovering else ("Ocultar" if entry.visible else "Mostrar"),
                 self.toggle_visibility),
                ("lock-keyhole" if entry.locked else "lock-keyhole-open", "Desbloquear" if entry.locked else "Bloquear cliques", self.toggle_lock),
                ("trash", "Excluir recorte", self.delete_current),
            ):
                button = QPushButton()
                button.setObjectName("iconButton")
                button.setFixedSize(28, 28)
                set_icon(button, name, size=16)
                button.setToolTip(tooltip)
                button.setAccessibleName(tooltip)
                button.clicked.connect(lambda checked=False, key=entry.key, fn=callback: self._card_action(key, fn))
                actions.addWidget(button)
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(10, 100)
            slider.setValue(100 - entry.transparency_percent)
            slider.setToolTip("Opacidade do recorte")
            slider.setMinimumWidth(45)
            value = QLabel(f"{slider.value()}%")
            value.setObjectName("percentageLabel")
            value.ensurePolished()
            value.setFixedWidth(value.fontMetrics().horizontalAdvance("100%") + 8)
            value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            slider.valueChanged.connect(lambda percent, key=entry.key, label=value: self._card_opacity(key, percent, label))
            actions.addWidget(slider, 1)
            actions.addWidget(value)
            box.addLayout(actions)
            self._cards[entry.key] = card
        self._position_cards()
        count = len(self._entries)
        visible = sum(entry.visible for entry in self._entries.values())
        summary = f"{visible}/{count} visíveis" if count else "Nenhum recorte criado"
        self.count_label.setVisible(bool(count or self._pending_mirrors))
        if self._pending_mirrors:
            summary += f" · {len(self._pending_mirrors)} aguardando janela"
        recovering = sum(entry.recovering for entry in self._entries.values())
        if recovering:
            summary += f" · {recovering} aguardando recuperação"
        self.count_label.setText(summary)
        self._update_controls()
        self._update_recovery_timer()

    def _card_opacity(self, key: int, percent: int, label: QLabel) -> None:
        self._select_entry(key)
        self._change_transparency(100 - percent)
        label.setText(f"{percent}%")

    def _refresh_theme(self) -> None:
        self._update_controls()

    def _update_controls(self) -> None:
        colors = current_palette()
        self.add_button.setEnabled(self.window_combo.currentData() is not None)
        self.bind_button.setEnabled((bool(self._pending_mirrors) or any(
            item.recovering for item in self._entries.values()))
                                    and self.window_combo.currentData() is not None)
        entry = self._current_entry()
        enabled = entry is not None
        for control in (self.rename_button, self.show_button, self.lock_button,
                        self.delete_button, self.fit_combo, self.transparency_slider):
            control.setEnabled(enabled)
        if entry is None:
            self.selected_name.setText("Selecione um recorte na lista")
            self.selected_source.setText("A origem e os controles aparecerão aqui.")
            self.selected_coordinates.clear()
            self.state_label.setText("Sem seleção")
            self.state_label.setStyleSheet(
                f"color: {colors['MUTED']}; background: {colors['SURFACE_HOVER']}; padding: 5px 9px; border-radius: 7px;")
            self.transparency_label.setText("Transparência  —")
            return
        self.selected_name.setText(entry.region.name)
        self.selected_source.setText(f"Janela de origem: {entry.source_title}")
        self.selected_coordinates.setText(
            f"Área: x={entry.region.x}, y={entry.region.y}  ·  "
            f"{entry.region.width} × {entry.region.height} px")
        state = "Aguardando origem" if entry.recovering else ("Visível" if entry.visible else "Oculto")
        state += " · Cliques bloqueados" if entry.locked else " · Editável"
        self.state_label.setText(state)
        bg, fg = colors["SURFACE_HOVER"], colors["ACCENT_LIGHT"] if entry.visible else colors["MUTED"]
        self.state_label.setStyleSheet(
            f"color: {fg}; background: {bg}; padding: 5px 9px; border-radius: 7px;")
        self.show_button.setText("Cancelar recuperação" if entry.recovering else
                                 ("Ocultar espelho" if entry.visible else "Mostrar espelho"))
        set_icon(self.show_button, "eye-off" if entry.visible else "eye", size=16)
        self.lock_button.setText("Desbloquear cliques" if entry.locked else "Bloquear cliques")
        set_icon(self.lock_button, "lock-keyhole-open" if entry.locked else "lock-keyhole", size=16)
        self.fit_combo.blockSignals(True)
        self.fit_combo.setCurrentIndex(self.fit_combo.findData(entry.fit_mode))
        self.fit_combo.blockSignals(False)
        self.transparency_slider.blockSignals(True)
        self.transparency_slider.setValue(entry.transparency_percent)
        self.transparency_slider.blockSignals(False)
        self.transparency_label.setText(f"Transparência  {entry.transparency_percent}%")

    def rename_current(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        name = self._ask_name("Renomear recorte", entry.region.name)
        if name:
            entry.region = Region(name, entry.region.x, entry.region.y,
                                  entry.region.width, entry.region.height)
            entry.window.rename(name)
            self._refresh_cards(entry.key)
            self._changed()

    def _ask_name(self, title: str, initial: str) -> str | None:
        dialog = StyledDialog(self, title)
        dialog.setMinimumWidth(340)
        field = QLineEdit(initial)
        field.setMaxLength(NAME_MAX_LENGTH)
        field.setToolTip(f"Máximo de {NAME_MAX_LENGTH} caracteres")
        field.setPlaceholderText("Nome do recorte")
        dialog.content_layout.addWidget(field)
        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(dialog.reject)
        save = QPushButton("Salvar")
        save.setObjectName("primaryButton")
        save.clicked.connect(dialog.accept)
        actions.addWidget(cancel)
        actions.addWidget(save)
        dialog.content_layout.addLayout(actions)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        return field.text().strip()

    def _show_entry(self, entry: MirrorEntry, *, refresh: bool = True) -> None:
        if refresh:
            self.refresh_windows()
        if entry.visible:
            return
        entry.recovering = True
        if self._try_resume_entry(entry):
            self.status_label.setText(f"{entry.region.name} está visível.")
        else:
            self.status_label.setText(
                f"{entry.region.name}: aguardando uma janela disponível. "
                "Se houver mais de uma possível, selecione a origem e clique em Vincular.")
        self._refresh_cards(entry.key)
        self._changed()

    def toggle_visibility(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        if entry.recovering:
            entry.recovering = False
            self.status_label.setText(f"{entry.region.name}: recuperação cancelada; espelho oculto.")
            self._refresh_cards(entry.key)
            self._changed()
        elif entry.visible:
            entry.window.close()
        else:
            self._show_entry(entry)

    def toggle_lock(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        try:
            entry.window.set_locked(not entry.locked)
        except RuntimeError as exc:
            QMessageBox.warning(self, "Bloqueio indisponível", str(exc))
            return
        entry.locked = entry.window.locked
        self._refresh_cards(entry.key)
        self._changed()
        self.status_label.setText(
            "Cliques atravessam o espelho. Desbloqueie pelo painel."
            if entry.locked else "Espelho desbloqueado: arraste a imagem ou as bordas.")

    def _change_fit_mode(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        mode = self.fit_combo.currentData()
        if mode is not None:
            entry.fit_mode = mode
            entry.window.set_fit_mode(mode)
            self._changed()

    def _change_transparency(self, percent: int) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        entry.transparency_percent = percent
        entry.window.set_opacity_percent(100 - percent)
        self.transparency_label.setText(f"Transparência  {percent}%")
        self._changed()

    def delete_current(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        del self._entries[entry.key]
        entry.window.close()
        entry.window.deleteLater()
        self.details_dialog.accept()
        self._refresh_cards()
        self.status_label.setText(f"{entry.region.name} foi excluído.")
        self._changed()

    def _on_mirror_stopped(self, key: int, message: str) -> None:
        entry = self._entries.get(key)
        if entry is None or self._shutting_down:
            return
        entry.recovering = bool(entry.window.source_interrupted) and (entry.visible or entry.recovering)
        entry.visible = False
        self._refresh_cards(key)
        self.status_label.setText(f"{entry.region.name}: {message}" +
                                  (". Aguardando recuperação; use Vincular se necessário." if entry.recovering else ""))
        self._changed()

    def export_state(self) -> list[dict]:
        records = list(self._pending_mirrors)
        for entry in self._entries.values():
            geometry = entry.window.geometry()
            records.append({
                "source_title": entry.source_title,
                "source_executable": entry.source_executable,
                "source_class": entry.source_class,
                "name": entry.region.name,
                "region": [entry.region.x, entry.region.y,
                           entry.region.width, entry.region.height],
                "geometry": [geometry.x(), geometry.y(), geometry.width(), geometry.height()],
                "visible": entry.visible or entry.recovering,
                "locked": entry.locked,
                "fit_mode": entry.fit_mode,
                "transparency_percent": entry.transparency_percent,
            })
        return records

    def load_state(self, records: list) -> list[str]:
        warnings = []
        if not isinstance(records, list):
            records = []
            warnings.append("Lista de recortes inválida; nenhum recorte restaurado.")
        self._loading = True
        try:
            for entry in list(self._entries.values()):
                del self._entries[entry.key]
                entry.window.close()
                entry.window.deleteLater()
            self._pending_mirrors = []
            self._selected_key = None
            for record in records:
                if isinstance(record, dict) and isinstance(record.get("name"), str):
                    if len(record["name"].strip()) > NAME_MAX_LENGTH:
                        warnings.append(f"Nome do recorte abreviado para {NAME_MAX_LENGTH} caracteres: {record['name']}")
                    record = {**record, "name": record["name"].strip()[:NAME_MAX_LENGTH]}
                if not self._valid_record(record):
                    warnings.append("Um recorte inválido foi ignorado.")
                    continue
                if not self._restore_record(record):
                    self._pending_mirrors.append(record)
                    warnings.append(f"Janela '{record['source_title']}' ausente; recorte '{record['name']}' aguardando.")
            self._refresh_cards()
        finally:
            self._loading = False
        return warnings

    @staticmethod
    def _valid_record(record) -> bool:
        if not isinstance(record, dict):
            return False
        region = record.get("region")
        geometry = record.get("geometry")
        return (
            isinstance(record.get("source_title"), str) and bool(record["source_title"].strip())
            and isinstance(record.get("source_executable", ""), str)
            and isinstance(record.get("source_class", ""), str)
            and isinstance(record.get("name"), str) and bool(record["name"].strip())
            and len(record["name"]) <= NAME_MAX_LENGTH
            and isinstance(region, list) and len(region) == 4
            and all(type(value) is int for value in region)
            and region[0] >= 0 and region[1] >= 0 and 1 <= region[2] <= 10000
            and 1 <= region[3] <= 10000
            and isinstance(geometry, list) and len(geometry) == 4
            and all(type(value) is int for value in geometry)
            and 24 <= geometry[2] <= 10000 and 24 <= geometry[3] <= 10000
            and type(record.get("visible")) is bool
            and type(record.get("locked")) is bool
            and record.get("fit_mode") in ("contain", "stretch")
            and type(record.get("transparency_percent")) is int
            and 0 <= record["transparency_percent"] <= 90
        )

    def _restore_record(self, record: dict, match_override: int | None = None) -> bool:
        executable = record.get("source_executable", "")
        window_class = record.get("source_class", "")
        match = match_override if match_override is not None else self._source_match(
            record["source_title"], executable, window_class)
        if match is None:
            return False
        hwnd = self.window_combo.itemData(match)
        if record["visible"]:
            try:
                area = get_client_area(hwnd)
                x, y, width, height = record["region"]
                if x + width > area.width or y + height > area.height:
                    return False
            except RuntimeError:
                return False
        current_title = self.window_combo.itemText(match)
        region = Region(record["name"], *record["region"])
        key = self._next_key
        self._next_key += 1
        mirror = DwmMirrorWindow(hwnd, region, fit_mode=record["fit_mode"])
        mirror.stopped.connect(lambda message, mirror_key=key:
                               self._on_mirror_stopped(mirror_key, message))
        mirror.action_requested.connect(lambda action, mirror_key=key:
                                        self._mirror_action(mirror_key, action))
        mirror.geometry_changed.connect(self._changed)
        mirror.opacity_requested.connect(lambda value, mirror_key=key:
                                          self._mirror_opacity(mirror_key, value))
        mirror.fit_mode_requested.connect(lambda mode, mirror_key=key:
                                          self._mirror_fit_mode(mirror_key, mode))
        mirror.setGeometry(*record["geometry"])
        mirror.set_locked(record["locked"])
        mirror.set_opacity_percent(100 - record["transparency_percent"])
        entry = MirrorEntry(key, hwnd, current_title, region, mirror,
                            visible=False, locked=record["locked"],
                            fit_mode=record["fit_mode"],
                            transparency_percent=record["transparency_percent"],
                            source_executable=executable or self.window_combo.itemData(
                                match, Qt.ItemDataRole.UserRole + 1) or "",
                            source_class=window_class or self.window_combo.itemData(
                                match, Qt.ItemDataRole.UserRole + 2) or "")
        self._entries[key] = entry
        if record["visible"]:
            self._show_entry(entry, refresh=False)
        return True

    def _restore_pending(self) -> None:
        remaining = []
        for record in self._pending_mirrors:
            if not self._restore_record(record):
                remaining.append(record)
        if len(remaining) != len(self._pending_mirrors):
            self._pending_mirrors = remaining
            self._refresh_cards()
            self._changed()

    def _bind_pending(self) -> None:
        index = self.window_combo.currentIndex()
        waiting = [entry for entry in self._entries.values() if entry.recovering]
        if index < 0 or not (self._pending_mirrors or waiting):
            return
        selected_hwnd = self.window_combo.itemData(index)
        dialog = StyledDialog(self, "Vincular recorte")
        dialog.setMinimumWidth(380)
        hint = QLabel("Escolha o recorte salvo para esta janela:")
        dialog.content_layout.addWidget(hint)
        choice = WindowSelector()
        choice.setPlaceholderText("Selecione o recorte salvo")
        for record in self._pending_mirrors:
            choice.addItem(f"{record['name']} · {record['source_title']}")
        for entry in waiting:
            choice.addItem(f"{entry.region.name} · {entry.source_title}")
        choice.setCurrentIndex(0)
        pending_records = list(self._pending_mirrors)
        pending_count = len(pending_records)
        dialog.content_layout.addWidget(choice)
        actions = QHBoxLayout()
        actions.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(dialog.reject)
        bind = QPushButton("Vincular")
        bind.setObjectName("primaryButton")
        bind.clicked.connect(dialog.accept)
        actions.addWidget(cancel)
        actions.addWidget(bind)
        dialog.content_layout.addLayout(actions)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        if not 0 <= choice.currentIndex() < choice.count():
            return
        index = self.window_combo.findData(selected_hwnd)
        if index < 0:
            self.status_label.setText("A janela escolhida não está mais disponível. Selecione outra origem.")
            return
        if choice.currentIndex() >= pending_count:
            entry = waiting[choice.currentIndex() - pending_count]
            if entry.key not in self._entries or not entry.recovering:
                return
            entry.source_hwnd = selected_hwnd
            entry.source_title = self.window_combo.itemText(index)
            entry.source_executable = self.window_combo.itemData(index, Qt.ItemDataRole.UserRole + 1) or ""
            entry.source_class = self.window_combo.itemData(index, Qt.ItemDataRole.UserRole + 2) or ""
            self._try_resume_entry(entry, match_override=index)
            self._refresh_cards(entry.key)
            self._changed()
            return
        original = pending_records[choice.currentIndex()]
        pending_index = next((i for i, item in enumerate(self._pending_mirrors)
                              if item is original), None)
        if pending_index is None:
            return
        record = self._pending_mirrors.pop(pending_index).copy()
        record["source_title"] = self.window_combo.itemText(index)
        record["source_executable"] = self.window_combo.itemData(
            index, Qt.ItemDataRole.UserRole + 1) or ""
        record["source_class"] = self.window_combo.itemData(
            index, Qt.ItemDataRole.UserRole + 2) or ""
        if not self._restore_record(record, match_override=index):
            self._pending_mirrors.append(record)
        self._refresh_cards()
        self._changed()

    def shutdown(self) -> bool:
        self._shutting_down = True
        self._recovery_timer.stop()
        for entry in self._entries.values():
            entry.window.close()
        self._entries.clear()
        return True
