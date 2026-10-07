"""Fluxos das ferramentas, clipboard e seletor compacto de tema."""

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication
from tibiaenhanced.ui.design import ThemeSwitch, load_fonts
from tibiaenhanced.ui.main_window import MainWindow
from tibiaenhanced.ui.theme_manager import theme_manager
from test_game_tools import SAMPLE


class ToolsPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        load_fonts()

    def setUp(self):
        theme_manager().apply("dark")
        with patch("tibiaenhanced.ui.capture_panel.list_windows", return_value=[]):
            self.window = MainWindow()
        self.window.show()
        self.window.navigation_buttons[2].click()
        self.tools = self.window.tools_panel
        self.app.processEvents()
        self.addCleanup(self.window.exit_app)
        self.addCleanup(theme_manager().apply, "dark")

    def test_calculate_copy_invalidate_and_switch_tools_preserve_input(self):
        panel = self.tools.loot_split
        panel.log_input.setPlainText(SAMPLE)
        panel.calculate_button.click()
        self.app.processEvents()
        self.assertIsNotNone(panel.result)
        self.app.processEvents()
        summary = panel.result_layout.itemAt(0).widget()
        top = summary.mapTo(self.tools.scroll.viewport(), QPoint(0, 0)).y()
        self.assertGreaterEqual(top, 0)
        self.assertLessEqual(top, 24)
        self.assertEqual(len(panel.transfer_copy_buttons), 2)
        panel.transfer_copy_buttons[0].click()
        self.assertEqual(QApplication.clipboard().text(), "transfer 327375 to Kandin")
        panel.copy_result_button.click()
        self.assertIn("transfer 139014 to Kandin", QApplication.clipboard().text())
        self.assertIn("Kandin - 43.6%", QApplication.clipboard().text())
        self.tools.tool_buttons[1].click()
        self.tools.exp_share.level_input.setValue(200)
        self.assertEqual(self.tools.exp_share.range_label.text(), "133 – 301")
        self.tools.exp_share.level_input.setValue(300)
        self.assertEqual(self.tools.exp_share.range_label.text(), "200 – 451")
        self.tools.tool_buttons[0].click()
        self.assertEqual(panel.log_input.toPlainText(), SAMPLE)
        self.assertIsNotNone(panel.result)
        panel.log_input.setPlainText("Incomplete\nLoot: 100")
        self.assertIsNone(panel.result)
        self.assertTrue(panel.results.isHidden())
        panel.calculate_button.click()
        self.assertTrue(panel.error_label.isVisible())
        self.assertIn("incompleto", panel.error_label.text())

    def test_tools_fit_minimum_window_in_both_themes_and_rashid_is_animated(self):
        self.assertTrue(self.tools.rashid_movie.isValid())
        self.assertGreater(self.tools.rashid_movie.frameCount(), 1)
        self.assertIn(self.tools._rashid_stop.city, self.tools.rashid_title.text())
        self.tools.loot_split.log_input.setPlainText(SAMPLE)
        self.tools.loot_split.calculate()
        for theme in ("dark", "light"):
            theme_manager().apply(theme)
            for width, height in ((940, 600), (800, 500)):
                self.window.resize(width, height)
                heights = []
                for index in (0, 1):
                    self.tools.tool_buttons[index].click()
                    self.app.processEvents()
                    self.assertEqual(self.tools.scroll.horizontalScrollBar().maximum(), 0)
                    self.assertLessEqual(self.tools.tool_pages.minimumSizeHint().width(),
                                         self.tools.scroll.viewport().width())
                    heights.append(self.tools.scroll.widget().height())
                self.assertLess(heights[1], heights[0])

    def test_theme_switch_updates_state_and_accessible_name_without_losing_results(self):
        panel = self.tools.loot_split
        panel.log_input.setPlainText(SAMPLE)
        panel.calculate()
        result = panel.result
        switch = self.window.theme_switch
        self.assertIsInstance(switch, ThemeSwitch)
        self.assertEqual(switch.text(), "")
        switch.click()
        self.assertEqual(theme_manager().mode, "light")
        self.assertEqual(switch.text(), "")
        self.assertEqual(switch.accessibleName(), "Tema claro")
        self.assertEqual(switch.toolTip(), "Ativar tema escuro")
        switch._animation.setCurrentTime(switch._animation.duration())
        self.assertEqual(switch._position, 0.0)
        self.assertIs(panel.result, result)
        self.assertIs(self.window.pages.currentWidget(), self.tools)
        theme_manager().apply("dark")
        switch._animation.setCurrentTime(switch._animation.duration())
        self.assertTrue(switch.isChecked())
        self.assertEqual(switch._position, 1.0)
        self.assertEqual(switch.text(), "")


if __name__ == "__main__":
    unittest.main()
