"""Tema compartilhado: hierarquia tipográfica, superfícies e estados dos controles."""

from .palette import palette_for


def app_stylesheet(heading_family: str = "Nunito", body_family: str = "Nunito", *, mode: str = "dark") -> str:
    return """
    QWidget {{ color: {TEXT}; font-family: "{body_family}"; font-size: 14px; font-weight: 400; }}
    QMainWindow {{ background: {BACKGROUND}; }}
    QWidget#appPage, QWidget#appWorkspace {{ background: {BACKGROUND}; }}
    QDialog, QMessageBox, QInputDialog {{ background: {SURFACE}; }}
    QLabel {{ background: transparent; }}
    QLabel#brandTitle, QLabel#pageTitle, QLabel#sectionTitle,
    QLabel#selectedTitle, QLabel#timerTitle, QLabel#timerCountdown,
    QLabel#dialogTitle, QLabel#emptyTitle {{ font-family: "{heading_family}"; font-weight: 600; }}
    QLabel#brandTitle {{ font-size: 17px; }}
    QLabel#pageTitle {{ font-size: 24px; }}
    QLabel#sectionTitle, QLabel#timerTitle, QLabel#selectedTitle {{ font-size: 16px; }}
    QLabel#timerCountdown {{ color: {TEXT}; font-size: 28px; }}
    QLabel#dialogTitle {{ font-size: 19px; }}
    QLabel#emptyTitle {{ color: {TEXT}; font-size: 18px; }}
    QLabel#mutedText, QLabel#pageDescription, QLabel#timerStatus,
    QLabel#timerShortcut {{ color: {MUTED}; font-size: 13px; font-weight: 500; }}
    QLabel#eyebrow {{ color: {MUTED}; font-size: 12px; font-weight: 600; }}
    QLabel#percentageLabel {{ color: {MUTED}; font-size: 13px; font-weight: 500; }}
    QLabel#stateBadge {{ font-size: 12px; font-weight: 600; padding: 6px 10px; }}
    QLabel#statusText {{ color: {MUTED}; font-size: 13px; padding: 6px 0; }}
    QLabel#brandIcon {{ background: transparent; border: 0; }}
    QLabel#emptyIcon {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 16px; }}
    QLabel#footerCredit {{ color: {MUTED}; font-size: 12px; }}

    QFrame#titleBar {{ background: {SURFACE}; border: 0; border-bottom: 1px solid {BORDER};
        border-top-left-radius: 11px; border-top-right-radius: 11px; }}
    QFrame#sidebar {{ background: {SIDEBAR}; border: 0; border-right: 1px solid {BORDER}; }}
    QLabel#navigationLabel {{ color: {MUTED}; font-size: 11px; font-weight: 600; padding: 4px 12px; }}
    QFrame#appearanceControls {{ background: transparent; border: 0; border-top: 1px solid {BORDER}; }}
    QLabel#appearanceLabel {{ color: {MUTED}; font-size: 11px; font-weight: 600; }}
    QPushButton#navigationButton {{ text-align: left; color: {MUTED}; background: transparent;
        border: 1px solid transparent; border-radius: 8px; padding: 9px 12px; min-height: 22px; }}
    QPushButton#navigationButton:hover {{ color: {TEXT}; background: {SURFACE_HOVER}; }}
    QPushButton#navigationButton:checked {{ color: {TEXT}; background: {SELECTED}; border-color: {SELECTED_BORDER}; }}
    QPushButton#navigationButton:focus {{ border-color: {ACCENT}; }}
    QFrame#profileControls {{ background: {INPUT}; border: 1px solid {BORDER}; border-radius: 8px; }}
    QLabel#profileLabel {{ color: {MUTED}; font-size: 12px; }}
    QFrame#profileDivider {{ background: {BORDER}; border: 0; }}
    QComboBox#profileSelector {{ background: transparent; border: 0; border-radius: 5px; padding: 3px 5px;
        min-height: 22px; font-size: 13px; }}
    QComboBox#profileSelector:hover, QComboBox#profileSelector:focus {{ background: {SURFACE_HOVER}; border: 0; }}

    QFrame#card, QFrame#timerCard {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 12px; }}
    QFrame#timerCard:hover {{ background: {CARD_HOVER}; border-color: {HOVER_BORDER}; }}
    QFrame#toolbar {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 10px; }}
    QFrame#emptyState {{ background: transparent; border: 0; }}
    QFrame#cardActions {{ background: {INPUT}; border: 0; border-radius: 8px; }}
    QFrame#dialogSurface {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 14px; }}
    QFrame#dialogBody, QFrame#dialogHeader {{ background: transparent; border: 0; }}

    QPushButton, QToolButton {{ color: {TEXT}; background: {ELEVATED}; font-size: 13px; font-weight: 600;
        border: 1px solid {BORDER}; border-radius: 8px; padding: 7px 12px; min-height: 20px; }}
    QPushButton:hover, QToolButton:hover {{ background: {SURFACE_HOVER}; border-color: {HOVER_BORDER}; }}
    QPushButton:pressed, QToolButton:pressed {{ background: {INPUT}; }}
    QPushButton:focus, QToolButton:focus {{ border-color: {ACCENT}; }}
    QPushButton:disabled, QToolButton:disabled {{ color: {DISABLED_TEXT}; background: {DISABLED_BACKGROUND}; border-color: {DISABLED_BORDER}; }}
    QPushButton#primaryButton {{ color: {PRIMARY_TEXT}; background: {PRIMARY}; border-color: {PRIMARY}; }}
    QPushButton#primaryButton:hover {{ background: {PRIMARY_HOVER}; border-color: {PRIMARY_HOVER}; }}
    QPushButton#primaryButton:pressed {{ background: {PRIMARY_PRESSED}; }}
    QPushButton#primaryButton:disabled {{ color: {PRIMARY_DISABLED_TEXT}; background: {PRIMARY_DISABLED_BACKGROUND}; border-color: {PRIMARY_DISABLED_BORDER}; }}
    QPushButton#dangerButton {{ color: {DANGER_TEXT}; background: {DANGER_BACKGROUND}; border-color: {DANGER_BORDER}; }}
    QPushButton#dangerButton:hover {{ background: {DANGER_HOVER}; border-color: {DANGER_HOVER_BORDER}; }}
    QPushButton#iconButton {{ background: transparent; border: 0; padding: 2px; min-height: 0; border-radius: 6px; }}
    QPushButton#iconButton:hover {{ background: {ICON_HOVER}; }}
    QPushButton#iconButton:focus {{ border: 1px solid {ACCENT}; }}
    QPushButton#chromeButton, QPushButton#chromeCloseButton {{ background: transparent; border: 0;
        border-radius: 6px; padding: 3px; min-height: 0; }}
    QPushButton#chromeButton:hover {{ background: {SURFACE_HOVER}; }}
    QPushButton#chromeCloseButton:hover {{ background: {CLOSE_HOVER}; }}

    QComboBox, QLineEdit, QSpinBox, QKeySequenceEdit {{ color: {TEXT}; background: {INPUT}; font-weight: 400;
        border: 1px solid {BORDER}; border-radius: 8px; padding: 7px 10px; min-height: 20px;
        selection-background-color: {PRIMARY}; selection-color: {PRIMARY_TEXT}; }}
    QSpinBox::up-button, QSpinBox::down-button {{ width: 0; border: 0; }}
    QComboBox:hover, QLineEdit:hover, QSpinBox:hover, QKeySequenceEdit:hover {{ border-color: {HOVER_BORDER}; }}
    QComboBox:focus, QLineEdit:focus, QSpinBox:focus, QKeySequenceEdit:focus {{ border-color: {ACCENT}; }}
    QComboBox:disabled, QLineEdit:disabled, QSpinBox:disabled {{ color: {DISABLED_TEXT}; background: {DISABLED_BACKGROUND}; }}
    QComboBox::drop-down {{ border: 0; width: 28px; }}
    QComboBox QAbstractItemView {{ color: {TEXT}; background: {SURFACE}; border: 1px solid {HOVER_BORDER};
        selection-background-color: {SELECTION}; selection-color: {TEXT}; padding: 5px; outline: 0; }}
    QCheckBox {{ color: {MUTED}; font-size: 13px; spacing: 8px; }}
    QCheckBox::indicator {{ width: 16px; height: 16px; background: {INPUT}; border: 1px solid {HOVER_BORDER}; border-radius: 4px; }}
    QCheckBox::indicator:hover {{ border-color: {ACCENT}; }}
    QCheckBox::indicator:checked {{ background: {PRIMARY}; border-color: {ACCENT}; }}
    QCheckBox#loopSwitch::indicator {{ width: 0; height: 0; border: 0; background: transparent; }}

    QSlider {{ background: transparent; min-height: 22px; max-height: 22px; }}
    QSlider::groove:horizontal {{ height: 4px; background: {TRACK}; border: 0; border-radius: 2px; }}
    QSlider::sub-page:horizontal {{ background: {ACCENT}; border: 0; border-radius: 2px; }}
    QSlider::add-page:horizontal {{ background: {TRACK}; border: 0; border-radius: 2px; }}
    QSlider::handle:horizontal {{ width: 10px; margin: -4px 0; border-radius: 6px; background: {ACCENT}; border: 1px solid {ACCENT_HOVER}; }}
    QSlider:disabled::handle:horizontal {{ background: {DISABLED_TEXT}; border-color: {DISABLED_TEXT}; }}

    QTreeWidget {{ color: {TEXT}; background: {INPUT}; border: 1px solid {BORDER}; border-radius: 10px; padding: 5px; outline: 0; }}
    QTreeWidget::item {{ min-height: 28px; padding: 4px 6px; border-radius: 5px; }}
    QTreeWidget::item:hover {{ background: {SURFACE_HOVER}; }}
    QTreeWidget::item:selected {{ color: {TEXT}; background: {SELECTION}; }}
    QHeaderView::section {{ color: {MUTED}; background: {SURFACE}; border: 0; border-bottom: 1px solid {BORDER};
        padding: 7px; font-size: 12px; font-weight: 600; }}
    QScrollArea#detailsScroll {{ background: transparent; border: 0; }}
    QScrollBar:vertical {{ width: 8px; background: transparent; margin: 2px 0; }}
    QScrollBar::handle:vertical {{ background: {SCROLLBAR}; border-radius: 4px; min-height: 30px; }}
    QScrollBar::handle:vertical:hover {{ background: {SCROLLBAR_HOVER}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
    QStatusBar {{ color: {MUTED}; background: transparent; border-top: 1px solid {BORDER}; font-size: 12px; }}
    QStatusBar::item {{ border: 0; }}
    QMenu {{ color: {TEXT}; background: {SURFACE}; border: 1px solid {HOVER_BORDER}; padding: 6px; }}
    QMenu::item {{ padding: 8px 26px; border-radius: 6px; }}
    QMenu::item:selected {{ background: {SELECTION}; }}
    QMenu::separator {{ height: 1px; background: {BORDER}; margin: 6px; }}
    QToolTip {{ color: {TEXT}; background: {ELEVATED}; border: 1px solid {HOVER_BORDER}; padding: 6px; }}
    """.format(heading_family=heading_family, body_family=body_family, **palette_for(mode))


APP_STYLESHEET = app_stylesheet()
