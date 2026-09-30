"""Painel de janelas de origem e seus espelhos DWM."""

from dataclasses import dataclass

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (QComboBox, QFrame, QGridLayout, QHBoxLayout,
                               QHeaderView, QInputDialog, QLabel, QMessageBox,
                               QPushButton, QScrollArea, QSlider, QTreeWidget,
                               QTreeWidgetItem, QVBoxLayout, QWidget)

from tibiaenhanced.models import Region
from tibiaenhanced.services.windowing import list_windows
from .dwm_windows import DwmMirrorWindow, DwmRegionDialog
from .design import heading_font, icon


@dataclass(slots=True)
class MirrorEntry:
    key: int
    source_hwnd: int
    source_title: str
    region: Region
    window: DwmMirrorWindow
    visible: bool = False
    locked: bool = False
    fit_mode: str = "contain"
    transparency_percent: int = 0


class CapturePanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("appPage")
        self._entries: dict[int, MirrorEntry] = {}
        self._next_key = 1
        self._shutting_down = False
        self._build_ui()
        self.refresh_windows()
        self._update_controls()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        title = QLabel("Espelhos")
        title.setObjectName("pageTitle")
        title.setFont(heading_font(19))
        layout.addWidget(title)
        subtitle = QLabel("Organize as áreas do Tibia que você quer acompanhar durante o jogo.")
        subtitle.setObjectName("mutedText")
        layout.addWidget(subtitle)

        source_card = QFrame()
        source_card.setObjectName("card")
        source_layout = QVBoxLayout(source_card)
        source_layout.setContentsMargins(14, 11, 14, 11)
        source_layout.setSpacing(7)
        source_heading = QLabel("1  Janela de origem")
        source_heading.setObjectName("sectionTitle")
        source_layout.addWidget(source_heading)
        source_row = QHBoxLayout()
        source_row.setSpacing(8)
        self.window_combo = QComboBox()
        self.window_combo.setToolTip("Escolha a janela que será espelhada")
        source_row.addWidget(self.window_combo, 1)
        refresh_button = QPushButton("Atualizar")
        refresh_button.setIcon(icon("refresh-cw", size=16))
        refresh_button.setIconSize(QSize(16, 16))
        refresh_button.setToolTip("Atualizar a lista de janelas abertas")
        refresh_button.clicked.connect(self.refresh_windows)
        source_row.addWidget(refresh_button)
        self.add_button = QPushButton("Novo recorte")
        self.add_button.setObjectName("primaryButton")
        self.add_button.setIcon(icon("plus", "#092035", 16))
        self.add_button.setIconSize(QSize(16, 16))
        self.add_button.setToolTip("Escolher uma área e criar um espelho")
        self.add_button.clicked.connect(self.add_mirror)
        source_row.addWidget(self.add_button)
        source_layout.addLayout(source_row)
        layout.addWidget(source_card)

        columns = QHBoxLayout()
        columns.setSpacing(10)

        list_card = QFrame()
        list_card.setObjectName("card")
        list_layout = QVBoxLayout(list_card)
        list_layout.setContentsMargins(14, 11, 14, 11)
        list_layout.setSpacing(7)
        list_heading = QLabel("2  Janelas e recortes")
        list_heading.setObjectName("sectionTitle")
        list_layout.addWidget(list_heading)
        self.mirror_tree = QTreeWidget()
        self.mirror_tree.setHeaderLabels(["ORIGEM / RECORTE", "ESTADO"])
        self.mirror_tree.setRootIsDecorated(True)
        self.mirror_tree.setIndentation(22)
        self.mirror_tree.setMinimumWidth(300)
        self.mirror_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.mirror_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.mirror_tree.itemSelectionChanged.connect(self._update_controls)
        list_layout.addWidget(self.mirror_tree, 1)
        self.count_label = QLabel("Nenhum recorte criado")
        self.count_label.setObjectName("mutedText")
        list_layout.addWidget(self.count_label)
        columns.addWidget(list_card, 11)

        detail_card = QFrame()
        detail_card.setObjectName("card")
        detail_layout = QVBoxLayout(detail_card)
        detail_layout.setContentsMargins(14, 11, 14, 11)
        detail_layout.setSpacing(7)
        detail_heading = QLabel("3  Recorte selecionado")
        detail_heading.setObjectName("sectionTitle")
        detail_layout.addWidget(detail_heading)
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
        detail_scroll = QScrollArea()
        detail_scroll.setObjectName("detailsScroll")
        detail_scroll.setFrameShape(QFrame.Shape.NoFrame)
        detail_scroll.setWidgetResizable(True)
        detail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        detail_scroll.setWidget(detail_card)
        columns.addWidget(detail_scroll, 9)
        layout.addLayout(columns, 1)

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
        except Exception as exc:
            self.status_label.setText(f"Não foi possível listar as janelas: {exc}")
        if previous is not None:
            index = self.window_combo.findData(previous)
            if index >= 0:
                self.window_combo.setCurrentIndex(index)
        self.window_combo.blockSignals(False)
        self._update_controls()

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
        entry = MirrorEntry(key, hwnd, source_title, region, mirror)
        self._entries[key] = entry
        self._refresh_tree(key)
        self._show_entry(entry)

    def _current_entry(self) -> MirrorEntry | None:
        item = self.mirror_tree.currentItem()
        if item is None:
            return None
        return self._entries.get(item.data(0, Qt.ItemDataRole.UserRole))

    def _refresh_tree(self, selected_key: int | None = None) -> None:
        if selected_key is None:
            current = self._current_entry()
            selected_key = current.key if current else None
        self.mirror_tree.blockSignals(True)
        self.mirror_tree.clear()
        roots: dict[int, QTreeWidgetItem] = {}
        selected_item: QTreeWidgetItem | None = None
        first_child: QTreeWidgetItem | None = None
        for entry in self._entries.values():
            root = roots.get(entry.source_hwnd)
            if root is None:
                root = QTreeWidgetItem(self.mirror_tree, [entry.source_title, "ORIGEM"])
                root.setIcon(0, icon("monitor", "#8bdcf2", 16))
                root.setFlags(root.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                font = QFont(root.font(0))
                font.setBold(True)
                root.setFont(0, font)
                root.setForeground(0, QColor("#a2e8f6"))
                root.setExpanded(True)
                roots[entry.source_hwnd] = root
            state = "VISÍVEL" if entry.visible else "OCULTO"
            if entry.locked:
                state += " · TRAVADO"
            child = QTreeWidgetItem(root, [entry.region.name, state])
            child.setIcon(0, icon("eye" if entry.visible else "eye-off", "#a4c4dc", 16))
            child.setData(0, Qt.ItemDataRole.UserRole, entry.key)
            child.setToolTip(0, f"{entry.region.width} × {entry.region.height} px")
            child.setForeground(1, QColor("#7ed7b0" if entry.visible else "#aeb9c7"))
            if first_child is None:
                first_child = child
            if entry.key == selected_key:
                selected_item = child
        self.mirror_tree.setCurrentItem(selected_item or first_child)
        self.mirror_tree.blockSignals(False)
        visible_count = sum(entry.visible for entry in self._entries.values())
        count = len(self._entries)
        self.count_label.setText(
            f"{count} recorte{'s' if count != 1 else ''}  ·  "
            f"{visible_count} {'visível' if visible_count == 1 else 'visíveis'}"
            if count else "Nenhum recorte criado")
        self._update_controls()

    def _update_controls(self) -> None:
        self.add_button.setEnabled(self.window_combo.currentData() is not None)
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
            self._refresh_tree(entry.key)

    def _ask_name(self, title: str, initial: str) -> str | None:
        dialog = QInputDialog(self)
        dialog.setWindowTitle(title)
        dialog.setLabelText("Nome do recorte")
        dialog.setTextValue(initial)
        dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        if dialog.exec() != QInputDialog.DialogCode.Accepted:
            return None
        return dialog.textValue().strip()

    def _show_entry(self, entry: MirrorEntry) -> None:
        entry.window.show()
        entry.visible = True
        self.status_label.setText(f"{entry.region.name} está visível.")
        self._refresh_tree(entry.key)

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
        self._refresh_tree(entry.key)
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

    def _change_transparency(self, percent: int) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        entry.transparency_percent = percent
        entry.window.set_opacity_percent(100 - percent)
        self.transparency_label.setText(f"Transparência  {percent}%")

    def delete_current(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        del self._entries[entry.key]
        entry.window.close()
        entry.window.deleteLater()
        self._refresh_tree()
        self.status_label.setText(f"{entry.region.name} foi excluído.")

    def _on_mirror_stopped(self, key: int, message: str) -> None:
        entry = self._entries.get(key)
        if entry is None or self._shutting_down:
            return
        entry.visible = False
        self._refresh_tree(key)
        self.status_label.setText(f"{entry.region.name}: {message}")

    def shutdown(self) -> bool:
        self._shutting_down = True
        for entry in self._entries.values():
            entry.window.close()
        self._entries.clear()
        return True
