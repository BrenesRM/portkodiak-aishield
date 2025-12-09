import os
import pytest
from app.common.crypto import encrypt_data, decrypt_data
from app.common.models import ConnectionEvent, Base
from app.common.database import engine, SessionLocal, init_db

# Setup test DB in memory
@pytest.fixture(scope="module")
def test_db():
    """Create in-memory database for testing."""
    # Override engine for testing if needed, but sqlite is local anyway.
    # We'll just verify the existing setup works.
    
    # Init tables
    init_db()
    
    db = SessionLocal()
    yield db
    db.close()
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)

class TestCrypto:
    """Test encryption utilities."""
    
    def test_encrypt_decrypt(self):
        original = "SecretData123"
        encrypted = encrypt_data(original)
        
        assert encrypted != original
        assert len(encrypted) > 0
        
        decrypted = decrypt_data(encrypted)
        assert decrypted == original
        
    def test_decrypt_invalid(self):
        assert decrypt_data("Runiberish") == ""
        assert decrypt_data("") == ""

class TestDatabase:
    """Test database operations."""
    
    def test_connection_event_crud(self, test_db):
        """Test creating and retrieving connection events."""
        event = ConnectionEvent(
            process_name="chrome.exe",
            process_id=1234,
            remote_ip="8.8.8.8",
            remote_port=443,
            protocol="TCP",
            action="allowed",
            risk_score=0.1
        )
        
        test_db.add(event)
        test_db.commit()
        test_db.refresh(event)
        
        assert event.id is not None
        assert event.timestamp is not None
        
        # Query
        saved = test_db.query(ConnectionEvent).filter_by(process_name="chrome.exe").first()
        assert saved.remote_ip == "8.8.8.8"
        assert saved.action == "allowed"
