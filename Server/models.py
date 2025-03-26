from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from Server.database import Base 

class DeviceLog(Base):
    __tablename__ = "device_logs"
    id = Column(String, primary_key=True, index=True)
    antivirus = Column(String, nullable=False)
    antivirus_updates = Column(String, nullable=False)
    vpn = Column(String, nullable=False)
    os = Column(String, nullable=False)
    os_updates = Column(String, nullable=False)
    firewall = Column(String, nullable=False)
    disk_encryption = Column(String, nullable=False)
    suspicious_processes = Column(String, nullable=False)
    ip = Column(String, nullable=False)
    status = Column(String, nullable=False)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # Будем хранить хеш пароля
    role = Column(String, default="employee")  # employee / admin
    created_at = Column(DateTime, default=datetime.utcnow)

    devices = relationship("Device", back_populates="user")
    auth_logs = relationship("AuthLog", back_populates="user")

class Device(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    os = Column(String)
    ip = Column(String)
    last_check = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="devices")
    logs = relationship("Log", back_populates="device")

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("devices.id"), nullable=False)
    antivirus = Column(String)
    antivirus_updates = Column(String)
    firewall = Column(String)
    vpn = Column(String)
    disk_encryption = Column(String)
    suspicious_processes = Column(String)
    os_updates = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    device = relationship("Device", back_populates="logs")

class AuthLog(Base):
    __tablename__ = "auth_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(String, ForeignKey("devices.id"), nullable=False)
    ip = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String)

    user = relationship("User", back_populates="auth_logs")