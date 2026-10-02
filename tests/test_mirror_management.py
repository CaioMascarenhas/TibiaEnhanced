"""Ciclo de vida de vários espelhos no painel, sem abrir o cliente do jogo."""

import os
import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, QRect, Signal  # noqa: E402
from PySide6.QtWidgets import QApplication, QDialog, QPushButton, QSlider  # noqa: E402

from tibiaenhanced.models import Region  # noqa: E402
from tibiaenhanced.ui.capture_panel import CapturePanel, MirrorEntry  # noqa: E402
from tibiaenhanced.services.windowing import WindowInfo  # noqa: E402
from tibiaenhanced.ui.dwm_windows import DwmMirrorWindow  # noqa: E402


class _FakeWindow(QObject):
    stopped = Signal(str)
    action_requested = Signal(str)
    geometry_changed = Signal()
    opacity_requested = Signal(int)
    fit_mode_requested = Signal(str)

    def __init__(self, hwnd=42, region=None, *, fit_mode="contain") -> None:
        super().__init__()
        self.active = False
        self.locked = False
        self.fit_mode = fit_mode
        self.opacity_percent = 100
        self.source_interrupted = False
        self.hwnd = hwnd
        self._geometry = QRect(120, 130, 200, 100)

    def geometry(self):
        return QRect(self._geometry)

    def setGeometry(self, *args):
        self._geometry = QRect(*args)

    def rebind_source(self, hwnd):
        self.hwnd = hwnd
        self.source_interrupted = False

    def interrupt(self):
        self.active = False
        self.source_interrupted = True
        self.stopped.emit("A janela selecionada foi fechada")

    def show(self) -> None:
        self.active = True

    def close(self) -> None:
        self.active = False
        self.source_interrupted = False
        self.stopped.emit("Espelho fechado")

    def set_locked(self, value: bool) -> None:
        self.locked = value

    def set_fit_mode(self, mode: str) -> None:
        self.fit_mode = mode

    def set_opacity_percent(self, percent: int) -> None:
        self.opacity_percent = percent

    def rename(self, _name: str) -> None:
        pass


class MirrorManagementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        area = patch("tibiaenhanced.ui.capture_panel.get_client_area",
                     return_value=SimpleNamespace(width=800, height=600))
        area.start()
        self.addCleanup(area.stop)

    def test_two_regions_from_same_source_are_independent(self) -> None:
        with patch("tibiaenhanced.ui.capture_panel.list_windows", return_value=[WindowInfo(42, "Tibia")]):
            panel = CapturePanel()
        first_window = _FakeWindow()
        second_window = _FakeWindow()
        first_window.stopped.connect(lambda message: panel._on_mirror_stopped(1, message))
        second_window.stopped.connect(lambda message: panel._on_mirror_stopped(2, message))
        panel._entries = {
            1: MirrorEntry(1, 42, "Tibia", Region("HP", 0, 0, 100, 40), first_window),
            2: MirrorEntry(2, 42, "Tibia", Region("Mana", 120, 0, 100, 40), second_window),
        }
        panel._refresh_cards(1)
        panel._show_entry(panel._entries[1], refresh=False)
        panel._show_entry(panel._entries[2], refresh=False)
        self.assertTrue(first_window.active)
        self.assertTrue(second_window.active)

        self.assertEqual(set(panel._cards), {1, 2})
        panel._cards[1].findChildren(QPushButton)[2].click()
        self.assertTrue(first_window.locked)
        self.assertFalse(second_window.locked)
        panel._cards[1].findChild(QSlider).setValue(55)
        self.assertEqual(first_window.opacity_percent, 55)
        self.assertEqual(second_window.opacity_percent, 100)
        panel._cards[1].findChildren(QPushButton)[1].click()
        self.assertFalse(first_window.active)
        self.assertTrue(second_window.active)

        panel._cards[2].findChildren(QPushButton)[3].click()
        self.assertFalse(second_window.active)
        self.assertEqual([entry.region.name for entry in panel.entries], ["HP"])
        panel.shutdown()

    def test_mirror_menu_actions_update_panel_entry(self) -> None:
        with patch("tibiaenhanced.ui.capture_panel.list_windows", return_value=[WindowInfo(42, "Tibia")]):
            panel = CapturePanel()
        window = _FakeWindow()
        window.stopped.connect(lambda message: panel._on_mirror_stopped(1, message))
        panel._entries[1] = MirrorEntry(1, 42, "Tibia", Region("HP", 0, 0, 100, 40), window)
        panel._show_entry(panel._entries[1], refresh=False)
        panel._mirror_opacity(1, 55)
        self.assertEqual(window.opacity_percent, 55)
        self.assertEqual(panel._entries[1].transparency_percent, 45)
        panel._mirror_fit_mode(1, "contain")
        self.assertEqual(window.fit_mode, "contain")
        self.assertEqual(panel._entries[1].fit_mode, "contain")
        self.assertEqual(panel.fit_combo.currentData(), "contain")
        panel._mirror_action(1, "lock")
        self.assertTrue(panel._entries[1].locked)
        panel._mirror_action(1, "hide")
        self.assertFalse(panel._entries[1].visible)
        panel._mirror_action(1, "delete")
        self.assertFalse(panel._entries)
        panel.shutdown()


class MirrorRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.windows = [WindowInfo(42, "Tibia - Old", "client.exe", "TibiaClient")]
        for patcher in (
            patch("tibiaenhanced.ui.capture_panel.list_windows", side_effect=lambda: list(self.windows)),
            patch("tibiaenhanced.ui.capture_panel.get_client_area",
                  return_value=SimpleNamespace(width=800, height=600)),
            patch("tibiaenhanced.ui.capture_panel.DwmMirrorWindow", side_effect=_FakeWindow),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.panel = CapturePanel()
        self.addCleanup(self.panel.shutdown)

    def add_entry(self, name="Vida", visible=True):
        key = self.panel._next_key
        self.panel._next_key += 1
        window = _FakeWindow()
        window.set_locked(True)
        window.set_opacity_percent(65)
        entry = MirrorEntry(key, 42, "Tibia - Old", Region(name, 10, 20, 100, 40),
                            window, locked=True, fit_mode="contain", transparency_percent=35,
                            source_executable="client.exe", source_class="TibiaClient")
        window.stopped.connect(lambda message: self.panel._on_mirror_stopped(key, message))
        self.panel._entries[key] = entry
        if visible:
            self.panel._show_entry(entry, refresh=False)
        else:
            self.panel._refresh_cards(key)
        return entry

    def test_reopened_source_preserves_recorte_and_does_not_show_hidden_mirror(self):
        entry = self.add_entry()
        hidden = self.add_entry("Mana", visible=False)
        original_window = entry.window
        geometry = entry.window.geometry()
        self.windows = []
        entry.window.interrupt()
        self.assertTrue(entry.recovering)
        self.assertFalse(entry.visible)
        self.assertTrue(self.panel._recovery_timer.isActive())
        records = {record["name"]: record for record in self.panel.export_state()}
        self.assertTrue(records["Vida"]["visible"])
        self.assertFalse(records["Mana"]["visible"])
        self.panel._poll_sources()
        self.assertFalse(entry.window.active)
        self.windows = [WindowInfo(43, "Tibia - New", "client.exe", "TibiaClient")]
        self.panel._poll_sources()
        self.assertTrue(entry.visible)
        self.assertFalse(entry.recovering)
        self.assertEqual(entry.source_hwnd, 43)
        self.assertEqual(entry.window.hwnd, 43)
        self.assertEqual(entry.source_title, "Tibia - New")
        self.assertIs(entry.window, original_window)
        self.assertEqual(entry.window.geometry(), geometry)
        self.assertEqual(entry.region, Region("Vida", 10, 20, 100, 40))
        self.assertTrue(entry.window.locked)
        self.assertEqual(entry.window.opacity_percent, 65)
        self.assertEqual(entry.window.fit_mode, "contain")
        self.assertFalse(hidden.visible)
        self.assertFalse(self.panel._recovery_timer.isActive())
        self.panel._show_entry(hidden)
        self.assertTrue(hidden.visible)
        self.assertEqual(hidden.window.hwnd, 43)
        self.assertEqual(len(self.panel.entries), 2)

    def test_minimized_or_small_source_waits_until_original_window_is_ready(self):
        entry = self.add_entry()
        entry.window.interrupt()
        with patch("tibiaenhanced.ui.capture_panel.get_client_area",
                   side_effect=RuntimeError("A janela selecionada está minimizada")):
            self.panel._poll_sources()
        self.assertTrue(entry.recovering)
        self.assertFalse(entry.window.active)
        with patch("tibiaenhanced.ui.capture_panel.get_client_area",
                   return_value=SimpleNamespace(width=50, height=30)):
            self.panel._poll_sources()
        self.assertTrue(entry.recovering)
        self.panel._poll_sources()
        self.assertTrue(entry.visible)
        self.assertEqual(entry.source_hwnd, 42)

    def test_ambiguous_source_requires_binding_and_keeps_existing_window(self):
        entry = self.add_entry()
        self.windows = [WindowInfo(43, "Tibia - A", "client.exe", "TibiaClient"),
                        WindowInfo(44, "Tibia - B", "client.exe", "TibiaClient")]
        entry.window.interrupt()
        self.panel._poll_sources()
        self.assertTrue(entry.recovering)
        self.assertFalse(entry.visible)
        self.panel.window_combo.setCurrentIndex(1)
        with patch("tibiaenhanced.ui.capture_panel.StyledDialog.exec",
                   return_value=QDialog.DialogCode.Accepted):
            self.panel._bind_pending()
        self.assertTrue(entry.visible)
        self.assertEqual(entry.source_hwnd, 44)
        self.assertEqual(entry.window.hwnd, 44)
        self.assertEqual(len(self.panel.entries), 1)
        self.assertFalse(self.panel._recovery_timer.isActive())

    def test_user_can_cancel_recovery_and_shutdown_stops_polling(self):
        entry = self.add_entry()
        self.windows = []
        entry.window.interrupt()
        self.panel._select_entry(entry.key)
        self.panel.toggle_visibility()
        self.assertFalse(entry.recovering)
        self.assertFalse(self.panel.export_state()[0]["visible"])
        self.assertFalse(self.panel._recovery_timer.isActive())
        self.windows = [WindowInfo(43, "Tibia - New", "client.exe", "TibiaClient")]
        self.panel._poll_sources()
        self.assertFalse(entry.visible)
        self.panel._show_entry(entry)
        self.assertTrue(entry.visible)
        entry.window.interrupt()
        self.assertTrue(self.panel._recovery_timer.isActive())
        self.panel.shutdown()
        self.assertFalse(self.panel._recovery_timer.isActive())
        self.panel._poll_sources()
        self.assertFalse(self.panel.entries)

    def test_same_title_from_another_program_is_not_used(self):
        entry = self.add_entry()
        self.windows = [WindowInfo(43, "Tibia - Old", "other.exe", "TibiaClient")]
        entry.window.interrupt()
        self.panel._poll_sources()
        self.assertTrue(entry.recovering)
        self.assertEqual(entry.source_hwnd, 42)

    def test_pending_visible_recorte_waits_for_source_then_restores_once(self):
        entry = self.add_entry()
        record = self.panel.export_state()[0]
        self.windows = []
        self.panel.refresh_windows()
        self.assertTrue(self.panel.load_state([record]))
        self.assertTrue(self.panel._recovery_timer.isActive())
        self.windows = [WindowInfo(43, "Tibia - New", "client.exe", "TibiaClient")]
        with patch("tibiaenhanced.ui.capture_panel.get_client_area",
                   side_effect=RuntimeError("minimizada")):
            self.panel._poll_sources()
        self.assertFalse(self.panel.entries)
        self.panel._poll_sources()
        self.panel._poll_sources()
        self.assertEqual(len(self.panel.entries), 1)
        restored = self.panel.entries[0]
        self.assertTrue(restored.visible)
        self.assertEqual(restored.window.geometry(), entry.window.geometry())
        self.assertTrue(restored.locked)
        self.assertEqual(restored.transparency_percent, 35)
        self.assertFalse(self.panel._pending_mirrors)
        self.assertFalse(self.panel._recovery_timer.isActive())

    def test_dwm_failure_marks_interruption_and_does_not_restart_refresh_timer(self):
        window = DwmMirrorWindow(42, Region("Vida", 0, 0, 100, 40))
        backend = Mock()
        backend.update.side_effect = RuntimeError("A janela selecionada está minimizada")
        with patch("tibiaenhanced.ui.dwm_windows.get_client_area"), \
                patch("tibiaenhanced.ui.dwm_windows.DwmMirror", return_value=backend), \
                patch.object(window, "_apply_lock_style"):
            window._start()
        self.assertTrue(window.source_interrupted)
        self.assertFalse(window.active)
        self.assertFalse(window._timer.isActive())
        backend.close.assert_called_once()
        window.rebind_source(43)
        self.assertEqual(window._hwnd, 43)
        self.assertFalse(window.source_interrupted)
        window.close()


if __name__ == "__main__":
    unittest.main()
