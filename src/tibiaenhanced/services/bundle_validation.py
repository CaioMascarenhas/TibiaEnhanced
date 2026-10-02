"""Diagnóstico do pacote executável, com perfil e janelas de teste próprios."""

import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import time
import traceback
import uuid

from PySide6.QtCore import QEvent, QEventLoop, QPoint, QPointF, Qt, QTimer
from PySide6.QtGui import QEnterEvent, QMouseEvent, QPixmap
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication, QWidget

from ..app import create_application
from ..ui.design import ASSETS
from ..ui.main_window import MainWindow
from .profiles import ProfileStore
from .windowing import list_windows


def _wait(predicate, timeout=5.0):
    deadline = time.monotonic() + timeout
    while not predicate():
        if time.monotonic() >= deadline:
            raise RuntimeError("Tempo limite no diagnóstico do pacote")
        loop = QEventLoop()
        QTimer.singleShot(25, loop.quit)
        loop.exec()


def run_source(title, control_file, status_file):
    """Janela de diagnóstico em outro processo; nunca controla janelas do usuário."""
    app = create_application([sys.argv[0]])
    source = QWidget()
    source.setWindowTitle(title)
    source.setStyleSheet("background: #c43b35")
    source.setGeometry(100, 100, 320, 240)
    source.show()
    last_id = -1

    def poll():
        nonlocal last_id
        try:
            command = json.loads(Path(control_file).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            command = {"id": 0, "action": "ready"}
        if command["id"] == last_id:
            return
        action = command["action"]
        if action == "minimize":
            source.showMinimized()
        elif action == "restore":
            source.showNormal()
        elif action == "quit":
            app.quit()
            return
        last_id = command["id"]
        Path(status_file).write_text(json.dumps({"id": last_id, "hwnd": int(source.winId()),
                                               "minimized": source.isMinimized()}), encoding="utf-8")

    timer = QTimer(source)
    timer.timeout.connect(poll)
    timer.start(50)
    return app.exec()


def _native_mirrors(window, check):
    title = "Tibia Enhanced build source " + uuid.uuid4().hex
    process = None
    with tempfile.TemporaryDirectory(prefix="tibiaenhanced-source-check-") as folder:
        control = Path(folder) / "control.json"
        status = Path(folder) / "status.json"
        command_id = 0

        def get_status():
            try:
                return json.loads(status.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                return {}

        def command(action):
            nonlocal command_id
            command_id += 1
            temporary = control.with_suffix(".tmp")
            temporary.write_text(json.dumps({"id": command_id, "action": action}), encoding="utf-8")
            os.replace(temporary, control)
            if action == "quit":
                _wait(lambda: process.poll() is not None)
            else:
                _wait(lambda: get_status().get("id") == command_id)

        def new_source():
            nonlocal process, command_id
            command_id = 0
            control.write_text(json.dumps({"id": 0, "action": "ready"}), encoding="utf-8")
            if status.exists():
                status.unlink()
            entry = [] if getattr(sys, "frozen", False) else [str(Path(sys.argv[0]).resolve())]
            process = subprocess.Popen([sys.executable, *entry, "--synthetic-source", title,
                                        "--source-control", str(control), "--source-status", str(status)],
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            _wait(lambda: "hwnd" in get_status())
            hwnd = get_status()["hwnd"]
            _wait(lambda: any(item.hwnd == hwnd for item in list_windows()))
            return hwnd

        try:
            hwnd = new_source()
            info = next(item for item in list_windows() if item.hwnd == hwnd)
            panel = window.capture_panel
            panel.refresh_windows()
            record = {
                "source_title": info.title, "source_executable": info.executable,
                "source_class": info.window_class, "name": "Build check",
                "region": [10, 10, 100, 80], "geometry": [450, 100, 180, 120],
                "visible": True, "locked": True, "fit_mode": "contain", "transparency_percent": 25,
            }
            check("restore_synthetic_mirror", not panel.load_state([record]))
            entry = panel.entries[0]
            _wait(lambda: entry.window.active)
            check("native_dwm_thumbnail", entry.visible and entry.window.active)
            geometry = entry.window.geometry()
            command("minimize")
            entry.window._refresh()
            check("minimized_source_waits", entry.recovering and not entry.visible)
            command("restore")
            panel._poll_sources()
            _wait(lambda: entry.window.active)
            check("restored_source_resumes", entry.visible and not entry.recovering)
            command("quit")
            entry.window._refresh()
            check("closed_source_waits", entry.recovering and not entry.visible)
            hwnd = new_source()
            panel._poll_sources()
            _wait(lambda: entry.window.active)
            check("reopened_source_resumes", entry.source_hwnd == hwnd and entry.visible)
            check("mirror_preferences_preserved", entry.window.geometry() == geometry and
                  entry.window.locked and entry.window.opacity_percent == 75 and entry.window.fit_mode == "contain")
            panel._select_entry(entry.key)
            panel.toggle_visibility()
            panel._poll_sources()
            check("hidden_mirror_stays_hidden", not entry.visible and not entry.recovering)
        finally:
            window.capture_panel.shutdown()
            if process is not None and process.poll() is None:
                process.terminate()
                process.wait(timeout=5)


def run_validation(report_file, screenshot_file=None, *, native=True):
    report = {"frozen": bool(getattr(sys, "frozen", False)), "executable": sys.executable,
              "assets": str(ASSETS), "native": native, "checks": {}, "status": "failed"}
    window = None

    def check(name, condition):
        report["checks"][name] = bool(condition)
        if not condition:
            raise RuntimeError(f"Falha no diagnóstico: {name}")

    try:
        app = create_application([sys.argv[0]])
        # Nomes resolvidos após create_application registrar as fontes.
        from ..ui import design
        check("fonts", design.HEADING_FAMILY == "Space Grotesk" and design.BODY_FAMILY.startswith("DM Sans"))
        for path in (ASSETS / "icons").glob("*.svg"):
            check("svg_" + path.stem, QSvgRenderer(str(path)).isValid())
        for path in (ASSETS / "imgs").rglob("*.png"):
            check("image_" + path.stem, not QPixmap(str(path)).isNull())
        with tempfile.TemporaryDirectory(prefix="tibiaenhanced-bundle-check-") as folder:
            profiles = ProfileStore(Path(folder) / "profiles.json")
            profiles.create("Build check")
            window = MainWindow(profiles)
            window.show()
            QApplication.processEvents()
            tabs = window.centralWidget()
            check("tabs", [tabs.tabText(i) for i in range(tabs.count())] == ["Recortes", "Alertas", "Donate"])
            check("app_icon", not window.windowIcon().isNull())
            window.audio_panel.cards[0].loop_check.setChecked(True)
            window._save_profile()
            reloaded = ProfileStore(profiles.path)
            check("profile_roundtrip", not reloaded.load() and reloaded.active_name == "Build check")
            state = reloaded.active["audio"]
            check("portable_audio_paths", all("sound_asset" in item and not Path(item["sound_file"]).is_absolute()
                                              for item in state["timers"]))
            check("audio_restore", not window.audio_panel.load_state(state))
            if native:
                for card in window.audio_panel.cards:
                    card.audio_output.setVolume(0)
                    card.player.play()
                    _wait(lambda: card.player.position() > 0 or card.player.error() != QMediaPlayer.Error.NoError)
                    check("decode_" + card.timer.sound_file.name, card.player.error() == QMediaPlayer.Error.NoError)
                    card.player.stop()
                _native_mirrors(window, check)
            tabs.setCurrentWidget(window.donate_panel)
            QApplication.processEvents()
            donate = window.donate_panel
            donate.copy_character_button.click()
            check("copy_character", QApplication.clipboard().text() == donate.character_label.text())
            donate.copy_pix_button.click()
            check("copy_pix", QApplication.clipboard().text() == donate.key_label.text())
            edge = QPoint(1, 200)
            QApplication.sendEvent(window, QMouseEvent(
                QEvent.Type.MouseMove, QPointF(edge), QPointF(window.mapToGlobal(edge)),
                Qt.MouseButton.NoButton, Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier))
            check("resize_cursor", window.cursor().shape() == Qt.CursorShape.SizeHorCursor)
            label = donate.character_label
            local = label.rect().center()
            global_point = label.mapToGlobal(local)
            QApplication.sendEvent(label, QEnterEvent(QPointF(local), QPointF(window.mapFromGlobal(global_point)),
                                                      QPointF(global_point)))
            check("cursor_resets_in_content", window.cursor().shape() == Qt.CursorShape.BitmapCursor)
            check("qr_present", not donate.qr_label.pixmap().isNull())
            if screenshot_file:
                check("screenshot", window.grab().save(str(screenshot_file)))
            for width, height in ((680, 460), (560, 380)):
                window.resize(width, height)
                QApplication.processEvents()
                check(f"layout_{width}", donate.scroll.horizontalScrollBar().maximum() == 0)
            window.exit_app()
            window = None
        report["status"] = "passed"
    except Exception:
        report["error"] = traceback.format_exc()
    finally:
        if window is not None:
            window.exit_app()
        Path(report_file).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0 if report["status"] == "passed" else 1
