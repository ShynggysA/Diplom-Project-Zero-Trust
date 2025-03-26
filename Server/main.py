from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from requests import Session
from Server import init_db, models
from Server.database import SessionLocal
from Server.schemas import DeviceData

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Инициализация базы при запуске
init_db.init_db()

# Подключаем шаблоны и статику
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция проверки устройства
def check_policies(device: DeviceData):
    return (
        device.antivirus != "None"
        and device.antivirus_updates != "Unknown"
        and device.firewall.lower() == "off"
        and device.disk_encryption.lower() == "off"
        and device.suspicious_processes.lower() == "not found"
    )

# API для проверки устройства
@app.post("/check")
async def check_device(device: DeviceData):
    try:
        session = SessionLocal()

        # Удаляем старую запись
        session.query(models.DeviceLog).filter_by(id=device.id).delete()

        # Проверяем политику безопасности
        status = "granted" if check_policies(device) else "denied"

        # Логируем устройство в БД
        new_log = models.DeviceLog(
            id=device.id,
            antivirus=device.antivirus,
            antivirus_updates=device.antivirus_updates,
            vpn=device.vpn,
            os=device.os,
            os_updates=device.os_updates,
            firewall=device.firewall,
            disk_encryption=device.disk_encryption,
            suspicious_processes=device.suspicious_processes,
            ip=device.ip,
            status=status,
        )
        session.add(new_log)
        session.commit()

        return {"access": status, "token": "secure-access-token" if status == "granted" else None}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        session.close()

@app.get("/api/server-status")
async def get_server_status():
    return {"status": "Server is running"}

# Получение сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Регистрация пользователя
@app.post("/register/")
def register(username: str, password: str, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(password)
    user = models.User(username=username, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered successfully", "user_id": user.id}

# Получение списка пользователей
@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

# Получение всех зарегистрированных устройств
@app.get("/devices/")
def get_devices(db: Session = Depends(get_db)):
    devices = db.query(models.Device).all()
    return devices

# Логирование входов
@app.post("/auth_logs/")
def log_auth(user_id: int, device_id: str, ip: str, status: str, db: Session = Depends(get_db)):
    log = models.AuthLog(user_id=user_id, device_id=device_id, ip=ip, status=status)
    db.add(log)
    db.commit()
    return {"message": "Log saved"}