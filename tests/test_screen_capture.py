"""Geometria e detecção de falha da captura, sem acessar janelas de terceiros."""

import unittest
from unittest.mock import patch

from tibiaenhanced.models import Region
from tibiaenhanced.services.screen_capture import Frame, _capture_box, frame_is_blank
from tibiaenhanced.services.windowing import ClientArea
from tibiaenhanced.services.windowing import require_capturable_window


class ScreenCaptureTests(unittest.TestCase):
    def test_region_follows_client_position(self) -> None:
        region = Region("teste", 12, 18, 80, 60)
        with patch(
            "tibiaenhanced.services.screen_capture.get_client_area",
            side_effect=[ClientArea(100, 200, 300, 200), ClientArea(-400, 20, 300, 200)],
        ):
            self.assertEqual(_capture_box(123, region), {"left": 112, "top": 218, "width": 80, "height": 60})
            self.assertEqual(_capture_box(123, region), {"left": -388, "top": 38, "width": 80, "height": 60})

    def test_region_rejects_smaller_window(self) -> None:
        with patch("tibiaenhanced.services.screen_capture.get_client_area", return_value=ClientArea(0, 0, 40, 40)):
            with self.assertRaisesRegex(RuntimeError, "não cabe mais"):
                _capture_box(123, Region("teste", 20, 20, 30, 30))

    def test_blank_frame_is_distinguished_from_colored_frame(self) -> None:
        self.assertTrue(frame_is_blank(Frame(bytes(4 * 16), 4, 4, 0)))
        colored = bytes([0, 0, 255, 0] * 16)
        self.assertFalse(frame_is_blank(Frame(colored, 4, 4, 0)))

    def test_declared_capture_restriction_is_respected(self) -> None:
        for value in (0x1, 0x11):
            with self.subTest(value=value), patch(
                "tibiaenhanced.services.windowing.get_display_affinity", return_value=value
            ):
                with self.assertRaisesRegex(RuntimeError, "restrição de captura"):
                    require_capturable_window(123)
        with patch("tibiaenhanced.services.windowing.get_display_affinity", return_value=0):
            require_capturable_window(123)


if __name__ == "__main__":
    unittest.main()
