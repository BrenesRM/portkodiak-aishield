"""
Shared styles and themes for the PortKodiakAIShield UI.
"""

DARK_THEME_QSS = """
QMainWindow {
    background-color: #1a1b1e;
    color: #e1e3e5;
}

QWidget {
    background-color: #1a1b1e;
    color: #e1e3e5;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #2c2e33;
    background: #1a1b1e;
    top: -1px;
}

QTabBar::tab {
    background: #25262b;
    color: #909296;
    border: 1px solid #2c2e33;
    border-bottom: none;
    padding: 8px 16px;
    margin-right: 2px;
    min-width: 80px;
}

QTabBar::tab:selected {
    background: #1a1b1e;
    color: #4dabf7;
    border-top: 2px solid #4dabf7;
}

QTabBar::tab:hover {
    background: #2c2e33;
    color: #e1e3e5;
}

/* Labels */
QLabel {
    color: #e1e3e5;
}

/* Group Boxes */
QGroupBox {
    border: 1px solid #373a40;
    border-radius: 4px;
    margin-top: 1em;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
    color: #4dabf7;
    font-weight: bold;
}

/* Status Bar */
QStatusBar {
    background: #141517;
    color: #909296;
    border-top: 1px solid #2c2e33;
}

/* Buttons */
QPushButton {
    background-color: #228be6;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #1c7ed6;
}

QPushButton:pressed {
    background-color: #1971c2;
}

QPushButton:disabled {
    background-color: #373a40;
    color: #909296;
}
"""
