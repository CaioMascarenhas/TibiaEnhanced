"""Cantos nativos para a janela de controle, sem composição por pixel alpha."""

import ctypes
from ctypes import wintypes


def request_rounded_corners(hwnd: int) -> bool:
    """Solicita arredondamento ao DWM; versões anteriores ao Windows 11 recusam."""
    dwm = ctypes.WinDLL("dwmapi", use_last_error=True)
    setter = dwm.DwmSetWindowAttribute
    setter.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
    setter.restype = ctypes.c_long
    preference = ctypes.c_uint(2)  # DWMWCP_ROUND
    return setter(hwnd, 33, ctypes.byref(preference), ctypes.sizeof(preference)) == 0
