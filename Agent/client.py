import re
import subprocess
import threading
import time
import requests
import uuid
import socket
import psutil
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# Конфигурация сервера
SERVER_URL = "http://127.0.0.1:8000/check"
DEVICE_ID = str(uuid.getnode())  # Используем MAC-адрес как ID устройства
CHECK_INTERVAL = 10  # Интервал проверки системы (в секундах)

running = True

def check_antivirus():
    try:
        result = subprocess.run(
            ["wmic", "/namespace:\\\\root\\SecurityCenter2", "path", "AntiVirusProduct", "get", "displayName"],
            capture_output=True, text=True
        )
        lines = result.stdout.split("\n")
        antivirus_names = [line.strip() for line in lines if line.strip() and "displayName" not in line]
        return antivirus_names[0] if antivirus_names else "Not found"
    except Exception as e:
        return str(e)  

def check_av_updates():
    try:
        result = subprocess.run(
            ["powershell", "$lang = [System.Globalization.CultureInfo]::GetCultureInfo('en-US'); "  
                          "$date = (Get-MpComputerStatus).AntivirusSignatureLastUpdated; "  
                          "$date.ToString('dd.MM.yyyy HH:mm:ss', $lang)"],
            capture_output=True, text=True, encoding="utf-8"
        )
        return result.stdout.strip()
    except Exception as e:
        return str(e)

def check_os_updates():
    try:
        result = subprocess.run(["wmic", "qfe", "list", "full"], capture_output=True, text=True)
        
        matches = re.findall(r"InstalledOn=(\d{2}/\d{2}/\d{4})", result.stdout)
        
        if matches:
            last_update_date = matches[-1]
            
            if "/" in last_update_date:
                date_obj = datetime.strptime(last_update_date, "%m/%d/%Y")
                formatted_date = date_obj.strftime("%d.%m.%Y")
            else:
                formatted_date = last_update_date
            
            return formatted_date
        else:
            return "No updates found"
    except Exception as e:
        return str(e)

def check_vpn_status():
    try:
        result = subprocess.run(
            ["powershell", "Get-VpnConnection"],
            capture_output=True, text=True
        )
        if "Name" in result.stdout:
            return "VPN Connected" if "Connected : True" in result.stdout else "VPN Disconnected"
        else:
            return "VPN - connection is not configured"
    except Exception as e:
        return str(e)

def get_windows_version():
    try:
        result = subprocess.run(
            ["wmic", "os", "get", "Caption,Version"], capture_output=True, text=True
        )
        lines = result.stdout.split("\n")
        return [line.strip() for line in lines if line.strip() and "Caption" not in line][0]
    except Exception as e:
        return str(e)

def check_windows_updates():
    try:
        result = subprocess.run(["wmic", "qfe", "get", "InstalledOn"], capture_output=True, text=True)
        update_dates = [line.strip() for line in result.stdout.split("\n") if line.strip() and "InstalledOn" not in line]
        return update_dates[-1] if update_dates else "Не найдено"
    except Exception as e:
        return str(e)

def check_firewall_status():
    try:
        result = subprocess.run(["netsh", "advfirewall", "show", "allprofiles"], capture_output=True, text=True)
        return "On" if "State ON" in result.stdout else "Off"
    except Exception as e:
        return str(e)

def check_bitlocker_status():
    try:
        result = subprocess.run(["manage-bde", "-status", "C:"], capture_output=True, text=True)
        return "On" if "Protection On" in result.stdout else "Off"
    except Exception as e:
        return str(e)

def check_suspicious_processes():
    suspicious_apps = ["anydesk", "teamviewer", "mstsc", "openvpn", "nordvpn", "protonvpn"]
    running_processes = [p.name().lower() for p in psutil.process_iter()]
    detected = [app for app in suspicious_apps if app in running_processes]
    return detected if detected else "Not found"

def get_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "Unknown IP"

def collect_device_data():
    return {
        "id": DEVICE_ID,
        "antivirus": check_antivirus(),
        "antivirus_updates": check_av_updates(),
        "vpn": check_vpn_status(),
        "os": get_windows_version(),
        "os_updates": check_os_updates(),
        "firewall": check_firewall_status(),
        "disk_encryption": check_bitlocker_status(),
        "suspicious_processes": check_suspicious_processes(),
        "ip": get_ip()
    }

def send_data():
    global running
    while running:
        try:
            device_data = collect_device_data()
            print(f"📤 Отправка данных: {device_data}")
            response = requests.post(SERVER_URL, json=device_data)
            print(f"✅ Ответ сервера: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"⚠ Ошибка отправки данных: {e}")

        time.sleep(CHECK_INTERVAL)

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Агент безопасности")
        self.root.geometry("300x150")

        self.status_label = tk.Label(root, text="Агент работает...", font=("Arial", 12))
        self.status_label.pack(pady=10)

        self.stop_button = tk.Button(root, text="Выключить агент", command=self.stop_agent, bg="red", fg="white")
        self.stop_button.pack(pady=10)

    def stop_agent(self):
        global running
        running = False
        self.status_label.config(text="Агент остановлен.")
        print("🛑 Агент выключен")
        messagebox.showinfo("Выход", "Агент остановлен.")
        self.root.destroy()

def start_monitoring():
    monitoring_thread = threading.Thread(target=send_data)
    monitoring_thread.daemon = True
    monitoring_thread.start()

if __name__ == "__main__":
    start_monitoring()
    root = tk.Tk()
    gui = ClientGUI(root)
    root.mainloop()