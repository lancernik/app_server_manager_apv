function showSpinner(form) {
    const button = form.querySelector("button[type='submit']");
    if (button) {
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = `<span class="spinner-border animate-spin mr-2"></span> Performing action...`;
    }
}

function hideSpinner(form) {
    const button = form.querySelector("button[type='submit']");
    if (button) {
        button.disabled = false;
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
        }
    }
}


function markPerformed(form) {
    console.log("PERFORMED")
    console.log(form)
    const button = form.querySelector("button[type='submit']");
    if (button) {
        button.disabled = true;
        button.innerHTML = button.dataset.originalText
            ? `${button.dataset.originalText} (Performed)`
            : `${button.innerHTML} (Performed)`;
    }
}

function handleResponse(form, response) {
    console.log(form, response);
    // Zakładamy, że response to HTML w postaci stringa,
    // np. '<div class="p-2 bg-green-200 rounded mb-1">Killed successfully</div>'
    const notificationArea = document.getElementById('notification-area');

    // Utworzenie tymczasowego kontenera do parsowania HTML
    const tempContainer = document.createElement('div');
    tempContainer.innerHTML = response;

    // Pobieramy pierwszy element, który powinien być naszym powiadomieniem
    const notification = tempContainer.firstElementChild;
    if (notification) {
        // Dodanie powiadomienia na początku listy
        notificationArea.prepend(notification);

        // Jeśli powiadomień jest za dużo, usuwamy najstarsze
        if (notificationArea.childElementCount > 20) {
            notificationArea.removeChild(notificationArea.lastChild);
        }
    }
}
