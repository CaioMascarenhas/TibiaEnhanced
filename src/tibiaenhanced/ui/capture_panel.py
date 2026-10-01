"""Painel de janelas de origem e seus espelhos DWM."""

from dataclasses import dataclass

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (QComboBox, QDialog, QFrame, QGridLayout, QHBoxLayout,
                               QLabel, QLineEdit, QMessageBox,
                               QPushButton, QScrollArea,
                               QVBoxLayout, QWidget)

from tibiaenhanced.models import NAME_MAX_LENGTH, Region
from tibiaenhanced.services.windowing import list_windows
from .dwm_windows import DwmMirrorWindow, DwmRegionDialog
from .design import icon
from .design import CompactSlider as QSlider
from .dialog_shell import StyledDialog
from .window_selector import WindowSelector


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
        self._build_ui()
        self.refresh_windows()
        self._update_controls()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        source_heading = QLabel("JANELA DE ORIGEM")
        source_heading.setObjectName("eyebrow")
        layout.addWidget(source_heading)
        source_row = QHBoxLayout()
        source_row.setSpacing(6)
        self.window_combo = WindowSelector()
        source_row.addWidget(self.window_combo, 1)
        refresh_button = QPushButton()
        refresh_button.setFixedWidth(30)
        refresh_button.setIcon(icon("refresh-cw", size=16))
        refresh_button.setIconSize(QSize(16, 16))
        refresh_button.setToolTip("Atualizar a lista de janelas abertas")
        refresh_button.clicked.connect(self.refresh_windows)
        source_row.addWidget(refresh_button)
        self.bind_button = QPushButton("Vincular")
        self.bind_button.setToolTip("Associar um recorte salvo à janela selecionada")
        self.bind_button.clicked.connect(self._bind_pending)
        self.bind_button.hide()
        source_row.addWidget(self.bind_button)
        self.add_button = QPushButton("Novo recorte")
        self.add_button.setObjectName("primaryButton")
        self.add_button.setIcon(icon("plus", "#ffffff", 16))
        self.add_button.setIconSize(QSize(16, 16))
        self.add_button.setToolTip("Escolher uma área e criar um espelho")
        self.add_button.clicked.connect(self.add_mirror)
        source_row.addWidget(self.add_button)
        layout.addLayout(source_row)
        self.count_label = QLabel("Nenhum recorte criado")
        self.count_label.setObjectName("mutedText")
        layout.addWidget(self.count_label)
        scroll = QScrollArea()
        scroll.setObjectName("detailsScroll")
        scroll.setWidgetResizable(True)
        container = QWidget()
        container.setObjectName("appPage")
        self.card_grid = QGridLayout(container)
        self.card_grid.setContentsMargins(0, 0, 4, 0)
        self.card_grid.setSpacing(7)
        self.card_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.empty_label = QLabel("Seus recortes aparecem aqui.\nEscolha uma janela e clique em Novo recorte.")
        self.empty_label.setObjectName("mutedText")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_grid.addWidget(self.empty_label, 0, 0)
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
        self.selected_name = QLabel("Selecione um recorte na lista")
        self.selected_name.setObjectName("selectedTitle")
        self.selected_name.setWordWrap(True)
        detail_layout.addWidget(self.selected_name)
        self.selected_source = QLabel("A origem e os controles aparecerão aqui.")
        self.selected_source.setObjectName("mutedText")
        self.selected_source.setWordWrap(True)
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
        self.lock_button.setIcon(icon("lock-keyhole", size=16))
        self.lock_button.clicked.connect(self.toggle_lock)
        actions.addWidget(self.lock_button, 0, 1)
        self.rename_button = QPushButton("Renomear")
        self.rename_button.setIcon(icon("pencil", size=16))
        self.rename_button.clicked.connect(self.rename_current)
        actions.addWidget(self.rename_button, 1, 0)
        self.delete_button = QPushButton("Excluir recorte")
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.setIcon(icon("trash", "#ffc6cb", 16))
        self.delete_button.clicked.connect(self.delete_current)
        actions.addWidget(self.delete_button, 1, 1)
        detail_layout.addLayout(actions)

        display_heading = QLabel("APARÊNCIA")
        display_heading.setObjectName("eyebrow")
        detail_layout.addWidget(display_heading)
        fit_row = QHBoxLayout()
        fit_row.addWidget(QLabel("Ajuste"))
        self.fit_combo = QComboBox()
        self.fit_combo.addItem("Preservar proporção", "contain")
        self.fit_combo.addItem("Preencher janela", "stretch")
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

        self.status_label = QLabel("Escolha uma janela acima e crie seu primeiro recorte.")
        self.status_label.setObjectName("statusText")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        self.window_combo.currentIndexChanged.connect(self._update_controls)

    @property
    def entries(self) -> tuple[MirrorEntry, ...]:
        return tuple(self._entries.values())

    def refresh_windows(self) -> None:
        previous = self.window_combo.currentData()
        self.window_combo.blockSignals(True)
        self.window_combo.clear()
        try:
            for window in list_windows():
                self.window_combo.addItem(window.title, window.hwnd)
                self.window_combo.setItemData(self.window_combo.count() - 1, window.title,
                                              Qt.ItemDataRole.ToolTipRole)
                self.window_combo.setItemData(self.window_combo.count() - 1,
                                              getattr(window, "executable", ""), Qt.ItemDataRole.UserRole + 1)
                self.window_combo.setItemData(self.window_combo.count() - 1,
                                              getattr(window, "window_class", ""), Qt.ItemDataRole.UserRole + 2)
        except Exception as exc:
            self.status_label.setText(f"Não foi possível listar as janelas: {exc}")
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

    def _position_cards(self) -> None:
        columns = max(1, self.width() // 260)
        for index, card in enumerate(self._cards.values()):
            self.card_grid.removeWidget(card)
            self.card_grid.addWidget(card, index // columns, index % columns)
        rows = (len(self._cards) + columns - 1) // columns
        self.card_grid.parentWidget().setMinimumHeight(max(0, rows * 91 - 7))

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
        self.empty_label.setVisible(not self._entries)
        self.empty_label.setText(
            f"{len(self._pending_mirrors)} recorte(s) aguardam uma janela.\n"
            "Selecione a janela acima e clique em Vincular."
            if self._pending_mirrors else
            "Seus recortes aparecem aqui.\nEscolha uma janela e clique em Novo recorte."
        )
        self.bind_button.setVisible(bool(self._pending_mirrors))
        self.bind_button.setEnabled(bool(self._pending_mirrors)
                                    and self.window_combo.currentData() is not None)
        for entry in self._entries.values():
            card = QFrame()
            card.setObjectName("timerCard")
            card.setFixedHeight(84)
            card.setMaximumWidth(320)
            box = QVBoxLayout(card)
            box.setContentsMargins(10, 8, 10, 8)
            box.setSpacing(5)
            title = QLabel(entry.region.name)
            title.setObjectName("sectionTitle")
            title.setToolTip(entry.region.name)
            box.addWidget(title)
            source = QLabel()
            source.setObjectName("mutedText")
            source.setToolTip(entry.source_title)
            source.setMaximumWidth(230)
            source.setText(source.fontMetrics().elidedText(
                entry.source_title, Qt.TextElideMode.ElideRight, 225))
            box.addWidget(source)
            actions = QHBoxLayout()
            actions.setSpacing(3)
            for name, tooltip, callback in (
                ("pencil", "Configurar recorte", self._edit_entry),
                ("eye" if entry.visible else "eye-off", "Ocultar" if entry.visible else "Mostrar", self.toggle_visibility),
                ("lock-keyhole" if entry.locked else "lock-keyhole-open", "Desbloquear" if entry.locked else "Bloquear cliques", self.toggle_lock),
                ("trash", "Excluir recorte", self.delete_current),
            ):
                button = QPushButton()
                button.setObjectName("iconButton")
                button.setFixedSize(24, 24)
                button.setIcon(icon(name, size=14))
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
            value.setObjectName("mutedText")
            value.setFixedWidth(value.fontMetrics().horizontalAdvance("100%") + 4)
            value.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            slider.valueChanged.connect(lambda percent, key=entry.key, label=value: self._card_opacity(key, percent, label))
            actions.addWidget(slider, 1)
            actions.addWidget(value)
            box.addLayout(actions)
            self._cards[entry.key] = card
        self._position_cards()
        count = len(self._entries)
        visible = sum(entry.visible for entry in self._entries.values())
        summary = f"{visible}/{count} visíveis" if count else "Nenhum recorte criado"
        if self._pending_mirrors:
            summary += f" · {len(self._pending_mirrors)} aguardando janela"
        self.count_label.setText(summary)
        self._update_controls()

    def _card_opacity(self, key: int, percent: int, label: QLabel) -> None:
        self._select_entry(key)
        self._change_transparency(100 - percent)
        label.setText(f"{percent}%")

    def _update_controls(self) -> None:
        self.add_button.setEnabled(self.window_combo.currentData() is not None)
        self.bind_button.setEnabled(bool(self._pending_mirrors)
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
            self.state_label.setText("SEM SELEÇÃO")
            self.state_label.setStyleSheet("color: #9fb4c9; background: #24344a; padding: 5px 9px; border-radius: 7px;")
            self.transparency_label.setText("Transparência  —")
            return
        self.selected_name.setText(entry.region.name)
        self.selected_source.setText(f"Janela de origem: {entry.source_title}")
        self.selected_coordinates.setText(
            f"Área: x={entry.region.x}, y={entry.region.y}  ·  "
            f"{entry.region.width} × {entry.region.height} px")
        state = "VISÍVEL" if entry.visible else "OCULTO"
        state += " · CLIQUES BLOQUEADOS" if entry.locked else " · EDITÁVEL"
        self.state_label.setText(state)
        bg, fg = ("#1d4738", "#a8ebc2") if entry.visible else ("#39404a", "#d0d8e0")
        self.state_label.setStyleSheet(
            f"color: {fg}; background: {bg}; padding: 5px 9px; border-radius: 7px;")
        self.show_button.setText("Ocultar espelho" if entry.visible else "Mostrar espelho")
        self.show_button.setIcon(icon("eye-off" if entry.visible else "eye", size=16))
        self.lock_button.setText("Desbloquear cliques" if entry.locked else "Bloquear cliques")
        self.lock_button.setIcon(icon("lock-keyhole-open" if entry.locked else "lock-keyhole", size=16))
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

    def _show_entry(self, entry: MirrorEntry) -> None:
        entry.window.show()
        entry.visible = True
        self.status_label.setText(f"{entry.region.name} está visível.")
        self._refresh_cards(entry.key)
        self._changed()

    def toggle_visibility(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        if entry.visible:
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
        entry.visible = False
        self._refresh_cards(key)
        self.status_label.setText(f"{entry.region.name}: {message}")
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
                "visible": entry.visible,
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
        indexes = list(range(self.window_combo.count()))
        exact = [index for index in indexes
                 if self.window_combo.itemText(index) == record["source_title"]]
        match = match_override if match_override is not None else (exact[0] if len(exact) == 1 else None)
        executable = record.get("source_executable", "")
        window_class = record.get("source_class", "")
        if match is None and executable:
            candidates = [index for index in indexes
                          if self.window_combo.itemData(index, Qt.ItemDataRole.UserRole + 1) == executable
                          and (not window_class or self.window_combo.itemData(
                              index, Qt.ItemDataRole.UserRole + 2) == window_class)]
            if len(candidates) == 1:
                match = candidates[0]
        if match is None:
            return False
        hwnd = self.window_combo.itemData(match)
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
            self._show_entry(entry)
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
        if index < 0 or not self._pending_mirrors:
            return
        dialog = StyledDialog(self, "Vincular recorte")
        dialog.setMinimumWidth(380)
        hint = QLabel("Escolha o recorte salvo para esta janela:")
        dialog.content_layout.addWidget(hint)
        choice = QComboBox()
        for record in self._pending_mirrors:
            choice.addItem(f"{record['name']} · {record['source_title']}")
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
        record = self._pending_mirrors.pop(choice.currentIndex()).copy()
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
        for entry in self._entries.values():
            entry.window.close()
        self._entries.clear()
        return True
