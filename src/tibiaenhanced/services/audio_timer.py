"""Estado de um temporizador controlado manualmente."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class AudioTimer:
    name: str
    duration_seconds: int
    sound_file: Path
    volume: float = 1.0
    images: tuple[Path, ...] = ()
    loop: bool = False
    shortcut: str = ""
    clock: Callable[[], float] = field(default=time.monotonic, repr=False)
    remaining_seconds: float = field(init=False)
    deadline: float | None = field(default=None, init=False)
    finished: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if self.duration_seconds < 1:
            raise ValueError("A duração deve ser positiva")
        self.remaining_seconds = float(self.duration_seconds)

    @property
    def running(self) -> bool:
        return self.deadline is not None

    def remaining(self) -> int:
        if self.deadline is None:
            return math.ceil(self.remaining_seconds)
        return max(0, math.ceil(self.deadline - self.clock()))

    def start(self) -> None:
        if not self.running:
            if self.finished:
                self.remaining_seconds = float(self.duration_seconds)
                self.finished = False
            self.deadline = self.clock() + self.remaining_seconds

    def pause(self) -> None:
        if self.running:
            self.remaining_seconds = max(0.0, self.deadline - self.clock())
            self.deadline = None

    def reset(self) -> None:
        self.deadline = None
        self.remaining_seconds = float(self.duration_seconds)
        self.finished = False

    def tick(self) -> bool:
        """Retorna True uma vez por ciclo quando o prazo passa."""
        if self.running and self.deadline <= self.clock():
            if self.loop:
                # Após suspensão, começa um ciclo novo agora, sem disparar
                # um alerta para cada ciclo perdido.
                self.deadline = self.clock() + self.duration_seconds
                self.remaining_seconds = float(self.duration_seconds)
            else:
                self.deadline = None
                self.remaining_seconds = 0.0
                self.finished = True
            return True
        return False
