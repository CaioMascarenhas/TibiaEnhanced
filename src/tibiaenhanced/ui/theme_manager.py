"""Troca de tema compartilhada por janelas, controles Qt e desenhos personalizados."""

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from .palette import palette_for


class ThemeManager(QObject):
    changed = Signal(str)

    def __init__(self, app: QApplication) -> None:
        super().__init__(app)
        self.app = app

    @property
    def mode(self) -> str:
        return self.app.property("themeMode") or "dark"

    def apply(self, mode: str) -> None:
        from . import design
        from .theme import app_stylesheet
        colors = palette_for(mode)
        stylesheet = app_stylesheet(design.HEADING_FAMILY, design.BODY_FAMILY, mode=mode)
        if mode == self.mode and self.app.styleSheet() == stylesheet:
            return
        self.app.setProperty("themeMode", mode)
        palette = QPalette()
        for role, token in (
            (QPalette.ColorRole.Window, "BACKGROUND"),
            (QPalette.ColorRole.WindowText, "TEXT"),
            (QPalette.ColorRole.Base, "INPUT"),
            (QPalette.ColorRole.AlternateBase, "SURFACE"),
            (QPalette.ColorRole.Text, "TEXT"),
            (QPalette.ColorRole.Button, "ELEVATED"),
            (QPalette.ColorRole.ButtonText, "TEXT"),
            (QPalette.ColorRole.ToolTipBase, "ELEVATED"),
            (QPalette.ColorRole.ToolTipText, "TEXT"),
            (QPalette.ColorRole.Highlight, "PRIMARY"),
            (QPalette.ColorRole.HighlightedText, "PRIMARY_TEXT"),
            (QPalette.ColorRole.PlaceholderText, "MUTED"),
        ):
            palette.setColor(role, QColor(colors[token]))
        for role in (QPalette.ColorRole.WindowText, QPalette.ColorRole.Text, QPalette.ColorRole.ButtonText):
            palette.setColor(QPalette.ColorGroup.Disabled, role, QColor(colors["DISABLED_TEXT"]))
        self.app.setPalette(palette)
        self.app.setStyleSheet(stylesheet)
        for widget in self.app.allWidgets():
            design.refresh_icon(widget)
            refresh = getattr(widget, "_refresh_theme", None)
            if refresh is not None:
                refresh()
            widget.update()
        self.changed.emit(mode)


def theme_manager() -> ThemeManager:
    app = QApplication.instance()
    if not hasattr(app, "_theme_manager"):
        app._theme_manager = ThemeManager(app)
    return app._theme_manager
