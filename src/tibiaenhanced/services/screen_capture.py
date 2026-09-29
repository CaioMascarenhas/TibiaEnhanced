"""Captura de pixels visíveis da tela com MSS."""

import time
from dataclasses import dataclass

import mss

from tibiaenhanced.models import Region
from .windowing import get_client_area, require_capturable_window


@dataclass(frozen=True, slots=True)
class Frame:
    bgra: bytes
    width: int
    height: int
    captured_at: float


def _capture_box(hwnd: int, region: Region | None) -> dict[str, int]:
    area = get_client_area(hwnd)
    if region is None:
        return {"left": area.left, "top": area.top, "width": area.width, "height": area.height}
    if (region.x < 0 or region.y < 0 or region.width < 1 or region.height < 1
            or region.x + region.width > area.width or region.y + region.height > area.height):
        raise RuntimeError("O recorte não cabe mais na janela. Selecione a região novamente")
    return {
        "left": area.left + region.x,
        "top": area.top + region.y,
        "width": region.width,
        "height": region.height,
    }


def frame_is_blank(frame: Frame) -> bool:
    """Detecta quadros totalmente pretos sem interpretar o conteúdo do jogo."""
    pixels = memoryview(frame.bgra)
    stride = max(1, (frame.width * frame.height) // 1500) * 4
    return all(not (pixels[index] | pixels[index + 1] | pixels[index + 2])
               for index in range(0, len(pixels), stride))


def snapshot_window(hwnd: int) -> Frame:
    require_capturable_window(hwnd)
    with mss.MSS() as screen:
        box = _capture_box(hwnd, None)
        shot = screen.grab(box)
        frame = Frame(shot.bgra, shot.width, shot.height, time.perf_counter())
        if frame_is_blank(frame):
            raise RuntimeError(
                "A captura da janela retornou somente preto. Verifique se o Tibia está "
                "visível em modo janela e tente novamente. Este protótipo não contorna "
                "bloqueios de captura do jogo ou do Windows."
            )
        return frame


class WindowRegionSource:
    def __init__(self, hwnd: int, region: Region, max_fps: int = 15) -> None:
        self._hwnd = hwnd
        self._region = region
        self._min_interval = 1 / max_fps
        self._last_capture = 0.0
        self._screen = mss.MSS()
        self._blank_frames = 0

    def grab_frame(self) -> Frame:
        require_capturable_window(self._hwnd)
        remaining = self._min_interval - (time.perf_counter() - self._last_capture)
        if remaining > 0:
            time.sleep(remaining)
        box = _capture_box(self._hwnd, self._region)
        shot = self._screen.grab(box)
        captured_at = time.perf_counter()
        self._last_capture = captured_at
        frame = Frame(shot.bgra, shot.width, shot.height, captured_at)
        self._blank_frames = self._blank_frames + 1 if frame_is_blank(frame) else 0
        if self._blank_frames >= 10:
            raise RuntimeError("A captura retornou apenas quadros pretos. Pare e revise o método de captura.")
        return frame

    def close(self) -> None:
        self._screen.close()
