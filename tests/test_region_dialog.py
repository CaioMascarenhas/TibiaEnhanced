"""Seleção de recorte em coordenadas da imagem."""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, QRect, Qt  # noqa: E402
from PySide6.QtGui import QImage  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication, QPushButton, QSlider  # noqa: E402

from tibiaenhanced.ui.region_dialog import RegionDialog  # noqa: E402
from tibiaenhanced.ui.dwm_windows import DwmMirrorWindow, DwmRegionDialog  # noqa: E402
from tibiaenhanced.models import Region  # noqa: E402


class RegionDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_drag_selects_image_pixel_rectangle(self) -> None:
        image = QImage(320, 200, QImage.Format.Format_RGB32)
        image.fill(Qt.GlobalColor.red)
        dialog = RegionDialog(image)
        dialog.show()
        canvas = dialog._canvas
        QTest.mousePress(canvas, Qt.MouseButton.LeftButton, pos=QPoint(10, 20))
        QTest.mouseMove(canvas, QPoint(70, 80))
        QTest.mouseRelease(canvas, Qt.MouseButton.LeftButton, pos=QPoint(70, 80))
        selection = dialog.selection
        self.assertEqual((selection.x(), selection.y(), selection.width(), selection.height()), (10, 20, 60, 60))
        dialog.close()

    def test_dwm_region_dialog_has_rounded_frameless_window(self) -> None:
        with patch("tibiaenhanced.ui.dwm_windows.get_client_area",
                   return_value=SimpleNamespace(width=800, height=600)):
            dialog = DwmRegionDialog(42)
        self.assertTrue(dialog.windowFlags() & Qt.WindowType.FramelessWindowHint)
        self.assertFalse(dialog.mask().isEmpty())
        cancel = next(button for button in dialog.findChildren(QPushButton)
                      if button.text() == "Cancelar")
        self.assertLess(cancel.parentWidget().layout().indexOf(cancel),
                        dialog._ok.parentWidget().layout().indexOf(dialog._ok))
        self.assertEqual(dialog._ok.objectName(), "primaryButton")
        dialog.close()

    def test_zoom_and_pan_keep_selection_in_source_coordinates(self) -> None:
        with patch("tibiaenhanced.ui.dwm_windows.get_client_area",
                   return_value=SimpleNamespace(width=800, height=600)):
            dialog = DwmRegionDialog(42)
        dialog._set_zoom(2.0)
        view = dialog._view_region()
        self.assertEqual((view.x, view.y, view.width, view.height), (200, 150, 400, 300))
        dialog._on_overlay_selection(QRect(0, 0, dialog._display.width() // 2,
                                           dialog._display.height() // 2))
        selected = dialog.selection
        self.assertEqual((selected.x(), selected.y()), (200, 150))
        self.assertAlmostEqual(selected.width(), 200, delta=1)
        self.assertAlmostEqual(selected.height(), 150, delta=1)
        dialog._view_x = 400
        dialog._view_y = 300
        dialog._on_overlay_selection(QRect(0, 0, dialog._display.width(), dialog._display.height()))
        selected = dialog.selection
        self.assertEqual((selected.x(), selected.y(), selected.width(), selected.height()),
                         (400, 300, 400, 300))
        dialog.close()

    def test_mirror_context_menu_emits_requested_actions(self) -> None:
        window = DwmMirrorWindow(42, Region("Teste", 0, 0, 100, 100))
        received = []
        window.action_requested.connect(received.append)
        menu = window._context_menu()
        for action in menu.actions():
            if not action.isSeparator():
                action.trigger()
        self.assertEqual(received, ["hide", "lock", "delete"])
        opacity = []
        fit_modes = []
        window.opacity_requested.connect(opacity.append)
        window.fit_mode_requested.connect(fit_modes.append)
        slider = menu.findChild(QSlider, "mirrorOpacity")
        self.assertEqual(slider.value(), 100)
        slider.setValue(55)
        self.assertEqual(opacity, [55])
        fit_menu = next(action.menu() for action in menu.actions() if action.menu() is not None)
        self.assertEqual(window.fit_mode, "stretch")
        self.assertTrue(fit_menu.actions()[0].isChecked())
        fit_menu.actions()[1].trigger()
        self.assertEqual(fit_modes, ["contain"])
        window.close()


if __name__ == "__main__":
    unittest.main()
