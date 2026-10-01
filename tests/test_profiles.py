"""Persistência local de perfis e restauração de configuração."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from unittest.mock import Mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialog  # noqa: E402
from PySide6.QtGui import QCloseEvent  # noqa: E402

from tibiaenhanced.services.audio_timer import AudioTimer  # noqa: E402
from tibiaenhanced.services.profiles import ProfileStore  # noqa: E402
from tibiaenhanced.services.windowing import WindowInfo  # noqa: E402
from tibiaenhanced.ui.audio_panel import AudioPanel, DEFAULT_TIMERS  # noqa: E402
from tibiaenhanced.ui.capture_panel import CapturePanel  # noqa: E402
from tibiaenhanced.ui.main_window import MainWindow  # noqa: E402
from tibiaenhanced.services.profiles import empty_profile  # noqa: E402


class ProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_profile_store_roundtrip_and_invalid_file_backup(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "profiles.json"
            store = ProfileStore(path)
            store.create("Knight")
            store.active["audio"] = {"master_volume": 73, "timers": []}
            store.save()
            loaded = ProfileStore(path)
            self.assertEqual(loaded.load(), [])
            self.assertEqual(loaded.active_name, "Knight")
            self.assertEqual(loaded.active["audio"]["master_volume"], 73)
            self.assertEqual(loaded.data["schema_version"], 1)
            path.write_text("{broken", encoding="utf-8")
            warnings = ProfileStore(path).load()
            self.assertTrue(warnings)
            self.assertTrue(list(Path(folder).glob("profiles-invalid-*.json")))

    def test_rename_and_delete_preserve_other_profiles_and_rollback_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            store = ProfileStore(Path(folder) / "profiles.json")
            store.create("Knight")
            store.active["audio"] = {"master_volume": 73}
            store.rename("Knight", "Sorcerer")
            self.assertEqual(store.active_name, "Sorcerer")
            self.assertEqual(store.active["audio"]["master_volume"], 73)
            with patch.object(store, "save", side_effect=OSError("disk failure")):
                with self.assertRaises(OSError):
                    store.delete("Sorcerer")
            self.assertEqual(store.active_name, "Sorcerer")
            store.delete("Sorcerer")
            reloaded = ProfileStore(store.path)
            self.assertEqual(reloaded.load(), [])
            self.assertEqual(reloaded.active_name, "Padrão")
            self.assertEqual(list(reloaded.data["profiles"]), ["Padrão"])
            with self.assertRaises(ValueError):
                store.delete("Padrão")

    def test_audio_configuration_restores_without_starting_timers(self) -> None:
        panel = AudioPanel()
        custom = panel.add_timer(AudioTimer("Boost", 125, DEFAULT_TIMERS[0][2],
                                            volume=0.4, loop=True, shortcut="Ctrl+K"))
        panel.cards[0].loop_check.setChecked(True)
        panel.cards[0].volume.setValue(35)
        custom.timer.start()
        panel.master_volume.setValue(72)
        saved = panel.export_state()
        warnings = panel.load_state(saved)
        self.assertEqual(warnings, [])
        self.assertEqual(panel.master_volume.value(), 72)
        self.assertEqual([card.timer.name for card in panel.cards],
                         ["Foods 1h", "Potions 10min", "Boost"])
        self.assertFalse(any(card.timer.running for card in panel.cards))
        self.assertTrue(panel.cards[-1].timer.loop)
        self.assertEqual(panel.cards[-1].timer.shortcut, "Ctrl+K")
        self.assertTrue(panel.cards[0].timer.loop)
        self.assertEqual(panel.cards[0].timer.volume, 0.35)
        saved["timers"][-1]["sound_file"] = "C:/missing/sound.mp3"
        self.assertTrue(any("Áudio ausente" in warning for warning in panel.load_state(saved)))
        panel.close()

    def test_recorte_follows_tibia_process_when_character_changes(self) -> None:
        windows = [WindowInfo(42, "Tibia - Novo personagem", "client.exe", "TibiaClient")]
        record = {
            "source_title": "Tibia - Personagem antigo",
            "source_executable": "client.exe",
            "source_class": "TibiaClient",
            "name": "Vida",
            "region": [10, 20, 100, 50],
            "geometry": [120, 130, 200, 100],
            "visible": False,
            "locked": True,
            "fit_mode": "contain",
            "transparency_percent": 20,
        }
        with patch("tibiaenhanced.ui.capture_panel.list_windows", return_value=windows):
            panel = CapturePanel()
        self.assertEqual(panel.load_state([record]), [])
        self.assertEqual(len(panel.entries), 1)
        self.assertEqual(panel.entries[0].source_title, "Tibia - Novo personagem")
        restored = panel.export_state()[0]
        self.assertEqual(restored["region"], [10, 20, 100, 50])
        self.assertEqual(restored["geometry"], [120, 130, 200, 100])
        self.assertTrue(restored["locked"])
        self.assertEqual(restored["transparency_percent"], 20)
        panel.shutdown()

    def test_ambiguous_tibia_windows_remain_pending(self) -> None:
        windows = [WindowInfo(42, "Tibia - A", "client.exe", "TibiaClient"),
                   WindowInfo(43, "Tibia - B", "client.exe", "TibiaClient")]
        record = {
            "source_title": "Tibia - Antigo", "source_executable": "client.exe",
            "source_class": "TibiaClient", "name": "Mana", "region": [0, 0, 90, 30],
            "geometry": [0, 0, 90, 30], "visible": False, "locked": False,
            "fit_mode": "contain", "transparency_percent": 0,
        }
        with patch("tibiaenhanced.ui.capture_panel.list_windows", return_value=windows):
            panel = CapturePanel()
        self.assertTrue(panel.load_state([record]))
        self.assertFalse(panel.entries)
        self.assertEqual(panel.export_state(), [record])
        panel.window_combo.setCurrentIndex(1)
        with patch("tibiaenhanced.ui.capture_panel.StyledDialog.exec",
                   return_value=QDialog.DialogCode.Accepted):
            panel._bind_pending()
        self.assertEqual(panel.entries[0].source_title, "Tibia - B")
        self.assertFalse(panel._pending_mirrors)
        panel.shutdown()

    def test_switching_profiles_saves_each_audio_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            store = ProfileStore(Path(folder) / "profiles.json")
            store.data["profiles"]["Mage"] = empty_profile()
            with patch("tibiaenhanced.ui.capture_panel.list_windows", return_value=[]):
                window = MainWindow(store)
            window.audio_panel.add_timer(AudioTimer("Knight timer", 45, DEFAULT_TIMERS[0][2]))
            self.assertTrue(window._save_timer.isActive())
            window._save_timer.timeout.emit()
            self.assertTrue(store.path.is_file())
            combo = window._title_bar.profile_combo
            combo.setCurrentText("Mage")
            self.assertEqual(len(window.audio_panel.cards), 2)
            window.audio_panel.add_timer(AudioTimer("Mage timer", 60, DEFAULT_TIMERS[1][2]))
            combo.setCurrentText("Padrão")
            self.assertEqual([card.timer.name for card in window.audio_panel.cards][-1],
                             "Knight timer")
            self.assertFalse(any(card.timer.running for card in window.audio_panel.cards))
            reloaded = ProfileStore(store.path)
            self.assertEqual(reloaded.load(), [])
            self.assertEqual(reloaded.data["profiles"]["Mage"]["audio"]["timers"][-1]["name"],
                             "Mage timer")
            window._exiting = True
            window.capture_panel.shutdown()
            window.close()

    def test_profile_actions_rename_without_reset_and_delete_with_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            store = ProfileStore(Path(folder) / "profiles.json")
            store.create("Knight")
            with patch("tibiaenhanced.ui.capture_panel.list_windows", return_value=[]):
                window = MainWindow(store)
            window.audio_panel.cards[0].timer.start()
            with patch.object(window, "_ask_profile_name", return_value="Sorcerer"):
                window._rename_profile()
            self.assertTrue(window.audio_panel.cards[0].timer.running)
            self.assertEqual(window._title_bar.profile_combo.currentText(), "Sorcerer")
            with patch("tibiaenhanced.ui.main_window.StyledDialog.exec",
                       return_value=QDialog.DialogCode.Accepted):
                window._delete_profile()
            self.assertEqual(store.active_name, "Padrão")
            self.assertFalse(window._title_bar.delete_profile_action.isEnabled())
            self.assertFalse(window.audio_panel.cards[0].timer.running)
            window._exiting = True
            window.capture_panel.shutdown()
            window.close()

    def test_close_choice_can_cancel_hide_to_tray_or_exit(self) -> None:
        with patch("tibiaenhanced.ui.capture_panel.list_windows", return_value=[]):
            window = MainWindow()
        window.show()
        event = QCloseEvent()
        with patch.object(window, "_ask_close_action", return_value=None):
            window.closeEvent(event)
        self.assertFalse(event.isAccepted())
        self.assertTrue(window.isVisible())
        with patch.object(window, "_ask_close_action", return_value="tray"):
            window.closeEvent(event)
        self.assertFalse(event.isAccepted())
        self.assertFalse(window.isVisible())
        quit_app = Mock()
        with patch.object(window, "_ask_close_action", return_value="exit"), patch(
                "tibiaenhanced.ui.main_window.QApplication.instance",
                return_value=SimpleNamespace(quit=quit_app)):
            window.closeEvent(event)
        self.assertTrue(event.isAccepted())
        quit_app.assert_called_once()
        self.assertTrue(window._exiting)
        window.close()


if __name__ == "__main__":
    unittest.main()
