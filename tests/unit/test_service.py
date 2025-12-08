import logging
import sys
from unittest.mock import MagicMock, patch
import pytest

# Mock win32 modules before importing service
if 'win32serviceutil' not in sys.modules:
    sys.modules['win32serviceutil'] = MagicMock()
if 'win32service' not in sys.modules:
    sys.modules['win32service'] = MagicMock()
    sys.modules['win32service'].SERVICE_STOP_PENDING = 1
if 'win32event' not in sys.modules:
    sys.modules['win32event'] = MagicMock()
    sys.modules['win32event'].WAIT_OBJECT_0 = 0  # CRITICAL: Must match WaitForSingleObject return
if 'servicemanager' not in sys.modules:
    sys.modules['servicemanager'] = MagicMock()
    sys.modules['servicemanager'].EVENTLOG_INFORMATION_TYPE = 1
    sys.modules['servicemanager'].PYS_SERVICE_STARTED = 1

from app.service.main import PortKodiakService

class TestPortKodiakService:
    """Test suite for PortKodiakService."""
    
    @pytest.fixture
    def mock_service_deps(self):
        """Setup mocks for service dependencies."""
        with patch('win32event.CreateEvent') as mock_create_event, \
             patch('win32event.WaitForSingleObject') as mock_wait, \
             patch('app.service.main.setup_logging') as mock_log:
            
            # Default behavior: Return 0 (signaled) to exit loops immediately
            mock_wait.return_value = 0
            
            yield {
                'create_event': mock_create_event,
                'wait': mock_wait,
                'log': mock_log
            }
            
    def test_service_initialization(self, mock_service_deps) -> None:
        """Test service can be initialized."""
        service = PortKodiakService(['PortKodiakAIShield', 'debug'])
        assert service._svc_name_ == "PortKodiakAIShield"
        assert not service.is_running
        
    def test_service_stop(self, mock_service_deps) -> None:
        """Test service stop signal."""
        service = PortKodiakService(['PortKodiakAIShield'])
        service.ReportServiceStatus = MagicMock()
        
        service.SvcStop()
        
        assert not service.is_running
        service.ReportServiceStatus.assert_called()

    def test_service_run_logic(self, mock_service_deps) -> None:
        """Test SvcDoRun calls main."""
        service = PortKodiakService(['PortKodiakAIShield'])
        service.ReportServiceStatus = MagicMock()
        service.main = MagicMock()
        
        service.SvcDoRun()
        
        assert service.is_running
        mock_service_deps['log'].assert_called()
        service.main.assert_called_once()


