import logging
import platform
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QLabel, QStatusBar, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

class PortKodiakWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.setWindowTitle("PortKodiak AI Shield")
        self.resize(1000, 700)
        
        # Setup basic UI layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Navigation Tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.setup_tabs()
        self.setup_status_bar()
        
        # Status update timer (mocking service check for now)
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_service_status)
        self.status_timer.start(5000)

    def setup_tabs(self):
        """Initialize all tabs."""
        self.dashboard_tab = QWidget()
        self.monitor_tab = QWidget()
        self.settings_tab = QWidget()
        
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.monitor_tab, "Live Monitor")
        self.tabs.addTab(self.settings_tab, "Settings")
        
        self.setup_dashboard()
        self.setup_monitor()
        self.setup_settings()

    def setup_dashboard(self):
        """Setup Dashboard tab content."""
        layout = QVBoxLayout(self.dashboard_tab)
        
        # System Info Box
        sys_group = QGroupBox("System Status")
        sys_layout = QGridLayout()
        sys_layout.addWidget(QLabel("OS:"), 0, 0)
        sys_layout.addWidget(QLabel(platform.system() + " " + platform.release()), 0, 1)
        sys_layout.addWidget(QLabel("Protection:"), 1, 0)
        sys_layout.addWidget(QLabel("Active"), 1, 1)
        sys_group.setLayout(sys_layout)
        
        layout.addWidget(sys_group)
        layout.addStretch()

    def setup_monitor(self):
        """Setup Monitor tab content (placeholder)."""
        layout = QVBoxLayout(self.monitor_tab)
        label = QLabel("Real-time network traffic will appear here.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

    def setup_settings(self):
        """Setup Settings tab content (placeholder)."""
        layout = QVBoxLayout(self.settings_tab)
        label = QLabel("Configuration options will be added here.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

    def setup_status_bar(self):
        """Initialize status bar implementation."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Service Status Indicator
        self.service_status_label = QLabel("Service: Checking...")
        self.service_status_label.setStyleSheet("color: #ebdbb2;")
        self.status_bar.addPermanentWidget(self.service_status_label)

    def check_service_status(self):
        """Check if background service is running (Mock implementation)."""
        # TODO: Implement actual service check via IPC or Service Ctl
        is_running = False 
        color = "#ff6b6b"  # Red
        status_text = "Stopped"
        
        self.service_status_label.setText(f"Service: {status_text}")
        self.service_status_label.setStyleSheet(f"color: {color}; padding-right: 10px;")
