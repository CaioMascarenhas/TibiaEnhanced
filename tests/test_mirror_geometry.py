"""Verifica os dois modos explícitos de ajuste da miniatura DWM."""

import unittest

from tibiaenhanced.ui.dwm_windows import destination_rect


class MirrorGeometryTests(unittest.TestCase):
    def test_contain_centers_image_without_distortion(self) -> None:
        self.assertEqual(destination_rect((200, 100), (300, 300), "contain"),
                         (0, 75, 300, 150))
        self.assertEqual(destination_rect((100, 200), (300, 300), "contain"),
                         (75, 0, 150, 300))

    def test_stretch_fills_destination(self) -> None:
        self.assertEqual(destination_rect((200, 100), (300, 300), "stretch"),
                         (0, 0, 300, 300))

    def test_invalid_dimensions_and_mode_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            destination_rect((0, 100), (300, 300), "contain")
        with self.assertRaises(ValueError):
            destination_rect((200, 100), (300, 300), "crop")


if __name__ == "__main__":
    unittest.main()
