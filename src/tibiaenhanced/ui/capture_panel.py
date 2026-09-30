"""Gerencia vários recortes visuais e suas janelas DWM."""

import time
from dataclasses import dataclass

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (QComboBox, QHBoxLayout, QInputDialog, QLabel,
                               QListWidget, QListWidgetItem, QMessageBox,
                               QPushButton, QSlider, QVBoxLayout, QWidget)

from tibiaenhanced.models import Region
from tibiaenhanced.services.windowing import list_windows
from .dwm_windows import DwmMirrorWindow, DwmRegionDialog


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
        self._entries: dict[int, MirrorEntry] = {}
        self._next_key = 1
        self._shutting_down = False
        self._cpu_started_at = time.process_time()
        self._wall_started_at = time.perf_counter()

        layout = QVBoxLayout(self)
        heading = QLabel("Recortes")
        heading.setStyleSheet("font-size: 20px; font-weight: 600;")
        layout.addWidget(heading)

        source_row = QHBoxLayout()
        source_row.addWidget(QLabel("Janela de origem:"))
        self.window_combo = QComboBox()
        source_row.addWidget(self.window_combo, 1)
        refresh_button = QPushButton("Atualizar janelas")
        refresh_button.clicked.connect(self.refresh_windows)
        source_row.addWidget(refresh_button)
        self.add_button = QPushButton("Novo recorte")
        self.add_button.clicked.connect(self.add_mirror)
        source_row.addWidget(self.add_button)
        layout.addLayout(source_row)

        layout.addWidget(QLabel("Espelhos:"))
        self.mirror_list = QListWidget()
        self.mirror_list.currentItemChanged.connect(self._on_selection_changed)
        layout.addWidget(self.mirror_list, 1)

        actions = QHBoxLayout()
        self.rename_button = QPushButton("Renomear")
        self.rename_button.clicked.connect(self.rename_current)
        actions.addWidget(self.rename_button)
        self.show_button = QPushButton("Ocultar")
        self.show_button.clicked.connect(self.toggle_visibility)
        actions.addWidget(self.show_button)
        self.lock_button = QPushButton("Bloquear")
        self.lock_button.clicked.connect(self.toggle_lock)
        actions.addWidget(self.lock_button)
        self.delete_button = QPushButton("Excluir")
        self.delete_button.clicked.connect(self.delete_current)
        actions.addWidget(self.delete_button)
        layout.addLayout(actions)

        fit_row = QHBoxLayout()
        fit_row.addWidget(QLabel("Ajuste da imagem:"))
        self.fit_combo = QComboBox()
        self.fit_combo.addItem("Preservar proporção", "contain")
        self.fit_combo.addItem("Preencher janela", "stretch")
        self.fit_combo.currentIndexChanged.connect(self._change_fit_mode)
        fit_row.addWidget(self.fit_combo)
        fit_row.addStretch()
        layout.addLayout(fit_row)

        opacity_row = QHBoxLayout()
        self.transparency_label = QLabel("Transparência: 0%")
        opacity_row.addWidget(self.transparency_label)
        self.transparency_slider = QSlider(Qt.Orientation.Horizontal)
        self.transparency_slider.setRange(0, 90)
        self.transparency_slider.setSingleStep(5)
        self.transparency_slider.setPageStep(10)
        self.transparency_slider.setTickInterval(10)
        self.transparency_slider.valueChanged.connect(self._change_transparency)
        opacity_row.addWidget(self.transparency_slider, 1)
        layout.addLayout(opacity_row)

        self.status_label = QLabel("Escolha a janela do Tibia e crie um recorte.")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        self.metric_label = QLabel("Espelhos ativos: 0  |  CPU do aplicativo: —")
        layout.addWidget(self.metric_label)
        hint = QLabel("Arraste a imagem do espelho para mover e use as bordas para redimensionar. "
                      "Ao bloquear, os cliques atravessam o espelho; desbloqueie pelo painel.")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.window_combo.currentIndexChanged.connect(self._update_controls)
        self._metric_timer = QTimer(self)
        self._metric_timer.timeout.connect(self._update_metrics)
        self.refresh_windows()
        self._update_controls()

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
        try:
            dialog = DwmRegionDialog(hwnd, self)
        except RuntimeError as exc:
            QMessageBox.warning(self, "Espelho indisponível", str(exc))
            return
        if dialog.exec() != DwmRegionDialog.DialogCode.Accepted:
            return
        default_name = f"Recorte {self._next_key}"
        name = self._ask_name("Nome do recorte", default_name)
        if name is None:
            return
        name = name or default_name
        rect = dialog.selection
        region = Region(name, rect.x(), rect.y(), rect.width(), rect.height())
        key = self._next_key
        self._next_key += 1
        mirror = DwmMirrorWindow(hwnd, region)
        mirror.stopped.connect(lambda message, mirror_key=key:
                               self._on_mirror_stopped(mirror_key, message))
        entry = MirrorEntry(key, hwnd, self.window_combo.currentText(), region, mirror)
        self._entries[key] = entry
        self._refresh_list(key)
        self._show_entry(entry)

    def _current_entry(self) -> MirrorEntry | None:
        item = self.mirror_list.currentItem()
        if item is None:
            return None
        return self._entries.get(item.data(Qt.ItemDataRole.UserRole))

    def _refresh_list(self, selected_key: int | None = None) -> None:
        if selected_key is None:
            current = self._current_entry()
            selected_key = current.key if current else None
        self.mirror_list.blockSignals(True)
        self.mirror_list.clear()
        selected_row = -1
        for row, entry in enumerate(self._entries.values()):
            state = "Aberto" if entry.visible else "Oculto"
            lock = " · bloqueado" if entry.locked else ""
            label = (f"{entry.region.name} — {entry.source_title} · "
                     f"{entry.region.width} × {entry.region.height} px · {state}{lock}")
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, entry.key)
            self.mirror_list.addItem(item)
            if entry.key == selected_key:
                selected_row = row
        if selected_row >= 0:
            self.mirror_list.setCurrentRow(selected_row)
        self.mirror_list.blockSignals(False)
        self._update_controls()

    def _on_selection_changed(self, _current, _previous) -> None:
        self._update_controls()

    def _update_controls(self) -> None:
        self.add_button.setEnabled(self.window_combo.currentData() is not None)
        entry = self._current_entry()
        enabled = entry is not None
        for button in (self.rename_button, self.show_button, self.lock_button,
                       self.delete_button, self.fit_combo, self.transparency_slider):
            button.setEnabled(enabled)
        if entry is not None:
            self.show_button.setText("Ocultar" if entry.visible else "Mostrar")
            self.lock_button.setText("Desbloquear" if entry.locked else "Bloquear")
            self.fit_combo.blockSignals(True)
            self.fit_combo.setCurrentIndex(self.fit_combo.findData(entry.fit_mode))
            self.fit_combo.blockSignals(False)
            self.transparency_slider.blockSignals(True)
            self.transparency_slider.setValue(entry.transparency_percent)
            self.transparency_slider.blockSignals(False)
            self.transparency_label.setText(f"Transparência: {entry.transparency_percent}%")
        else:
            self.transparency_label.setText("Transparência: —")

    def rename_current(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        name = self._ask_name("Renomear recorte", entry.region.name)
        if name:
            entry.region = Region(name, entry.region.x, entry.region.y,
                                  entry.region.width, entry.region.height)
            entry.window.rename(entry.region.name)
            self._refresh_list(entry.key)

    def _ask_name(self, title: str, initial: str) -> str | None:
        dialog = QInputDialog(self)
        dialog.setWindowTitle(title)
        dialog.setLabelText("Nome:")
        dialog.setTextValue(initial)
        dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        if dialog.exec() != QInputDialog.DialogCode.Accepted:
            return None
        return dialog.textValue().strip()

    def _show_entry(self, entry: MirrorEntry) -> None:
        entry.window.show()
        entry.visible = True
        self.status_label.setText(f"Espelho {entry.region.name} aberto.")
        self._refresh_list(entry.key)
        QTimer.singleShot(0, self._sync_metrics)

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
        self._refresh_list(entry.key)
        self.status_label.setText(
            "Espelho bloqueado; cliques atravessam a janela. Desbloqueie pelo painel."
            if entry.locked else "Espelho desbloqueado; pode mover e redimensionar.")

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
        self.transparency_label.setText(f"Transparência: {percent}%")

    def delete_current(self) -> None:
        entry = self._current_entry()
        if entry is None:
            return
        del self._entries[entry.key]
        entry.window.close()
        entry.window.deleteLater()
        self._refresh_list()
        self._sync_metrics()
        self.status_label.setText(f"Recorte {entry.region.name} excluído.")

    def _on_mirror_stopped(self, key: int, message: str) -> None:
        entry = self._entries.get(key)
        if entry is None or self._shutting_down:
            return
        entry.visible = False
        self._refresh_list(key)
        self._sync_metrics()
        self.status_label.setText(f"{entry.region.name}: {message}")

    def _sync_metrics(self) -> None:
        active = sum(entry.window.active for entry in self._entries.values())
        if active and not self._metric_timer.isActive():
            self._cpu_started_at = time.process_time()
            self._wall_started_at = time.perf_counter()
            self._metric_timer.start(1000)
        elif not active:
            self._metric_timer.stop()
            self.metric_label.setText("Espelhos ativos: 0  |  CPU do aplicativo: —")

    def _update_metrics(self) -> None:
        active = sum(entry.window.active for entry in self._entries.values())
        elapsed = time.perf_counter() - self._wall_started_at
        cpu = 100 * (time.process_time() - self._cpu_started_at) / max(elapsed, 0.001)
        self.metric_label.setText(f"Espelhos ativos: {active}  |  "
                                  f"CPU do aplicativo: {cpu:.1f}%")
        self._cpu_started_at = time.process_time()
        self._wall_started_at = time.perf_counter()

    def shutdown(self) -> bool:
        self._shutting_down = True
        for entry in self._entries.values():
            entry.window.close()
        self._entries.clear()
        self._metric_timer.stop()
        return True
