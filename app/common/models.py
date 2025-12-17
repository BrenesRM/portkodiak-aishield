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

class DnsLog(Base):
    """Represents a DNS resolution event."""
    __tablename__ = "dns_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    ip_address: Mapped[str] = mapped_column(String(45))
    hostname: Mapped[str] = mapped_column(String(255))
    
    def __repr__(self) -> str:
        return f"<DnsLog(ip={self.ip_address}, host={self.hostname})>"

class AppPolicy(Base):
    """Represents a policy for a specific application/process."""
    __tablename__ = "app_policies"

    id: Mapped[int] = mapped_column(primary_key=True)
    process_path: Mapped[str] = mapped_column(String(512), unique=True) # Full path
    policy_type: Mapped[str] = mapped_column(String(20)) # ALLOW or BLOCK
    is_active: Mapped[bool] = mapped_column(default=True)
    
    def __repr__(self) -> str:
        return f"<AppPolicy(path={self.process_path}, type={self.policy_type})>"

class TrafficSample(Base):
    """Raw connection features for ML training."""
    __tablename__ = "traffic_samples"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    process_name: Mapped[str] = mapped_column(String(255))
    process_path: Mapped[str] = mapped_column(String(512))
    process_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    parent_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    remote_ip: Mapped[str] = mapped_column(String(45))
    remote_port: Mapped[int] = mapped_column(Integer)
    remote_hostname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    protocol: Mapped[str] = mapped_column(String(10), default="TCP") # Mostly TCP for now
    direction: Mapped[str] = mapped_column(String(10)) # Inbound/Outbound
    
    is_malicious: Mapped[bool] = mapped_column(default=False) # Label
    
    
    def __repr__(self) -> str:
        return f"<TrafficSample(proc={self.process_name}, ip={self.remote_ip})>"

class Alert(Base):
    """Represents a high-risk event/anomaly detected by the system."""
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    process_name: Mapped[str] = mapped_column(String(255))
    process_path: Mapped[str] = mapped_column(String(512))
    
    remote_ip: Mapped[str] = mapped_column(String(45))
    remote_port: Mapped[int] = mapped_column(Integer)
    
    risk_score: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="New") # New, Viewed, Actioned
    
    def __repr__(self) -> str:
        return f"<Alert(proc={self.process_name}, score={self.risk_score})>"
