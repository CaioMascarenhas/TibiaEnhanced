"""Linguagem visual do aplicativo; os espelhos DWM mantêm sua própria aparência."""

APP_STYLESHEET = """
QMainWindow, QWidget#appPage, QWidget#placeholderPage {
    background: #111a24;
    color: #edf2f7;
}
QDialog {
    background: #182430;
    color: #edf2f7;
}
QLabel {
    color: #edf2f7;
    background: transparent;
}
QLabel#pageTitle {
    font-size: 25px;
    font-weight: 700;
    color: #f8fafc;
}
QLabel#sectionTitle {
    font-size: 15px;
    font-weight: 700;
    color: #f1d199;
}
QLabel#selectedTitle {
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
}
QLabel#mutedText, QLabel#eyebrow {
    color: #9eafc0;
}
QLabel#eyebrow {
    font-size: 11px;
    font-weight: 700;
    padding-top: 12px;
}
QLabel#statusText {
    color: #bed0df;
    background: #1c2a38;
    border: 1px solid #304357;
    border-radius: 8px;
    padding: 9px 12px;
}
QFrame#card {
    background: #1b2937;
    border: 1px solid #34485b;
    border-radius: 11px;
}
QScrollArea#detailsScroll {
    background: #111a24;
    border: 0;
}
QScrollBar:vertical {
    width: 9px;
    background: #14212d;
}
QScrollBar::handle:vertical {
    background: #4b6278;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QPushButton {
    color: #e8f0f7;
    background: #2b3d50;
    border: 1px solid #40566b;
    border-radius: 7px;
    padding: 8px 12px;
    min-height: 21px;
}
QPushButton:hover { background: #38516a; border-color: #6586a0; }
QPushButton:pressed { background: #25374a; }
QPushButton:disabled {
    color: #748596;
    background: #23303d;
    border-color: #344252;
}
QPushButton#primaryButton {
    color: #1d2024;
    background: #e5b65d;
    border-color: #f0cd82;
    font-weight: 700;
}
QPushButton#primaryButton:hover { background: #f3cb7d; }
QPushButton#primaryButton:disabled {
    color: #756b55;
    background: #776747;
    border-color: #837257;
}
QPushButton#dangerButton { color: #ffd8d8; border-color: #744851; }
QPushButton#dangerButton:hover { background: #6c3541; }
QComboBox, QLineEdit {
    color: #f1f5f9;
    background: #13202c;
    border: 1px solid #43576b;
    border-radius: 7px;
    padding: 7px 10px;
    min-height: 22px;
    selection-background-color: #376985;
}
QComboBox:hover, QLineEdit:focus { border-color: #d5ac64; }
QComboBox:disabled, QLineEdit:disabled { color: #748596; }
QComboBox::drop-down { border: 0; width: 24px; }
QComboBox QAbstractItemView {
    color: #f1f5f9;
    background: #1b2937;
    border: 1px solid #52677c;
    selection-background-color: #376985;
}
QTreeWidget {
    color: #e8eff6;
    background: #14212d;
    border: 1px solid #344a5e;
    border-radius: 8px;
    padding: 5px;
    outline: none;
}
QTreeWidget::item { min-height: 32px; padding: 4px 5px; }
QTreeWidget::item:hover { background: #273e51; }
QTreeWidget::item:selected {
    color: #ffffff;
    background: #345e78;
    border-left: 3px solid #e5b65d;
}
QHeaderView::section {
    color: #9eafc0;
    background: #1b2937;
    border: 0;
    border-bottom: 1px solid #344a5e;
    padding: 6px 8px;
    font-size: 11px;
    font-weight: 700;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #35495b;
    border-radius: 3px;
}
QSlider::sub-page:horizontal { background: #e5b65d; border-radius: 3px; }
QSlider::handle:horizontal {
    background: #f8d28b;
    border: 1px solid #fff0ca;
    width: 15px;
    margin: -6px 0;
    border-radius: 8px;
}
QTabWidget::pane { border: 0; background: #111a24; }
QTabBar::tab {
    color: #aab9c9;
    background: #1b2937;
    border: 0;
    border-bottom: 3px solid transparent;
    padding: 11px 22px;
    min-width: 112px;
}
QTabBar::tab:selected {
    color: #ffffff;
    background: #243648;
    border-bottom-color: #e5b65d;
}
QTabBar::tab:hover { background: #2a3f53; }
QStatusBar {
    color: #aab9c9;
    background: #182430;
    border-top: 1px solid #34485b;
}
QMenu {
    color: #edf2f7;
    background: #1b2937;
    border: 1px solid #43576b;
    padding: 4px;
}
QMenu::item { padding: 7px 22px; }
QMenu::item:selected { background: #345e78; }
"""
