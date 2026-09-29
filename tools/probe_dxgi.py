"""Mede somente a área do Tibia no monitor quando ele está em primeiro plano."""

import ctypes

from windows_capture import DxgiDuplicationSession

from tibiaenhanced.services.windowing import get_client_area, list_windows


def main() -> None:
    window = next(
        (item for item in list_windows() if item.title == "Tibia" or item.title.startswith("Tibia -")),
        None,
    )
    if window is None:
        raise SystemExit("Janela do Tibia não encontrada")
    if ctypes.windll.user32.GetForegroundWindow() != window.hwnd:
        raise SystemExit("Deixe o Tibia em primeiro plano antes do teste")

    area = get_client_area(window.hwnd)
    session = DxgiDuplicationSession()
    frame = session.acquire_frame(timeout_ms=1000)
    if frame is None:
        raise SystemExit("A API DXGI não entregou um quadro")
    image = frame.to_numpy()
    if area.left < 0 or area.top < 0 or area.left + area.width > frame.width or area.top + area.height > frame.height:
        raise SystemExit("A janela está fora dos limites do monitor principal")
    target = image[area.top:area.top + area.height:8, area.left:area.left + area.width:8, :3]
    print({
        "window": window.title,
        "monitor_size": (frame.width, frame.height),
        "client_size": (area.width, area.height),
        "nonblack_fraction": round(float((target.max(axis=2) > 0).mean()), 3),
    })


if __name__ == "__main__":
    main()
