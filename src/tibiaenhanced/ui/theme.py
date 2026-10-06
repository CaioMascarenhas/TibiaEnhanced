"""Tema escuro e compacto da interface de controle."""

from .palette import (ACCENT, ACCENT_HOVER, ACCENT_LIGHT, BACKGROUND,
                      BORDER, ELEVATED, INPUT, MUTED, PRIMARY,
                      PRIMARY_HOVER, SURFACE, SURFACE_HOVER, TEXT, TRACK)


def app_stylesheet(heading_family: str = "Segoe UI", body_family: str = "Segoe UI") -> str:
    return f"""
    QWidget {{ color: {TEXT}; font-family: "{body_family}"; font-size: 11pt; font-weight: 400; }}
    QMainWindow {{ background: transparent; }}
    QWidget#appPage {{ background: {BACKGROUND}; }}
    QDialog, QMessageBox, QInputDialog {{ background: {INPUT}; }}
    QLabel {{ background: transparent; }}

    QLabel#brandTitle, QLabel#pageTitle, QLabel#sectionTitle,
    QLabel#selectedTitle, QLabel#timerTitle, QLabel#timerCountdown {{
        font-family: "{heading_family}"; font-weight: 600;
    }}
    QLabel#brandTitle {{ color: {TEXT}; font-size: 13pt; }}
    QLabel#brandSubtitle {{ color: #83a1be; font-size: 10pt; letter-spacing: 1px; }}
    QLabel#pageTitle {{ color: {TEXT}; font-size: 13pt; }}
    QLabel#sectionTitle {{ color: {TEXT}; font-size: 11pt; }}
    QLabel#selectedTitle {{ color: {TEXT}; font-size: 11pt; }}
    QLabel#timerTitle {{ color: {TEXT}; font-size: 11pt; }}
    QLabel#timerCountdown {{ color: {ACCENT_LIGHT}; font-size: 18pt; }}
    QLabel#mutedText, QLabel#eyebrow {{ color: {MUTED}; font-weight: 400; }}
    QLabel#eyebrow {{ font-size: 10pt; font-weight: 600; padding-top: 4px; }}
    QLabel#stateBadge {{ font-size: 10pt; font-weight: 600; padding: 5px 9px; }}
    QLabel#statusText {{
        color: {MUTED}; background: {BACKGROUND};
        border: 1px solid {BACKGROUND}; border-radius: 9px; padding: 6px 10px;
    }}
    QLabel#timerArt {{ background: #213033; border: 1px solid {BORDER}; border-radius: 10px; }}
    QLabel#brandIcon {{ background: #263234; border: 1px solid {BORDER}; border-radius: 10px; }}

    QFrame#card, QFrame#timerCard {{
        background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 10px;
    }}
    QFrame#timerCard {{ border-left: 3px solid {ACCENT}; }}
    QFrame#timerCard:hover {{ background: {SURFACE_HOVER}; border-color: #4b7972; border-left-color: {ACCENT_HOVER}; }}
    QFrame#dialogSurface {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 14px; }}
    QFrame#dialogBody, QFrame#dialogHeader {{ background: transparent; border: 0; }}
    QLabel#dialogTitle {{ color: {TEXT}; font-family: "{heading_family}"; font-size: 13pt; font-weight: 600; }}
    QLabel#footerCredit {{ color: #a7b9b5; font-size: 10pt; }}
    QPushButton#iconButton {{ background: transparent; border: 0; padding: 2px; min-height: 0; border-radius: 5px; }}
    QPushButton#iconButton:hover {{ background: #35494a; }}
    QFrame#titleBar {{ background: transparent; border: 0; }}
    QFrame#profileControls {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 10px; }}
    QLabel#profileLabel {{ color: {MUTED}; font-size: 10pt; font-weight: 600; }}
    QFrame#profileDivider {{ background: {BORDER}; border: 0; }}
    QComboBox#profileSelector {{ background: transparent; border: 0; border-radius: 6px; padding: 3px 4px; }}
    QComboBox#profileSelector:hover {{ background: {SURFACE_HOVER}; }}
    QComboBox#profileSelector:focus {{ background: {SURFACE_HOVER}; border: 0; }}

    QPushButton, QToolButton {{
        color: {TEXT}; background: {ELEVATED}; font-weight: 600;
        border: 1px solid {BORDER}; border-radius: 9px;
        padding: 5px 10px; min-height: 24px;
    }}
    QPushButton:hover, QToolButton:hover {{ background: {SURFACE_HOVER}; border-color: #66827e; }}
    QPushButton:pressed, QToolButton:pressed {{ background: #292c36; }}
    QPushButton:focus, QToolButton:focus {{ border: 1px solid {ACCENT_HOVER}; }}
    QPushButton:disabled, QToolButton:disabled {{
        color: #788da5; background: #1a283b; border-color: #2b3a4e;
    }}
    QPushButton#primaryButton {{
        color: {TEXT}; background: {PRIMARY}; border-color: {ACCENT}; font-weight: 600;
    }}
    QPushButton#primaryButton:hover {{ background: {PRIMARY_HOVER}; border-color: {ACCENT_LIGHT}; }}
    QPushButton#primaryButton:disabled {{ color: #91a6c0; background: #2d514e; border-color: #3c6964; }}
    QPushButton#dangerButton {{ color: {TEXT}; background: #4e2935; border-color: #ad6675; }}
    QPushButton#dangerButton:hover {{ background: #573241; border-color: #a95a69; }}
    QPushButton#chromeButton, QPushButton#chromeCloseButton {{
        background: transparent; border: 0; border-radius: 8px; padding: 3px; min-height: 0;
    }}
    QPushButton#chromeButton:hover {{ background: #2e4648; }}
    QPushButton#chromeCloseButton:hover {{ background: #a53848; }}

    QComboBox, QLineEdit, QSpinBox, QKeySequenceEdit {{
        color: #f1f6ff; background: {INPUT};
        border: 1px solid {BORDER}; border-radius: 9px;
        padding: 5px 10px; min-height: 24px;
        selection-background-color: #277c70;
    }}
    QComboBox, QLineEdit, QSpinBox, QKeySequenceEdit {{ font-weight: 400; }}
    QSpinBox::up-button, QSpinBox::down-button {{ width: 0; border: 0; }}
    QComboBox:hover, QLineEdit:hover, QSpinBox:hover, QKeySequenceEdit:hover {{ border-color: #63817c; }}
    QComboBox:focus, QLineEdit:focus, QSpinBox:focus, QKeySequenceEdit:focus {{ border: 1px solid {ACCENT_HOVER}; }}
    QComboBox:disabled, QLineEdit:disabled, QSpinBox:disabled {{ color: #92aaa4; background: #233133; }}
    QComboBox::drop-down {{ border: 0; width: 25px; }}
    QComboBox QAbstractItemView {{
        color: #eef5ff; background: #213033; border: 1px solid #49615f;
        selection-background-color: #285f59; padding: 4px;
    }}
    QCheckBox {{ color: {TEXT}; spacing: 8px; }}
    QCheckBox::indicator {{
        width: 16px; height: 16px; background: {INPUT};
        border: 1px solid #5a7772; border-radius: 5px;
    }}
    QCheckBox::indicator:hover {{ border-color: {ACCENT_HOVER}; }}
    QCheckBox::indicator:checked {{ background: {PRIMARY}; border-color: {ACCENT_HOVER}; }}
    QCheckBox#loopSwitch::indicator {{ width: 0; height: 0; border: 0; background: transparent; }}

    QSlider {{ background: transparent; min-height: 16px; max-height: 16px; }}
    QSlider::groove:horizontal {{ height: 4px; background: {TRACK}; border: 0; border-radius: 2px; }}
    QSlider::sub-page:horizontal {{ background: {ACCENT}; border: 0; border-radius: 2px; margin: 6px 0; }}
    QSlider::add-page:horizontal {{ background: {TRACK}; border: 0; border-radius: 2px; margin: 6px 0; }}
    QSlider::handle:horizontal {{
        width: 10px; margin: -4px 0; border-radius: 6px;
        background: {ACCENT}; border: 1px solid {ACCENT_HOVER};
    }}
    QSlider::handle:horizontal:hover {{ background: {TEXT}; border-color: {ACCENT_LIGHT}; }}
    QSlider:disabled::sub-page:horizontal {{ background: #4c7069; }}
    QSlider:disabled::handle:horizontal {{ background: #829b95; border-color: #829b95; }}

    QTreeWidget {{
        color: {TEXT}; background: #252838;
        border: 1px solid {BORDER}; border-radius: 10px; padding: 4px; outline: 0;
    }}
    QTreeWidget::item {{ min-height: 25px; padding: 3px 5px; border-radius: 5px; }}
    QTreeWidget::item:hover {{ background: #2d4343; }}
    QTreeWidget::item:selected {{ color: {TEXT}; background: #2a5e56; }}
    QHeaderView::section {{
        color: {MUTED}; background: {SURFACE}; border: 0;
        border-bottom: 1px solid {BORDER}; padding: 5px 7px; font-size: 10pt; font-weight: 600;
    }}
    QScrollArea#detailsScroll {{ background: transparent; border: 0; }}
    QScrollBar:vertical {{ width: 8px; background: transparent; margin: 3px 0; }}
    QScrollBar::handle:vertical {{ background: #58706c; border-radius: 4px; min-height: 26px; }}
    QScrollBar::handle:vertical:hover {{ background: #759c94; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

    QTabWidget::pane {{ border: 0; background: {BACKGROUND}; }}
    QTabBar {{ background: {BACKGROUND}; }}
    QTabBar::tab {{
        color: {TEXT}; background: #1e292c;
        border: 1px solid {BORDER}; border-radius: 9px;
        padding: 7px 12px; margin: 2px 3px 3px 3px; min-width: 68px;
    }}
    QTabBar::tab:hover {{ background: #2e4648; color: {TEXT}; }}
    QTabBar::tab:selected {{ color: #d5f5eb; background: #1e403c; border-color: {ACCENT}; font-weight: 600; }}
    QTabBar::tab:focus {{ border: 1px solid {ACCENT_HOVER}; }}
    QStatusBar {{ color: #a7b9b5; background: transparent; border-top: 1px solid {BORDER}; font-size: 10pt; }}
    QStatusBar::item {{ border: 0; }}
    QMenu {{ color: {TEXT}; background: #213033; border: 1px solid #49615f; padding: 5px; }}
    QMenu::item {{ padding: 7px 24px; border-radius: 6px; }}
    QMenu::item:selected {{ background: #2a5e56; }}
    QToolTip {{ color: {TEXT}; background: #263c3d; border: 1px solid #5c7d76; padding: 5px; }}
    """


APP_STYLESHEET = app_stylesheet()
