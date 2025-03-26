from pydantic import BaseModel

class DeviceData(BaseModel):
    id: str
    antivirus: str
    antivirus_updates: str
    vpn: str
    os: str
    os_updates: str
    firewall: str
    disk_encryption: str
    suspicious_processes: str
    ip: str