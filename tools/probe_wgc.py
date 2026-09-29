"""Diagnóstico manual e local da captura WGC da janela do Tibia."""

import time

from windows_capture import WindowsCapture

from tibiaenhanced.services.windowing import list_windows


def main() -> None:
    window = next(
        (item for item in list_windows() if item.title == "Tibia" or item.title.startswith("Tibia -")),
        None,
    )
    if window is None:
        raise SystemExit("Janela do Tibia não encontrada")

    capture = WindowsCapture(
        cursor_capture=False,
        draw_border=None,
        monitor_index=None,
        window_hwnd=window.hwnd,
        minimum_update_interval=66,
    )
    frames: list[tuple[int, int, float, float]] = []

    @capture.event
    def on_frame_arrived(frame, control) -> None:
        sample = frame.frame_buffer[::8, ::8, :3]
        nonblack = float((sample.max(axis=2) > 0).mean())
        center = frame.frame_buffer[
            frame.height // 10: frame.height * 9 // 10:8,
            frame.width // 10: frame.width * 9 // 10:8,
            :3,
        ]
        center_nonblack = float((center.max(axis=2) > 0).mean())
        frames.append((frame.width, frame.height, nonblack, center_nonblack))
        if len(frames) >= 10:
            control.stop()

    @capture.event
    def on_closed() -> None:
        pass

    started = time.perf_counter()
    control = capture.start_free_threaded()
    time.sleep(5)
    control.stop()
    control.wait()
    print({"window": window.title, "frames": len(frames), "elapsed": round(time.perf_counter() - started, 2), "samples": frames[:3]})


if __name__ == "__main__":
    main()
