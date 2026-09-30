"""Tema escuro e compacto da interface de controle."""


def app_stylesheet(heading_family: str = "Exo", body_family: str = "Quicksand") -> str:
    return f"""
    QWidget {{ color: #eaf2fc; font-family: "{body_family}"; font-size: 10pt; }}
    QMainWindow {{ background: transparent; }}
    QWidget#appPage {{ background: #0e1727; }}
    QDialog, QMessageBox, QInputDialog {{ background: #111b2b; }}
    QLabel {{ background: transparent; }}

    QLabel#brandTitle, QLabel#pageTitle, QLabel#sectionTitle,
    QLabel#selectedTitle, QLabel#timerTitle, QLabel#timerCountdown {{
        font-family: "{heading_family}"; font-weight: 900;
    }}
    QLabel#brandTitle {{ color: #f4f8ff; font-size: 16pt; }}
    QLabel#brandSubtitle {{ color: #83a1be; font-size: 8pt; letter-spacing: 1px; }}
    QLabel#pageTitle {{ color: #f4f8ff; font-size: 19pt; }}
    QLabel#sectionTitle {{ color: #e9f1ff; font-size: 11pt; }}
    QLabel#selectedTitle {{ color: #ffffff; font-size: 15pt; }}
    QLabel#timerTitle {{ color: #f5f8ff; font-size: 12pt; }}
    QLabel#timerCountdown {{ color: #f3c97b; font-size: 21pt; }}
    QLabel#mutedText, QLabel#eyebrow {{ color: #9ab0c8; }}
    QLabel#eyebrow {{ font-size: 8pt; font-weight: 700; padding-top: 4px; }}
    QLabel#stateBadge {{ font-size: 8pt; font-weight: 700; padding: 5px 9px; }}
    QLabel#statusText {{
        color: #b5cbe1; background: #142338;
        border: 1px solid #29415b; border-radius: 9px; padding: 6px 10px;
    }}
    QLabel#timerArt {{ background: #102036; border: 1px solid #30455e; border-radius: 10px; }}
    QLabel#brandIcon {{ background: #153354; border: 1px solid #2b668c; border-radius: 10px; }}

    QFrame#card, QFrame#timerCard {{
        background: #172338; border: 1px solid #2b3c53; border-radius: 14px;
    }}
    QFrame#timerCard {{ border-left: 3px solid #d9aa64; }}
    QFrame#titleBar {{ background: transparent; border: 0; }}

    QPushButton, QToolButton {{
        color: #e8f1fd; background: #233249;
        border: 1px solid #344760; border-radius: 9px;
        padding: 5px 10px; min-height: 22px;
    }}
    QPushButton:hover, QToolButton:hover {{ background: #30445f; border-color: #537395; }}
    QPushButton:pressed, QToolButton:pressed {{ background: #18283e; }}
    QPushButton:focus, QToolButton:focus {{ border: 2px solid #6bd4f3; }}
    QPushButton:disabled, QToolButton:disabled {{
        color: #788da5; background: #1a283b; border-color: #2b3a4e;
    }}
    QPushButton#primaryButton {{
        color: #092035; background: #74d4ed; border-color: #91e4f5; font-weight: 700;
    }}
    QPushButton#primaryButton:hover {{ background: #9be8f8; }}
    QPushButton#primaryButton:disabled {{ color: #637a89; background: #2c5868; border-color: #3b6a78; }}
    QPushButton#dangerButton {{ color: #ffc6cb; background: #382635; border-color: #704352; }}
    QPushButton#dangerButton:hover {{ background: #573241; border-color: #a95a69; }}
    QPushButton#chromeButton, QPushButton#chromeCloseButton {{
        background: transparent; border: 0; border-radius: 8px; padding: 3px; min-height: 0;
    }}
    QPushButton#chromeButton:hover {{ background: #253750; }}
    QPushButton#chromeCloseButton:hover {{ background: #a53848; }}

    QComboBox, QLineEdit, QSpinBox, QKeySequenceEdit {{
        color: #f1f6ff; background: #0f1a2b;
        border: 1px solid #34475e; border-radius: 9px;
        padding: 5px 9px; min-height: 22px;
        selection-background-color: #287497;
    }}
    QComboBox:hover, QLineEdit:hover, QSpinBox:hover, QKeySequenceEdit:hover {{ border-color: #56718d; }}
    QComboBox:focus, QLineEdit:focus, QSpinBox:focus, QKeySequenceEdit:focus {{ border: 2px solid #68cce9; }}
    QComboBox:disabled, QLineEdit:disabled, QSpinBox:disabled {{ color: #7d90a6; background: #182536; }}
    QComboBox::drop-down {{ border: 0; width: 25px; }}
    QComboBox QAbstractItemView {{
        color: #eef5ff; background: #17243a; border: 1px solid #405672;
        selection-background-color: #275676; padding: 4px;
    }}
    QCheckBox {{ color: #d9e6f5; spacing: 8px; }}
    QCheckBox::indicator {{
        width: 16px; height: 16px; background: #101c2d;
        border: 1px solid #52708b; border-radius: 5px;
    }}
    QCheckBox::indicator:hover {{ border-color: #78d5ed; }}
    QCheckBox::indicator:checked {{ background: #70cee9; border-color: #9be9f8; }}

    QSlider::groove:horizontal {{ height: 7px; background: #31465d; border-radius: 4px; }}
    QSlider::sub-page:horizontal {{ background: #65cbe9; border-radius: 4px; }}
    QSlider::handle:horizontal {{
        width: 16px; margin: -6px 0; border-radius: 8px;
        background: #f2fbff; border: 2px solid #6bd4f3;
    }}
    QSlider::handle:horizontal:hover {{ background: #ffffff; border-color: #a6efff; }}
    QSlider:disabled::sub-page:horizontal {{ background: #3b6475; }}
    QSlider:disabled::handle:horizontal {{ background: #72889a; border-color: #72889a; }}

    QTreeWidget {{
        color: #e4effb; background: #111d2f;
        border: 1px solid #2c4058; border-radius: 10px; padding: 4px; outline: 0;
    }}
    QTreeWidget::item {{ min-height: 25px; padding: 3px 5px; border-radius: 5px; }}
    QTreeWidget::item:hover {{ background: #21344d; }}
    QTreeWidget::item:selected {{ color: #ffffff; background: #2a526e; }}
    QHeaderView::section {{
        color: #8faac4; background: #172338; border: 0;
        border-bottom: 1px solid #30445a; padding: 5px 7px; font-size: 8pt; font-weight: 700;
    }}
    QScrollArea#detailsScroll {{ background: transparent; border: 0; }}
    QScrollBar:vertical {{ width: 8px; background: transparent; margin: 3px 0; }}
    QScrollBar::handle:vertical {{ background: #48617b; border-radius: 4px; min-height: 26px; }}
    QScrollBar::handle:vertical:hover {{ background: #6f91b2; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

    QTabWidget::pane {{ border: 0; background: #0e1727; }}
    QTabBar {{ background: #0e1727; }}
    QTabBar::tab {{
        color: #a8bdd3; background: #172439;
        border: 1px solid #283b52; border-radius: 9px;
        padding: 7px 15px; margin: 4px 3px 6px 3px; min-width: 100px;
    }}
    QTabBar::tab:hover {{ background: #263b55; color: #f1f7ff; }}
    QTabBar::tab:selected {{ color: #092137; background: #77d2eb; border-color: #a1e8f7; font-weight: 700; }}
    QTabBar::tab:focus {{ border: 2px solid #a1e8f7; }}
    QStatusBar {{ color: #8fa6bd; background: transparent; border-top: 1px solid #263a50; font-size: 8pt; }}
    QStatusBar::item {{ border: 0; }}
    QMenu {{ color: #eaf3ff; background: #17243a; border: 1px solid #405672; padding: 5px; }}
    QMenu::item {{ padding: 7px 24px; border-radius: 6px; }}
    QMenu::item:selected {{ background: #2a526e; }}
    QToolTip {{ color: #eff7ff; background: #22364d; border: 1px solid #54708d; padding: 5px; }}
    """


APP_STYLESHEET = app_stylesheet()
