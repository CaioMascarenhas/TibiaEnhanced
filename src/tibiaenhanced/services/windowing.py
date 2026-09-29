"""Consulta de janelas Win32 sem tocar no processo do jogo."""

import ctypes
import os
from ctypes import wintypes
from dataclasses import dataclass


user32 = ctypes.WinDLL("user32", use_last_error=True)


class _Point(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


class _Rect(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


user32.IsWindow.argtypes = [wintypes.HWND]
user32.IsWindow.restype = wintypes.BOOL
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL
user32.IsIconic.argtypes = [wintypes.HWND]
user32.IsIconic.restype = wintypes.BOOL
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(_Rect)]
user32.GetClientRect.restype = wintypes.BOOL
user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(_Point)]
user32.ClientToScreen.restype = wintypes.BOOL
user32.GetWindowDisplayAffinity.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowDisplayAffinity.restype = wintypes.BOOL

WDA_MONITOR = 0x00000001
WDA_EXCLUDEFROMCAPTURE = 0x00000011


@dataclass(frozen=True, slots=True)
class WindowInfo:
    hwnd: int
    title: str


@dataclass(frozen=True, slots=True)
class ClientArea:
    left: int
    top: int
    width: int
    height: int


def enable_per_monitor_dpi_awareness() -> None:
    """Alinha coordenadas Win32 e pixels capturados em monitores com escala diferente."""
    try:
        setter = user32.SetProcessDpiAwarenessContext
        setter.argtypes = [ctypes.c_void_p]
        setter.restype = wintypes.BOOL
        if setter(ctypes.c_void_p(-4)):
            return
    except AttributeError:
        pass
    try:
        shcore = ctypes.WinDLL("shcore", use_last_error=True)
        shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        pass


def list_windows() -> list[WindowInfo]:
    windows: list[WindowInfo] = []
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def visit(hwnd: int, _param: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        title_length = user32.GetWindowTextLengthW(hwnd)
        if not title_length:
            return True
        owner_pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner_pid))
        if owner_pid.value == os.getpid():
            return True
        area = _Rect()
        if not user32.GetClientRect(hwnd, ctypes.byref(area)) or area.right < 80 or area.bottom < 80:
            return True
        title = ctypes.create_unicode_buffer(title_length + 1)
        user32.GetWindowTextW(hwnd, title, len(title))
        if title.value:
            windows.append(WindowInfo(int(hwnd), title.value))
        return True

    user32.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    user32.EnumWindows.restype = wintypes.BOOL
    user32.EnumWindows(callback_type(visit), 0)
    return sorted(windows, key=lambda item: ("tibia" not in item.title.casefold(), item.title.casefold()))


def get_client_area(hwnd: int) -> ClientArea:
    if not user32.IsWindow(hwnd):
        raise RuntimeError("A janela selecionada foi fechada")
    if user32.IsIconic(hwnd):
        raise RuntimeError("A janela selecionada está minimizada")
    area = _Rect()
    origin = _Point(0, 0)
    if not user32.GetClientRect(hwnd, ctypes.byref(area)) or not user32.ClientToScreen(hwnd, ctypes.byref(origin)):
        raise RuntimeError("Não foi possível obter a área da janela")
    width = area.right - area.left
    height = area.bottom - area.top
    if width < 1 or height < 1:
        raise RuntimeError("A área da janela está vazia")
    return ClientArea(origin.x, origin.y, width, height)


def get_display_affinity(hwnd: int) -> int | None:
    """Retorna a política de captura declarada pela janela, quando disponível."""
    value = wintypes.DWORD()
    if user32.GetWindowDisplayAffinity(hwnd, ctypes.byref(value)):
        return value.value
    return None


def require_capturable_window(hwnd: int) -> None:
    affinity = get_display_affinity(hwnd)
    if affinity in (WDA_MONITOR, WDA_EXCLUDEFROMCAPTURE):
        raise RuntimeError(
            "A janela selecionada declarou uma restrição de captura ao Windows "
            f"(WDA={affinity:#x}). O aplicativo respeita essa configuração e não "
            "pode espelhar seu conteúdo."
        )
