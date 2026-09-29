"""Espelhamento visual de uma janela com miniaturas oficiais do DWM."""

import ctypes
from ctypes import wintypes

from tibiaenhanced.models import Region
from .windowing import get_client_area


class Rect(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG),
                ("right", wintypes.LONG), ("bottom", wintypes.LONG)]


class ThumbnailProperties(ctypes.Structure):
    _fields_ = [("flags", wintypes.DWORD), ("destination", Rect),
                ("source", Rect), ("opacity", ctypes.c_ubyte),
                ("visible", wintypes.BOOL), ("client_only", wintypes.BOOL)]


dwm = ctypes.WinDLL("dwmapi", use_last_error=True)
dwm.DwmRegisterThumbnail.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.POINTER(wintypes.HANDLE)]
dwm.DwmRegisterThumbnail.restype = ctypes.c_long
dwm.DwmUpdateThumbnailProperties.argtypes = [wintypes.HANDLE, ctypes.POINTER(ThumbnailProperties)]
dwm.DwmUpdateThumbnailProperties.restype = ctypes.c_long
dwm.DwmUnregisterThumbnail.argtypes = [wintypes.HANDLE]
dwm.DwmUnregisterThumbnail.restype = ctypes.c_long


class DwmMirror:
    """Mantém uma miniatura viva em uma janela de destino de nível superior."""

    def __init__(self, source_hwnd: int, destination_hwnd: int) -> None:
        self.source_hwnd = source_hwnd
        self._handle = wintypes.HANDLE()
        result = dwm.DwmRegisterThumbnail(destination_hwnd, source_hwnd, ctypes.byref(self._handle))
        if result:
            raise RuntimeError(f"O DWM não conseguiu abrir o espelho ({result & 0xffffffff:#x})")

    def update(self, region: Region | None, destination: tuple[int, int, int, int]) -> None:
        area = get_client_area(self.source_hwnd)
        if region is None:
            source = Rect(0, 0, area.width, area.height)
        else:
            if (region.x < 0 or region.y < 0 or region.width < 1 or region.height < 1
                    or region.x + region.width > area.width
                    or region.y + region.height > area.height):
                raise RuntimeError("O recorte não cabe mais na janela do Tibia")
            source = Rect(region.x, region.y, region.x + region.width, region.y + region.height)
        x, y, width, height = destination
        properties = ThumbnailProperties(
            flags=0x1 | 0x2 | 0x4 | 0x8 | 0x10,
            destination=Rect(x, y, x + width, y + height),
            source=source,
            opacity=255,
            visible=True,
            client_only=True,
        )
        result = dwm.DwmUpdateThumbnailProperties(self._handle, ctypes.byref(properties))
        if result:
            raise RuntimeError(f"O DWM não conseguiu atualizar o espelho ({result & 0xffffffff:#x})")

    def close(self) -> None:
        if self._handle.value:
            dwm.DwmUnregisterThumbnail(self._handle)
            self._handle = wintypes.HANDLE()
