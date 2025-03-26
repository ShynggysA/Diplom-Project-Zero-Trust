import subprocess

# Запуск Uvicorn
uvicorn_process = subprocess.Popen(["uvicorn", "Server.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])

# Запуск локального веб-сервера для HTML (если он нужен)
web_server_process = subprocess.Popen(["python", "-m", "http.server", "8080"], cwd="Server.templates")

try:
    uvicorn_process.wait()
    web_server_process.wait()
except KeyboardInterrupt:
    uvicorn_process.terminate()
    web_server_process.terminate()
