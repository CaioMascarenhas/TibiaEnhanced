"""Dados de domínio, independentes da interface e do mecanismo de captura."""

from dataclasses import dataclass
from pathlib import Path


NAME_MAX_LENGTH = 24


@dataclass(frozen=True, slots=True)
class Region:
    name: str
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class AudioAlert:
    name: str
    duration_seconds: int
    sound_file: Path
    volume: float = 1.0
