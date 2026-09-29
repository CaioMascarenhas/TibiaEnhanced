"""Controles do recorte visual do Tibia."""

import time

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QMessageBox,
                               QPushButton, QVBoxLayout, QWidget)

from tibiaenhanced.models import Region
from tibiaenhanced.services.windowing import list_windows
from .dwm_windows import DwmMirrorWindow, DwmRegionDialog


class CapturePanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._region: Region | None = None
        self._selected_hwnd: int | None = None
        self._mirror: DwmMirrorWindow | None = None
        self._cpu_started_at = time.process_time()
        self._wall_started_at = time.perf_counter()

        layout = QVBoxLayout(self)
        heading = QLabel("Recortes")
        heading.setStyleSheet("font-size: 20px; font-weight: 600;")
        layout.addWidget(heading)
        chooser = QHBoxLayout()
        chooser.addWidget(QLabel("Janela:"))
        self.window_combo = QComboBox()
        chooser.addWidget(self.window_combo, 1)
        refresh = QPushButton("Atualizar lista")
        refresh.clicked.connect(self.refresh_windows)
        chooser.addWidget(refresh)
        layout.addLayout(chooser)
        controls = QHBoxLayout()
        self.select_button = QPushButton("Selecionar região")
        self.select_button.clicked.connect(self.choose_region)
        controls.addWidget(self.select_button)
        self.start_button = QPushButton("Abrir espelho")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_capture)
        controls.addWidget(self.start_button)
        self.stop_button = QPushButton("Parar")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_capture)
        controls.addWidget(self.stop_button)
        controls.addStretch()
        layout.addLayout(controls)
        self.region_label = QLabel("Nenhuma região selecionada")
        layout.addWidget(self.region_label)
        self.status_label = QLabel("Selecione uma janela e uma região para começar.")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        self.metric_label = QLabel("DWM: —  |  CPU do aplicativo: —")
        layout.addWidget(self.metric_label)
        info = QLabel("O espelho usa a miniatura visual do Windows. Ela acompanha a imagem "
                      "do jogo sem ler memória ou enviar comandos ao cliente. A taxa de "
                      "quadros é controlada pelo compositor do Windows.")
        info.setWordWrap(True)
        layout.addWidget(info)
        layout.addStretch()
        self.window_combo.currentIndexChanged.connect(self._on_window_changed)
        self._metric_timer = QTimer(self)
        self._metric_timer.timeout.connect(self._update_metrics)
        self.refresh_windows()

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
        self._on_window_changed()

    def _on_window_changed(self) -> None:
        hwnd = self.window_combo.currentData()
        if hwnd != self._selected_hwnd:
            self.stop_capture()
            self._selected_hwnd = hwnd
            self._region = None
            self.region_label.setText("Nenhuma região selecionada")
            self.start_button.setEnabled(False)
        self.select_button.setEnabled(hwnd is not None)

    def choose_region(self) -> None:
        hwnd = self.window_combo.currentData()
        if hwnd is None:
            return
        self.stop_capture()
        try:
            dialog = DwmRegionDialog(hwnd, self)
        except RuntimeError as exc:
            QMessageBox.warning(self, "Espelho indisponível", str(exc))
            return
        if dialog.exec() != DwmRegionDialog.DialogCode.Accepted:
            return
        rect = dialog.selection
        self._region = Region("Recorte 1", rect.x(), rect.y(), rect.width(), rect.height())
        self.region_label.setText(f"Região: x={rect.x()}, y={rect.y()}, "
                                  f"{rect.width()} × {rect.height()} px")
        self.start_button.setEnabled(True)
        self.status_label.setText("Região selecionada. Clique em Abrir espelho.")

    def start_capture(self) -> None:
        hwnd = self.window_combo.currentData()
        if hwnd is None or self._region is None or self._mirror is not None:
            return
        self._mirror = DwmMirrorWindow(hwnd, self._region)
        self._mirror.stopped.connect(self._on_mirror_stopped)
        self._mirror.show()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Espelho visual ao vivo aberto.")
        self._cpu_started_at = time.process_time()
        self._wall_started_at = time.perf_counter()
        self._metric_timer.start(1000)

    def stop_capture(self) -> None:
        if self._mirror is not None:
            self._mirror.close()

    def _on_mirror_stopped(self, message: str) -> None:
        self._metric_timer.stop()
        self._mirror = None
        self.start_button.setEnabled(self._region is not None and self.window_combo.currentData() is not None)
        self.stop_button.setEnabled(False)
        self.status_label.setText(message)

    def _update_metrics(self) -> None:
        if self._mirror is None:
            return
        elapsed = time.perf_counter() - self._wall_started_at
        cpu = 100 * (time.process_time() - self._cpu_started_at) / max(elapsed, 0.001)
        self.metric_label.setText(f"DWM: {self._mirror.elapsed_seconds:.0f} s ativo  |  "
                                  f"CPU do aplicativo: {cpu:.1f}%  |  FPS: gerenciado pelo Windows")
        self._cpu_started_at = time.process_time()
        self._wall_started_at = time.perf_counter()

    def shutdown(self) -> bool:
        self.stop_capture()
        return True
