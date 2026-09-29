"""Seleção de recorte em coordenadas da imagem."""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, Qt  # noqa: E402
from PySide6.QtGui import QImage  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from tibiaenhanced.ui.region_dialog import RegionDialog  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
