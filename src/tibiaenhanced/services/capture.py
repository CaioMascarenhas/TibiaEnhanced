"""Execução de captura fora da thread da interface.

A implementação da fonte de quadros será adicionada na issue #2. A fonte deve
retornar de ``grab_frame`` periodicamente para permitir uma parada rápida.
"""

from collections.abc import Callable
from typing import Protocol
from threading import Event

from PySide6.QtCore import QObject, QThread, Signal, Slot


class FrameSource(Protocol):
    def grab_frame(self) -> object | None: ...

    def close(self) -> None: ...


class _CaptureWorker(QObject):
    frame_ready = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, source_factory: Callable[[], FrameSource], stop_event: Event) -> None:
        super().__init__()
        self._source_factory = source_factory
        self._stop_event = stop_event

    @Slot()
    def run(self) -> None:
        source: FrameSource | None = None
        try:
            source = self._source_factory()
            while not self._stop_event.is_set():
                frame = source.grab_frame()
                if frame is not None and not self._stop_event.is_set():
                    self.frame_ready.emit(frame)
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            if source is not None:
                try:
                    source.close()
                except Exception as exc:
                    self.failed.emit(str(exc))
            self.finished.emit()


class CaptureService(QObject):
    """Controla uma fonte de quadros sem bloquear o loop da interface."""

    frame_ready = Signal(object)
    failed = Signal(str)
    stopped = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._thread: QThread | None = None
        self._worker: _CaptureWorker | None = None
        self._stop_event: Event | None = None

    @property
    def running(self) -> bool:
        return self._thread is not None

    def start(self, source_factory: Callable[[], FrameSource]) -> None:
        if self.running:
            raise RuntimeError("A captura já está em execução")

        self._stop_event = Event()
        self._thread = QThread(self)
        self._worker = _CaptureWorker(source_factory, self._stop_event)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.frame_ready.connect(self.frame_ready)
        self._worker.failed.connect(self.failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._on_thread_finished)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def stop(self) -> None:
        if self._stop_event is not None:
            self._stop_event.set()

    @Slot()
    def _on_thread_finished(self) -> None:
        self._thread = None
        self._worker = None
        self._stop_event = None
        self.stopped.emit()
