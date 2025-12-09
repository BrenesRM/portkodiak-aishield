from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application configuration."""
    
    # Service settings
    SERVICE_NAME: str = "PortKodiakAIShield"
    SERVICE_DISPLAY_NAME: str = "PortKodiak AI Shield"
    SERVICE_DESCRIPTION: str = "Windows Application Firewall with ML-based Anomaly Detection"
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Path("C:/ProgramData/PortKodiakAIShield/logs")
    
    # ML settings
    MODEL_DIR: Path = Path("ml/models")
    
    # Data storage
    DB_PATH: Path = Path("C:/ProgramData/PortKodiakAIShield/data.db")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
