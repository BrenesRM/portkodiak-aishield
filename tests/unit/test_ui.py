import pytest
from PyQt6.QtWidgets import QMainWindow, QTabWidget
from app.ui.main_window import PortKodiakWindow

# Use headless mode for CI/testing if possible, but pytest-qt handles this well usually.
# Requires 'pytest-qt' or careful handling of QApplication.

@pytest.fixture
def app(qtbot):
    """Create the main window for testing."""
    window = PortKodiakWindow()
    qtbot.addWidget(window)
    return window

def test_window_title(app):
    """Test window title is correct."""
    assert app.windowTitle() == "PortKodiak AI Shield"

def test_tabs_exist(app):
    """Test that tabs are created."""
    assert isinstance(app.tabs, QTabWidget)
    assert app.tabs.count() == 3
    assert app.tabs.tabText(0) == "Dashboard"
    assert app.tabs.tabText(1) == "Live Monitor"
    assert app.tabs.tabText(2) == "Settings"

def test_status_bar_initial(app):
    """Test status bar exists."""
    assert app.statusBar() is not None
