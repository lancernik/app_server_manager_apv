let lastUpdateFailed = false;

// Refresh notifications
document.addEventListener("htmx:afterOnLoad", function (event) {
    // Sprawdź, czy zdarzenie dotyczy naszej tabeli i czy poprzednia próba się powiodła
    if (event.target.id === "process-table-data" && !lastUpdateFailed) {
        console.log("Data updated successfully");
        addNotification(`Data refreshed at ${new Date().toLocaleTimeString()}`, "bg-gray-200");
    }
    // Zresetuj flagę błędu po udanej aktualizacji
    lastUpdateFailed = false;
});

document.addEventListener("htmx:responseError", function (event) {
    // Sprawdź, czy zdarzenie dotyczy naszej tabeli
    if (event.detail.target.id === "process-table-data") {
        console.error("Data update failed");
        addNotification(`Data update failed at ${new Date().toLocaleTimeString()}`, "bg-red-200");
        // Ustaw flagę błędu
        lastUpdateFailed = true;
    }
});


function addNotification(message, bgColorClass) {
    const notificationArea = document.getElementById('notification-area');

    // Tworzenie nowego powiadomienia
    const notification = document.createElement('div');
    notification.className = `p-2 ${bgColorClass} rounded mb-1`;
    notification.textContent = message;

    // Dodanie powiadomienia na górze listy
    notificationArea.prepend(notification);

    // Sprawdzenie liczby powiadomień (usunięcie najstarszych jeśli jest ich za dużo)
    if (notificationArea.childElementCount > 20) {
        notificationArea.removeChild(notificationArea.lastChild);
    }
}
