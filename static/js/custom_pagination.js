// ------------------------------------
// KONFIGURACJA
// ------------------------------------
const ROWS_PER_PAGE = 10; // Ile wierszy na stronę

// ------------------------------------
// 1) FUNKCJA TWORZĄCA PAGINACJĘ DLA DANEJ TABELI
// ------------------------------------
function initializePaginationForTable(table) {
  // Ustaw domyślnie, że wszystkie wiersze są przefiltrowane
  const allRows = table.querySelectorAll('tbody tr');
  allRows.forEach(row => {
    row.dataset.filtered = "true";
  });

  // Jeśli nie ma data-current-page, ustawiamy ją na 1
  if (!table.dataset.currentPage) {
    table.dataset.currentPage = 1;
  }

  // Jeżeli już istnieje kontener paginacji, nie tworzymy go drugi raz
  if (!table.nextElementSibling || !table.nextElementSibling.classList.contains('pagination-container')) {
    const paginationContainer = document.createElement('div');
    paginationContainer.classList.add('pagination-container');
    paginationContainer.style.margin = '10px 0';

    // --- Przycisk "Poprzednia" ---
    const prevButton = document.createElement('button');
    prevButton.textContent = 'Poprzednia';
    prevButton.addEventListener('click', () => {
      let currentPage = parseInt(table.dataset.currentPage, 10);
      if (currentPage > 1) {
        table.dataset.currentPage = currentPage - 1;
        renderPagination(table);
      }
    });
    paginationContainer.appendChild(prevButton);

    // --- Przycisk "Następna" ---
    const nextButton = document.createElement('button');
    nextButton.textContent = 'Następna';
    nextButton.style.marginLeft = '5px';
    nextButton.addEventListener('click', () => {
      let currentPage = parseInt(table.dataset.currentPage, 10);
      table.dataset.currentPage = currentPage + 1;
      renderPagination(table);
    });
    paginationContainer.appendChild(nextButton);

    // --- Info o stronach ---
    const infoSpan = document.createElement('span');
    infoSpan.style.marginLeft = '10px';
    infoSpan.className = 'pagination-info';
    paginationContainer.appendChild(infoSpan);

    // Wstawiamy kontener pod tabelą
    table.insertAdjacentElement('afterend', paginationContainer);
  }

  // Pierwsze wymuszone renderowanie
  renderPagination(table);
}

// ------------------------------------
// 2) FUNKCJA RENDERUJĄCA PAGINACJĘ
// ------------------------------------
function renderPagination(table) {
  let currentPage = parseInt(table.dataset.currentPage, 10) || 1;
  const allRows = Array.from(table.querySelectorAll('tbody tr'));

  // Używamy atrybutu data-filtered – tylko te, które przeszły filtr (czyli mają "true")
  const visibleRows = allRows.filter(row => {
    return row.dataset.filtered === "true";
  });

  // Obliczamy liczbę stron
  const totalPages = Math.max(1, Math.ceil(visibleRows.length / ROWS_PER_PAGE));

  // Korekta bieżącej strony, jeśli przekroczono zakres
  if (currentPage > totalPages) {
    currentPage = totalPages;
    table.dataset.currentPage = currentPage;
  }

  // Ukrywamy wszystkie przefiltrowane wiersze
  visibleRows.forEach(row => {
    row.style.display = 'none';
  });

  // Wyświetlamy tylko te wiersze, które należą do bieżącej strony
  const startIndex = (currentPage - 1) * ROWS_PER_PAGE;
  const endIndex = startIndex + ROWS_PER_PAGE;
  visibleRows.slice(startIndex, endIndex).forEach(row => {
    row.style.display = 'table-row';
  });

  // Aktualizacja przycisków i informacji o paginacji
  const paginationContainer = table.nextElementSibling;
  if (paginationContainer && paginationContainer.classList.contains('pagination-container')) {
    const [prevButton, nextButton, infoSpan] = paginationContainer.children;
    prevButton.disabled = (currentPage === 1);
    nextButton.disabled = (currentPage === totalPages);
    infoSpan.textContent = `Strona ${currentPage} z ${totalPages} (widoczne wiersze: ${visibleRows.length})`;
  }
}

// ------------------------------------
// 3) INICJACJA FILTROWANIA I PAGINACJI DLA WSZYSTKICH TABEL
// ------------------------------------
function initializePagination() {
  // Wybieramy wszystkie tabele z atrybutem pagination="true"
  const tables = document.querySelectorAll('table[pagination="true"]');

  tables.forEach(table => {
    // Inicjujemy paginację dla każdej tabeli
    initializePaginationForTable(table);

    // Podpinamy nasłuchiwacze zdarzeń dla filtrów (input lub select w nagłówkach)
    const filterElements = table.querySelectorAll('th input[type="text"], th select');
    filterElements.forEach(filterEl => {
      const eventName = (filterEl.tagName === 'INPUT') ? 'input' : 'change';
      filterEl.addEventListener(eventName, () => {
        // Po wywołaniu filtra (przy użyciu zewnętrznego mechanizmu) odłóż działanie, aby pobrać nowy stan
        setTimeout(() => {
          // Aktualizujemy atrybut data-filtered dla każdego wiersza
          const allRows = table.querySelectorAll('tbody tr');
          allRows.forEach(row => {
            row.dataset.filtered = row.style.display !== 'none' ? "true" : "false";
          });
          // Resetujemy paginację do strony 1 i renderujemy
          table.dataset.currentPage = 1;
          renderPagination(table);
        }, 0);
      });
    });
  });
}

// ------------------------------------
// 4) STARTOWA INICJALIZACJA ORAZ OBSŁUGA HTMX
// ------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  initializePagination();
});

// Inicjalizacja po przeładowaniu fragmentu strony przez HTMX
document.body.addEventListener('htmx:afterSwap', function(event) {
  // Opcjonalnie możesz sprawdzić, czy nowy fragment zawiera tabele z paginacją:
  if (event.detail.target.querySelector('table[pagination="true"]')) {
    initializePagination();
  }
});


function initializePagination() {
  const tables = document.querySelectorAll('table[pagination="true"]');
  console.log("Znalezione tabele z paginacją:", tables);
  tables.forEach(table => {
    console.log("Inicjalizuję paginację dla:", table);
    initializePaginationForTable(table);
    // … reszta kodu
  });
}

