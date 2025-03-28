// Funkcja dodająca do odpowiednich nagłówków (th) element sterujący filtrowania
function initializeFilterControls() {
    // Wybieramy wszystkie th z atrybutem filterable="true"
    const thElements = document.querySelectorAll('th[filterable="true"]');

    thElements.forEach(th => {
        const filterType = th.getAttribute("filter-type");

        // Dla filtra tekstowego – dodajemy input
        if (filterType === "text") {
            if (!th.querySelector("input[type='text']")) {
                const input = document.createElement("input");
                input.type = "text";
                input.placeholder = th.getAttribute("filter-placeholder") || "";
                input.className = "mt-1 p-1 w-full rounded border border-gray-300";
                th.appendChild(input);
            }
        }
        // Dla filtra typu select – dodajemy select
        else if (filterType === "select") {
            if (!th.querySelector("select")) {
                const select = document.createElement("select");
                select.className = "mt-1 p-1 w-full rounded border border-gray-300";

                // Pobieramy opcje z atrybutu filter-options
                const optionsStr = th.getAttribute("filter-options");
                if (optionsStr) {
                    const optionsArr = optionsStr.split(",");
                    optionsArr.forEach(optionText => {
                        let parts = optionText.split(":");
                        let value, display;
                        // Jeśli mamy dwie części – wartość i tekst wyświetlany
                        if (parts.length === 2) {
                            value = parts[0].trim().toLowerCase();
                            display = parts[1].trim();
                        } else {
                            // Jeśli nie, używamy tej samej wartości dla obu
                            value = optionText.trim().toLowerCase();
                            display = optionText.trim();
                        }
                        const option = document.createElement("option");
                        option.value = value;
                        option.textContent = display;
                        select.appendChild(option);
                    });
                }
                th.appendChild(select);
            }
        }
    });
}

// Funkcja filtrująca pojedynczą tabelę, wywoływana przy każdej zmianie w polu filtrowym
function filterTable(event) {
    // Filtr, który wywołał zdarzenie
    const filterEl = event.target;
    // Odszukaj tabelę, w której znajduje się filtr
    const table = filterEl.closest("table");
    if (!table) return; // Jeśli z jakiegoś powodu nie ma tabeli, przerywamy

    // Pobierz wszystkie filtry (inputy i selecty) wyłącznie z tej tabeli
    const filterElements = table.querySelectorAll("th input[type='text'], th select");
    // Pobierz wszystkie wiersze w tbody wyłącznie z tej tabeli
    const rows = table.querySelectorAll("tbody tr");

    rows.forEach(row => {
        let showRow = true; // Załóżmy, że wiersz spełnia wszystkie filtry

        filterElements.forEach(filter => {
            const filterValue = filter.value.toLowerCase().trim();
            if (filterValue !== "") {
                // Znajdujemy kolumnę dla tego filtra
                const th = filter.closest("th");
                const tr = th.closest("tr");
                // Indeks kolumny (th) w obrębie wiersza nagłówka
                const columnIndex = Array.from(tr.children).indexOf(th);

                const cell = row.children[columnIndex];
                if (cell) {
                    const cellText = cell.textContent.toLowerCase().trim();

                    if (filter.tagName === "INPUT") {
                        // Dla inputa: sprawdzamy, czy tekst komórki zawiera wpisany ciąg
                        if (!cellText.includes(filterValue)) {
                            showRow = false;
                        }
                    } else if (filter.tagName === "SELECT") {
                        // Dla selecta: sprawdzamy, czy tekst komórki jest równy wybranej wartości
                        if (cellText !== filterValue) {
                            showRow = false;
                        }
                    }
                }
            }
        });

        // W zależności od wyniku showRow ukrywamy/pokazujemy wiersz
        row.style.display = showRow ? "" : "none";
    });
}

// Funkcja inicjalizująca elementy filtrujące i nasłuch
function initializeTableSearch() {
    // Najpierw tworzymy elementy filtrujące (input/select) w nagłówkach:
    initializeFilterControls();

    // Następnie podpinamy nasłuchy zdarzeń do tych elementów
    const filterElements = document.querySelectorAll("th input[type='text'], th select");
    filterElements.forEach(filterEl => {
        if (filterEl.tagName === "INPUT") {
            filterEl.addEventListener("input", filterTable);
        } else if (filterEl.tagName === "SELECT") {
            filterEl.addEventListener("change", filterTable);
        }
    });

    // Na koniec możemy wywołać filtrację "startową" (jeśli chcemy od razu przefiltrować)
    filterElements.forEach(filterEl => {
        // Symulujemy zdarzenie, aby od razu zastosować filtry
        const eventName = filterEl.tagName === "INPUT" ? "input" : "change";
        filterEl.dispatchEvent(new Event(eventName));
    });
}

// Uruchomienie inicjalizacji po załadowaniu DOM oraz po htmx:afterSwap
document.addEventListener("DOMContentLoaded", initializeTableSearch);
document.addEventListener('htmx:afterSwap', initializeTableSearch);
