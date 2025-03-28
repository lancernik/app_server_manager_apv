import logging

from django.http import HttpResponse
from django.views.decorators.http import require_POST

from process_manager.utils import fetch_processes, create_processes_snapshot, kill_process_and_log

logger = logging.getLogger(__name__)


@require_POST
def kill_process(request, pid, name):
    # Wywołujemy funkcję, która próbuje zabić proces i tworzy wpis w bazie
    success, message = kill_process_and_log(pid, name, author=request.user)

    # Ustalamy kolor tła w zależności od wyniku operacji
    if success:
        bg_color_class = "bg-green-200"
    elif message.startswith("Error:"):
        bg_color_class = "bg-red-200"
    else:
        bg_color_class = "bg-yellow-200"

    # Zwracamy powiadomienie jako fragment HTML
    return HttpResponse(f'<div class="p-2 {bg_color_class} rounded mb-1">{message}</div>')


@require_POST
def take_snapshot(request):
    try:
        # Pobieranie danych procesów
        processes_data = fetch_processes()
        create_processes_snapshot(processes_data, user=request.user)
        # Sukces - tworzymy powiadomienie
        message = "Snapshot saved successfully"
        bg_color_class = "bg-green-200"
    except Exception as e:
        # Obsługa błędu - zapis do logów
        logger.error(f"Error taking snapshot: {str(e)}")

        # Komunikat błędu
        message = f"Error taking snapshot: {str(e)}"
        bg_color_class = "bg-red-200"

    # Zwracanie powiadomienia jako element HTML
    return HttpResponse(f'<div class="p-2 {bg_color_class} rounded mb-1">{message}</div>')
