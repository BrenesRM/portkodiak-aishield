"""
Data models for PortKodiakAIShield.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass

class ConnectionEvent(Base):
    """Represents a network connection attempt."""
    
    __tablename__ = "connection_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    process_name: Mapped[str] = mapped_column(String(255))
    process_id: Mapped[int] = mapped_column(Integer)
    
    remote_ip: Mapped[str] = mapped_column(String(45))  # IPv6 support
    remote_port: Mapped[int] = mapped_column(Integer)
    protocol: Mapped[str] = mapped_column(String(10))   # TCP/UDP
    
    action: Mapped[str] = mapped_column(String(20))     # allowed/blocked
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    def __repr__(self) -> str:
        return f"<ConnectionEvent(proc={self.process_name}, ip={self.remote_ip}, action={self.action})>"
