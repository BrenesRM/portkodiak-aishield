"""
Main entry point for the PortKodiakAIShield Windows service.
"""

import sys
import logging
import time
import socket
from pathlib import Path
from typing import NoReturn

import win32serviceutil  # type: ignore
import win32service  # type: ignore
import win32event  # type: ignore
import servicemanager  # type: ignore

from app.common.logging import setup_logging

class PortKodiakService(win32serviceutil.ServiceFramework):
    """Main service class for PortKodiakAIShield."""
    
    _svc_name_ = "PortKodiakAIShield"
    _svc_display_name_ = "PortKodiak AI Shield"
    _svc_description_ = "Windows Application Firewall with ML-based Anomaly Detection"
    
    def __init__(self, args: list) -> None:
        """Initialize the service."""
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = False
        self.logger = logging.getLogger(__name__)

    def SvcStop(self) -> None:
        """Stop the service."""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.is_running = False
        self.logger.info("Service stop signal received")

    def SvcDoRun(self) -> None:
        """Main service loop."""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        # Setup logging to ProgramData
        log_dir = Path("C:/ProgramData/PortKodiakAIShield/logs")
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            setup_logging(log_file=log_dir / "service.log")
        except Exception:
            # Fallback to current directory if permission denied (dev mode)
            setup_logging(log_file=Path("service.log"))

        self.logger.info(f"Service {self._svc_name_} started")
        self.is_running = True
        
        try:
            self.main()
        except Exception as e:
            self.logger.error(f"Service error: {e}", exc_info=True)
            self.SvcStop()

    def main(self) -> None:
        """Service logic."""
        # TODO: Initialize WFP integration
        # TODO: Load ML models
        
        while self.is_running:
            # Check for stop signal
            rc = win32event.WaitForSingleObject(self.stop_event, 1000)
            if rc == win32event.WAIT_OBJECT_0:
                break
                
            # TODO: Process events
            self.logger.debug("Service heartbeat")
            

def main() -> None:
    """Entry point."""
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(PortKodiakService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(PortKodiakService)

if __name__ == "__main__":
    main()
