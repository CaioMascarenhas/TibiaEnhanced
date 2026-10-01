"""Interação real do mouse com o slider compartilhado por áudio e recortes."""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from tibiaenhanced.ui.design import CompactSlider
from tibiaenhanced.ui.theme import app_stylesheet


class SliderInteractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.slider = CompactSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(10, 110)
        self.slider.resize(210, 24)
        self.slider.show()
        self.addCleanup(self.slider.close)

    def point(self, fraction):
        start, end, _, _ = self.slider._track_geometry()
        return QPoint(round(start + (end - start) * fraction), self.slider.height() // 2)

    def move(self, point):
        event = QMouseEvent(QEvent.Type.MouseMove, QPointF(point), QPointF(point),
                            Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton,
                            Qt.KeyboardModifier.NoModifier)
        QApplication.sendEvent(self.slider, event)

    def test_click_jumps_to_pointer_instead_of_page_step(self):
        for fraction, expected in ((0.75, 85), (0.25, 35), (1, 110), (0, 10)):
            QTest.mouseClick(self.slider, Qt.MouseButton.LeftButton, pos=self.point(fraction))
            self.assertAlmostEqual(self.slider.value(), expected, delta=1)

    def test_press_drag_release_updates_live_and_clamps_outside(self):
        pressed, released, moved = [], [], []
        self.slider.sliderPressed.connect(lambda: pressed.append(True))
        self.slider.sliderReleased.connect(lambda: released.append(True))
        self.slider.sliderMoved.connect(moved.append)
        QTest.mousePress(self.slider, Qt.MouseButton.LeftButton, pos=self.point(0.5))
        self.assertAlmostEqual(self.slider.value(), 60, delta=1)
        self.move(self.point(0.8))
        self.assertAlmostEqual(self.slider.value(), 90, delta=1)
        self.move(QPoint(self.slider.width() + 50, 12))
        self.assertEqual(self.slider.value(), 110)
        QTest.mouseRelease(self.slider, Qt.MouseButton.LeftButton, pos=QPoint(-50, 12))
        self.assertEqual(self.slider.value(), 10)
        self.assertFalse(self.slider.isSliderDown())
        self.assertEqual((len(pressed), len(released)), (1, 1))
        self.assertTrue(moved)

    def test_handle_edge_does_not_jump_before_drag(self):
        self.slider.setValue(60)
        point = self.point(0.5) + QPoint(4, 0)
        QTest.mousePress(self.slider, Qt.MouseButton.LeftButton, pos=point)
        self.assertEqual(self.slider.value(), 60)
        self.move(point + QPoint(20, 0))
        self.assertGreater(self.slider.value(), 60)
        QTest.mouseRelease(self.slider, Qt.MouseButton.LeftButton, pos=point + QPoint(20, 0))

    def test_reversed_direction_uses_the_painted_track(self):
        for rtl, inverted in ((False, True), (True, False), (True, True)):
            self.slider.setLayoutDirection(Qt.LayoutDirection.RightToLeft if rtl
                                           else Qt.LayoutDirection.LeftToRight)
            self.slider.setInvertedAppearance(inverted)
            self.slider.setValue(60)
            QTest.mouseClick(self.slider, Qt.MouseButton.LeftButton, pos=self.point(0))
            self.assertEqual(self.slider.value(), 110 if rtl != inverted else 10)

    def test_tracking_off_commits_only_on_release(self):
        self.slider.setTracking(False)
        QTest.mousePress(self.slider, Qt.MouseButton.LeftButton, pos=self.point(0.5))
        self.move(self.point(0.75))
        self.assertEqual(self.slider.value(), 10)
        self.assertAlmostEqual(self.slider.sliderPosition(), 85, delta=1)
        QTest.mouseRelease(self.slider, Qt.MouseButton.LeftButton, pos=self.point(0.75))
        self.assertAlmostEqual(self.slider.value(), 85, delta=1)

    def test_disabled_and_keyboard_behavior(self):
        self.slider.setEnabled(False)
        QTest.mouseClick(self.slider, Qt.MouseButton.LeftButton, pos=self.point(1))
        self.assertEqual(self.slider.value(), 10)
        self.slider.setEnabled(True)
        QTest.keyClick(self.slider, Qt.Key.Key_Right)
        self.assertEqual(self.slider.value(), 11)


class StyledSliderInteractionTests(SliderInteractionTests):
    """Repete as interações com a geometria definida pelo tema real do app."""

    def setUp(self):
        super().setUp()
        self.slider.setStyleSheet(app_stylesheet())
        self.slider.ensurePolished()


if __name__ == "__main__":
    unittest.main()
