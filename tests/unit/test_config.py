import os
from pathlib import Path
from app.config import settings, Settings

class TestSettings:
    """Test suite for application settings."""
    
    def test_default_values(self):
        """Test default configuration values."""
        assert settings.SERVICE_NAME == "PortKodiakAIShield"
        assert settings.LOG_LEVEL == "INFO"
        assert isinstance(settings.LOG_DIR, Path)
        
    def test_env_override(self, monkeypatch):
        """Test environment variables override defaults."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("SERVICE_NAME", "TestService")
        
        # Reload settings to pick up env vars
        # Note: In a real app we might not reload the global object, 
        # but for testing we want to verify the logic.
        # Alternatively, verify on a new instance:
        test_settings = Settings()
        assert test_settings.LOG_LEVEL == "DEBUG"
        assert test_settings.SERVICE_NAME == "TestService"
