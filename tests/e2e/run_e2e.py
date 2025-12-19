import sys
import os
import time
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Patch DB to memory BEFORE importing app modules
from app.config import settings
from pathlib import Path
settings.DB_PATH = Path(":memory:")

from app.common import database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Re-init engine just in case
database.engine = create_engine("sqlite:///:memory:")
database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=database.engine)

from app.common.models import Alert, TrafficSample
from app.common.database import SessionLocal, init_db
from app.core.action_manager import ActionManager

def run_test():
    print("--- Starting E2E Workflow Test ---")
    
    print("1. Initializing DB...")
    init_db()
    
    print("2. Testing Alert Generation (Simulated)...")
    db = SessionLocal()
    alert = Alert(
        process_name="nmap.exe",
        process_path="C:\\Program Files\\nmap\\nmap.exe",
        remote_ip="192.168.1.100",
        remote_port=445,
        risk_score=0.95,
        status="NEW"
    )
    db.add(alert)
    db.commit()
    alert_id = alert.id
    db.close()
    print("   -> Alert Injected.")
    
    # Verify
    db = SessionLocal()
    saved = db.query(Alert).filter(Alert.id == alert_id).first()
    if saved and saved.process_name == "nmap.exe":
        print("   -> PASS: Alert found in DB.")
    else:
        print("   -> FAIL: Alert not found.")
        sys.exit(1)
    db.close()
    
    print("3. Testing Action Integration...")
    # Create pending alert
    db = SessionLocal()
    pending_alert = Alert(
        process_name="malware.exe",
        process_path="C:\\Temp\\malware.exe",
        remote_ip="10.0.0.5",
        remote_port=6667,
        risk_score=0.99,
        status="PENDING_BLOCK"
    )
    db.add(pending_alert)
    db.commit()
    p_id = pending_alert.id
    db.close()
    
    # Run ActionManager
    mock_agent = MagicMock()
    mock_agent.add_block_rule.return_value = 999
    
    manager = ActionManager(mock_agent)
    print("   -> Processing Action Queue...")
    manager.process_queue()
    
    # Verify
    db = SessionLocal()
    updated = db.query(Alert).filter(Alert.id == p_id).first()
    if updated.status == "BLOCKED":
        print("   -> PASS: Alert status updated to BLOCKED.")
    else:
        print(f"   -> FAIL: Alert status is {updated.status}")
        sys.exit(1)
        
    mock_agent.add_block_rule.assert_called_with(6667, name=f"AutoBlock Alert {p_id}")
    print("   -> PASS: Agent method called.")
    
    print("--- E2E Test Complete: SUCCESS ---")

if __name__ == "__main__":
    run_test()
