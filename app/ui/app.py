"""
Main UI application entry point.
"""
import sys
from PyQt6.QtWidgets import QApplication
from app.ui.main_window import PortKodiakWindow
from app.ui.styles import DARK_THEME_QSS

def run_ui():
    """Initialize and run the Qt application."""
    app = QApplication(sys.argv)
    
    # Apply theme
    app.setStyleSheet(DARK_THEME_QSS)
    app.setApplicationName("PortKodiak AI Shield")
    app.setOrganizationName("KodiakAI")
    
    window = PortKodiakWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    run_ui()
