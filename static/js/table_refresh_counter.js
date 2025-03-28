// Ustawienie interwału (w sekundach) między aktualizacjami
const updateInterval = 30;
let timer = null;
let firstUpdate = true;

// Funkcja aktualizująca licznik
function updateCountdown() {
    if (timer !== null) {
        timer--;
        // Aktualizujemy licznik jeśli wartość jest nieujemna
        if (timer >= 0) {
            document.getElementById('next-update-counter').innerText = 'Next update in: ' + timer + ' seconds';
        }
    }
}

// Inicjalizacja licznika co sekundę, ale tylko po pierwszej aktualizacji
setInterval(updateCountdown, 1000);

// Nasłuchiwanie zdarzenia htmx po wymianie zawartości
document.body.addEventListener('htmx:afterSwap', function (evt) {
    if (evt.detail.target.id === "process-table-data") {
        // Aktualizacja czasu ostatniej aktualizacji
        document.getElementById('last-update').innerText = 'Last update: ' + new Date().toLocaleString();

        // Uruchamiamy licznik dopiero po pierwszej aktualizacji
        if (firstUpdate) {
            firstUpdate = false;
            timer = updateInterval;
        } else {
            // Resetujemy licznik przy każdej kolejnej aktualizacji
            timer = updateInterval;
        }
    }
});
