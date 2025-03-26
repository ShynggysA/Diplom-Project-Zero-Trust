document.addEventListener("DOMContentLoaded", function () {
    const statusElement = document.getElementById("status"); // Проверяем правильный ID

    // Функция для обновления статуса сервера
    async function fetchServerStatus() {
        try {
            let response = await fetch("http://127.0.0.1:8000/api/server-status");
    
            if (!response.ok) throw new Error("Server error");
    
            let data = await response.json();
    
            statusElement.textContent = data.status; // Обновляем HTML
        } catch (error) {
            statusElement.textContent = "Connection error";
        }
    }
    

    // Первоначальная проверка статуса
    fetchServerStatus();

    // Запрашивать статус каждые 5 секунд
    setInterval(fetchServerStatus, 5000);
});