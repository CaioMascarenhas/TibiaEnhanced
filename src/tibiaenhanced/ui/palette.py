"""Superfícies neutras e cores de ação compartilhadas pela interface."""

BACKGROUND = "#191c23"
SURFACE = "#232730"
SURFACE_HOVER = "#2b303b"
INPUT = "#1d2129"
ELEVATED = "#2c313c"
BORDER = "#363c49"
TEXT = "#edf0f5"
MUTED = "#cbd1dc"
ACCENT = "#86adf4"
ACCENT_HOVER = "#aac8ff"
ACCENT_LIGHT = "#bed3fa"
PRIMARY = "#365db4"
PRIMARY_HOVER = "#416bca"
TRACK = "#454d5e"


# Os aliases acima preservam a paleta escura usada por integrações existentes.
DARK = {
    "BACKGROUND": BACKGROUND, "SURFACE": SURFACE, "SURFACE_HOVER": SURFACE_HOVER,
    "INPUT": INPUT, "ELEVATED": ELEVATED, "BORDER": BORDER, "TEXT": TEXT,
    "MUTED": MUTED, "ACCENT": ACCENT, "ACCENT_HOVER": ACCENT_HOVER,
    "ACCENT_LIGHT": ACCENT_LIGHT, "PRIMARY": PRIMARY, "PRIMARY_HOVER": PRIMARY_HOVER,
    "TRACK": TRACK, "ICON": "#c5cfdf", "SIDEBAR": "#1e222a",
    "SELECTED": "#2c374c", "SELECTED_BORDER": "#3c506e",
    "CARD_HOVER": "#272c36", "HOVER_BORDER": "#66738a",
    "DISABLED_TEXT": "#8e98aa", "DISABLED_BACKGROUND": "#252a34",
    "DISABLED_BORDER": "#343b48", "PRIMARY_TEXT": "#ffffff",
    "PRIMARY_PRESSED": "#294c9a", "PRIMARY_DISABLED_TEXT": "#9cacc6",
    "PRIMARY_DISABLED_BACKGROUND": "#2b3952", "PRIMARY_DISABLED_BORDER": "#3b4961",
    "DANGER_TEXT": "#f4c6cd", "DANGER_BACKGROUND": "#392a32", "DANGER_BORDER": "#67424e",
    "DANGER_HOVER": "#50323e", "DANGER_HOVER_BORDER": "#9b6273",
    "ICON_HOVER": "#394354", "CLOSE_HOVER": "#9b3c4f", "SELECTION": "#344766",
    "SCROLLBAR": "#4b5364", "SCROLLBAR_HOVER": "#69778f",
    "SWITCH_THUMB": "#e5e7ec", "DISABLED_TRACK": "#343a46",
}

LIGHT = {
    "BACKGROUND": "#f3f5f9", "SURFACE": "#ffffff", "SURFACE_HOVER": "#edf2fa",
    "INPUT": "#f7f9fc", "ELEVATED": "#f0f3f8", "BORDER": "#d4dce8",
    "TEXT": "#202a3b", "MUTED": "#586579", "ACCENT": "#3569c1",
    "ACCENT_HOVER": "#2456aa", "ACCENT_LIGHT": "#275cab",
    "PRIMARY": "#335cb5", "PRIMARY_HOVER": "#274e9f", "TRACK": "#c8d2e1",
    "ICON": "#55647a", "SIDEBAR": "#e9eef6", "SELECTED": "#dce7fa",
    "SELECTED_BORDER": "#b5c9ed", "CARD_HOVER": "#f8faff", "HOVER_BORDER": "#98aac5",
    "DISABLED_TEXT": "#718099", "DISABLED_BACKGROUND": "#edf0f5", "DISABLED_BORDER": "#dce2ec",
    "PRIMARY_TEXT": "#ffffff", "PRIMARY_PRESSED": "#20468f",
    "PRIMARY_DISABLED_TEXT": "#687b9a", "PRIMARY_DISABLED_BACKGROUND": "#e1e8f5",
    "PRIMARY_DISABLED_BORDER": "#cbd5e6", "DANGER_TEXT": "#a1324b",
    "DANGER_BACKGROUND": "#fff1f4", "DANGER_BORDER": "#eac7d0",
    "DANGER_HOVER": "#ffe3eb", "DANGER_HOVER_BORDER": "#ce95a6",
    "ICON_HOVER": "#e0e8f5", "CLOSE_HOVER": "#ffe0e7", "SELECTION": "#dce7fa",
    "SCROLLBAR": "#c2cbd9", "SCROLLBAR_HOVER": "#9faec3",
    "SWITCH_THUMB": "#ffffff", "DISABLED_TRACK": "#dce2ec",
}


def palette_for(mode: str) -> dict[str, str]:
    if mode == "dark":
        return DARK
    if mode == "light":
        return LIGHT
    raise ValueError(f"Tema desconhecido: {mode}")


def current_palette() -> dict[str, str]:
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    return palette_for(app.property("themeMode") or "dark") if app else DARK
