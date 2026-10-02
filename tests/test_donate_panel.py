"""Dados de doação e conteúdo copiado para a área de transferência."""

import binascii
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402
from tibiaenhanced.ui.donate_panel import (CHARACTER, PIX_KEY, PIX_PAYLOAD,
                                         DonatePanel)  # noqa: E402


class DonatePanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_copy_actions_use_exact_donation_details(self) -> None:
        panel = DonatePanel()
        for button, expected in ((panel.copy_character_button, CHARACTER),
                                 (panel.copy_pix_button, PIX_KEY),
                                 (panel.copy_code_button, PIX_PAYLOAD)):
            button.click()
            self.assertEqual(self.app.clipboard().text(), expected)
            self.assertEqual(button.text(), "Copiado!")
        self.assertFalse(panel.qr_label.pixmap().isNull())
        self.assertEqual(f"{binascii.crc_hqx(PIX_PAYLOAD[:-4].encode(), 0xffff):04X}",
                         PIX_PAYLOAD[-4:])
        self.assertIn(PIX_KEY, PIX_PAYLOAD)
        panel.close()
