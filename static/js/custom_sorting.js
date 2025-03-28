/**
 * Funkcja inicjalizująca nagłówki sortowalne.
 * Znajduje wszystkie <th> z atrybutem sortable="true" i opakowuje ich zawartość
 * w element umożliwiający sortowanie.
 */
function initializeSortableHeaders() {
    // Wyszukujemy wszystkie nagłówki <th> posiadające atrybut sortable="true"
    const sortableHeaders = document.querySelectorAll("th[sortable='true']");

    sortableHeaders.forEach(th => {
        // Sprawdź, czy już zawiera wewnątrz .sortable-column (czyli był już inicjowany)
        if (th.querySelector(".sortable-column")) {
            // Już zainicjalizowane - pomijamy
            return;
        }

        // Jeśli nie, generujemy nową strukturę z divem i ikoną sortowania
        const headerContent = th.innerHTML.trim();
        th.innerHTML = `
      <div onclick="toggleSort(this)"
           class="sortable-column cursor-pointer select-none"
           data-sort="none">
        ${headerContent}
        <span class="icon">⭥</span>
      </div>
    `;
    });
}

// Inicjalizacja sortowania po załadowaniu dokumentu
document.addEventListener("DOMContentLoaded", initializeSortableHeaders);


/**
 * Funkcja aktualizująca ikony sortowania.
 * - Wszystkie kolumny w tej samej tabeli, które nie zostały kliknięte, resetują się do "none" i ikony "⭥"
 * - Kliknięta kolumna ustawia się na 'asc' lub 'desc' (zależnie od bieżącego stanu)
 */
function updateSortIcons(clickedElement, newState) {
    // Odnajdujemy tabelę, w której nastąpiło kliknięcie
    const table = clickedElement.closest("table");
    // W tej tabeli pobieramy wszystkie kolumny z klasą .sortable-column
    const allSortableColumns = table.querySelectorAll(".sortable-column");

    // Resetujemy wszystkie kolumny oprócz klikniętej
    allSortableColumns.forEach(column => {
        if (column !== clickedElement) {
            column.setAttribute("data-sort", "none");
            column.querySelector(".icon").textContent = "⭥";
        }
    });

    // Dla klikniętej kolumny ustawiamy nowy stan (asc/desc/none)
    clickedElement.setAttribute("data-sort", newState);
    const icon = clickedElement.querySelector(".icon");
    if (newState === "asc") {
        icon.textContent = "🡩";  // Strzałka w górę
    } else if (newState === "desc") {
        icon.textContent = "🡣";  // Strzałka w dół
    } else {
        icon.textContent = "⭥";   // Stan neutralny
    }
}


/**
 * Sortuje wiersze w <tbody> na podstawie wybranej kolumny.
 * ascending = true -> sortowanie rosnące,
 * ascending = false -> sortowanie malejące.
 */
function sortTable(tbody, columnIndex, ascending) {
    const rows = Array.from(tbody.querySelectorAll("tr"));
    rows.sort((a, b) => {
        const cellA = a.querySelectorAll("td")[columnIndex]?.textContent.trim() || "";
        const cellB = b.querySelectorAll("td")[columnIndex]?.textContent.trim() || "";

        // Sortowanie z uwzględnieniem wartości tekstowych i liczbowych
        return ascending
            ? cellA.localeCompare(cellB, undefined, {numeric: true})
            : cellB.localeCompare(cellA, undefined, {numeric: true});
    });

    tbody.innerHTML = "";
    rows.forEach(row => tbody.appendChild(row));
}


/**
 * Główna funkcja obsługująca kliknięcie w nagłówek kolumny sortowalnej.
 * - Odczytuje aktualny stan data-sort (none, asc, desc)
 * - Ustala nowy kierunek sortowania
 * - Wywołuje updateSortIcons i sortTable
 */
function toggleSort(clickedElement) {
    // Znajdź tabelę, w której znajduje się kliknięty nagłówek
    const table = clickedElement.closest("table");
    const tbody = table.querySelector("tbody");
    // Bieżący stan sortowania w klikniętej kolumnie
    const currentSort = clickedElement.getAttribute("data-sort");
    // Ustal nowy stan (jeśli był asc, to teraz będzie desc, w przeciwnym wypadku asc)
    let newState = currentSort === "asc" ? "desc" : "asc";

    // Znajdź indeks klikniętej kolumny
    const headerCells = Array.from(clickedElement.closest("tr").querySelectorAll("th"));
    const columnIndex = headerCells.findIndex(th => th.contains(clickedElement));

    // Zaktualizuj ikony w tej tabeli
    updateSortIcons(clickedElement, newState);
    // Wykonaj faktyczne sortowanie
    const ascending = (newState === "asc");
    sortTable(tbody, columnIndex, ascending);
}


/**
 * Funkcje pomocnicze do przywracania stanu sortowania po odświeżeniu danych (np. przez htmx).
 * Teraz są dostosowane tak, by wyszukiwać stan sortowania tylko w danej tabeli.
 */
function getCurrentSorting(table) {
    // Znajdź w tej tabeli kolumnę, która ma data-sort ustawione na "asc" lub "desc"
    const sortedColumn = table.querySelector(".sortable-column[data-sort='asc'], .sortable-column[data-sort='desc']");
    if (!sortedColumn) return null;

    const currentSort = sortedColumn.getAttribute("data-sort");
    const ascending = (currentSort === "asc");
    const headerCells = Array.from(sortedColumn.closest("tr").querySelectorAll("th"));
    const columnIndex = headerCells.findIndex(th => th.contains(sortedColumn));

    return {columnIndex, ascending};
}

function applyCurrentSorting(table) {
    const sorting = getCurrentSorting(table);
    if (!sorting) return;  // Brak aktualnie wybranej kolumny do sortowania

    const tbody = table.querySelector("tbody");
    sortTable(tbody, sorting.columnIndex, sorting.ascending);
}


// Po swapie (np. HTMX) możemy chcieć przywrócić poprzedni stan sortowania
document.addEventListener('htmx:afterSwap', () => {
    // Dla każdej tabeli na stronie próbujemy przywrócić poprzedni stan
    document.querySelectorAll("table").forEach(table => {
        applyCurrentSorting(table);
    });
});


document.addEventListener("htmx:afterSwap", () => {
    // Po wczytaniu nowej tabeli wstawionej przez HTMX
    initializeSortableHeaders();
    initializeTableSearch(); // jeśli używasz filtrów


});
