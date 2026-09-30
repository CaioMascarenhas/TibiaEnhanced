"""Tema escuro e compacto da interface de controle."""


def app_stylesheet(heading_family: str = "Exo", body_family: str = "Inter") -> str:
    return f"""
    QWidget {{ color: #eaf2fc; font-family: "{body_family}"; font-size: 9pt; }}
    QMainWindow {{ background: transparent; }}
    QWidget#appPage {{ background: #1b1e24; }}
    QDialog, QMessageBox, QInputDialog {{ background: #202329; }}
    QLabel {{ background: transparent; }}

    QLabel#brandTitle, QLabel#pageTitle, QLabel#sectionTitle,
    QLabel#selectedTitle, QLabel#timerTitle, QLabel#timerCountdown {{
        font-family: "{heading_family}"; font-weight: 900;
    }}
    QLabel#brandTitle {{ color: #f4f8ff; font-size: 13pt; }}
    QLabel#brandSubtitle {{ color: #83a1be; font-size: 8pt; letter-spacing: 1px; }}
    QLabel#pageTitle {{ color: #f4f8ff; font-size: 13pt; }}
    QLabel#sectionTitle {{ color: #e9f1ff; font-size: 11pt; }}
    QLabel#selectedTitle {{ color: #ffffff; font-size: 11pt; }}
    QLabel#timerTitle {{ color: #f5f8ff; font-size: 11pt; }}
    QLabel#timerCountdown {{ color: #ffb454; font-size: 18pt; }}
    QLabel#mutedText, QLabel#eyebrow {{ color: #9a9eae; }}
    QLabel#eyebrow {{ font-size: 8pt; font-weight: 700; padding-top: 4px; }}
    QLabel#stateBadge {{ font-size: 8pt; font-weight: 700; padding: 5px 9px; }}
    QLabel#statusText {{
        color: #9296a4; background: #1b1e24;
        border: 1px solid #1b1e24; border-radius: 9px; padding: 6px 10px;
    }}
    QLabel#timerArt {{ background: #252839; border: 1px solid #35384a; border-radius: 10px; }}
    QLabel#brandIcon {{ background: #292c34; border: 1px solid #383b45; border-radius: 10px; }}

    QFrame#card, QFrame#timerCard {{
        background: #292c40; border: 1px solid #34374a; border-radius: 10px;
    }}
    QFrame#timerCard {{ border-left: 3px solid #ff940d; }}
    QLabel#footerCredit {{ color: #969aa6; font-size: 8pt; }}
    QPushButton#iconButton {{ background: transparent; border: 0; padding: 2px; min-height: 0; border-radius: 5px; }}
    QPushButton#iconButton:hover {{ background: #45485a; }}
    QFrame#titleBar {{ background: transparent; border: 0; }}

    QPushButton, QToolButton {{
        color: #e8f1fd; background: #30333e;
        border: 1px solid #41444f; border-radius: 9px;
        padding: 3px 8px; min-height: 18px;
    }}
    QPushButton:hover, QToolButton:hover {{ background: #3d404d; border-color: #666978; }}
    QPushButton:pressed, QToolButton:pressed {{ background: #292c36; }}
    QPushButton:focus, QToolButton:focus {{ border: 1px solid #ff940d; }}
    QPushButton:disabled, QToolButton:disabled {{
        color: #788da5; background: #1a283b; border-color: #2b3a4e;
    }}
    QPushButton#primaryButton {{
        color: #21180d; background: #ff940d; border-color: #ffad40; font-weight: 700;
    }}
    QPushButton#primaryButton:hover {{ background: #ffac3d; }}
    QPushButton#primaryButton:disabled {{ color: #637a89; background: #2c5868; border-color: #3b6a78; }}
    QPushButton#dangerButton {{ color: #ffc6cb; background: #382635; border-color: #704352; }}
    QPushButton#dangerButton:hover {{ background: #573241; border-color: #a95a69; }}
    QPushButton#chromeButton, QPushButton#chromeCloseButton {{
        background: transparent; border: 0; border-radius: 8px; padding: 3px; min-height: 0;
    }}
    QPushButton#chromeButton:hover {{ background: #253750; }}
    QPushButton#chromeCloseButton:hover {{ background: #a53848; }}

    QComboBox, QLineEdit, QSpinBox, QKeySequenceEdit {{
        color: #f1f6ff; background: #20232b;
        border: 1px solid #3c3f4b; border-radius: 9px;
        padding: 3px 8px; min-height: 18px;
        selection-background-color: #287497;
    }}
    QComboBox:hover, QLineEdit:hover, QSpinBox:hover, QKeySequenceEdit:hover {{ border-color: #56718d; }}
    QComboBox:focus, QLineEdit:focus, QSpinBox:focus, QKeySequenceEdit:focus {{ border: 1px solid #ff940d; }}
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
    QCheckBox::indicator:hover {{ border-color: #ff940d; }}
    QCheckBox::indicator:checked {{ background: #ff940d; border-color: #ffad40; }}

    QSlider {{ background: transparent; min-height: 16px; max-height: 16px; }}
    QSlider::groove:horizontal {{ height: 4px; background: #484b59; border: 0; border-radius: 2px; }}
    QSlider::sub-page:horizontal {{ background: #ff940d; border: 0; border-radius: 2px; margin: 6px 0; }}
    QSlider::add-page:horizontal {{ background: #484b59; border: 0; border-radius: 2px; margin: 6px 0; }}
    QSlider::handle:horizontal {{
        width: 10px; margin: -4px 0; border-radius: 6px;
        background: #ff9b23; border: 1px solid #ff940d;
    }}
    QSlider::handle:horizontal:hover {{ background: #ffffff; border-color: #a6efff; }}
    QSlider:disabled::sub-page:horizontal {{ background: #3b6475; }}
    QSlider:disabled::handle:horizontal {{ background: #72889a; border-color: #72889a; }}

    QTreeWidget {{
        color: #e4effb; background: #252838;
        border: 1px solid #2c4058; border-radius: 10px; padding: 4px; outline: 0;
    }}
    QTreeWidget::item {{ min-height: 25px; padding: 3px 5px; border-radius: 5px; }}
    QTreeWidget::item:hover {{ background: #21344d; }}
    QTreeWidget::item:selected {{ color: #ffffff; background: #2a526e; }}
    QHeaderView::section {{
        color: #8faac4; background: #292c40; border: 0;
        border-bottom: 1px solid #30445a; padding: 5px 7px; font-size: 8pt; font-weight: 700;
    }}
    QScrollArea#detailsScroll {{ background: transparent; border: 0; }}
    QScrollBar:vertical {{ width: 8px; background: transparent; margin: 3px 0; }}
    QScrollBar::handle:vertical {{ background: #4c4f5b; border-radius: 4px; min-height: 26px; }}
    QScrollBar::handle:vertical:hover {{ background: #6f91b2; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

    QTabWidget::pane {{ border: 0; background: #1b1e24; }}
    QTabBar {{ background: #1b1e24; }}
    QTabBar::tab {{
        color: #a6a9b5; background: #24272f;
        border: 1px solid #283b52; border-radius: 9px;
        padding: 5px 10px; margin: 2px 3px 3px 3px; min-width: 68px;
    }}
    QTabBar::tab:hover {{ background: #263b55; color: #f1f7ff; }}
    QTabBar::tab:selected {{ color: #ffab43; background: #35313a; border-color: #ff940d; font-weight: 700; }}
    QTabBar::tab:focus {{ border: 1px solid #ff940d; }}
    QStatusBar {{ color: #9599a5; background: transparent; border-top: 1px solid #30333b; font-size: 8pt; }}
    QStatusBar::item {{ border: 0; }}
    QMenu {{ color: #eaf3ff; background: #17243a; border: 1px solid #405672; padding: 5px; }}
    QMenu::item {{ padding: 7px 24px; border-radius: 6px; }}
    QMenu::item:selected {{ background: #2a526e; }}
    QToolTip {{ color: #eff7ff; background: #22364d; border: 1px solid #54708d; padding: 5px; }}
    """


APP_STYLESHEET = app_stylesheet()
