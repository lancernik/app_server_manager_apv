import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from openpyxl import Workbook

from process_manager.models import SystemProcessesSnapshot


def export_snapshot_processes(request, pk):
    # Pobierz snapshot lub zwróć 404, jeśli nie istnieje
    snapshot = get_object_or_404(SystemProcessesSnapshot, pk=pk)
    processes = snapshot.processes.all()

    # Utwórz nowy skoroszyt Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Processes Snapshot"

    # Zdefiniuj nagłówki kolumn
    headers = ['Name', 'PID', 'Status', 'Start Time', 'Duration', 'Memory Usage [MB]', 'CPU Usage [%]']
    ws.append(headers)

    # Dodaj dane procesów
    for process in processes:
        ws.append([
            process.name,
            process.pid,
            process.status,
            process.start_time.strftime("%Y-%m-%d %H:%M:%S") if process.start_time else '',
            str(process.duration),
            process.formatted_memory_usage(),
            process.cpu_usage,
        ])

    # Przygotuj odpowiedź HTTP z plikiem Excel
    response = HttpResponse(content_type='application/ms-excel')
    # Get current date in format yyyy_mm_dd
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"{date}__{pk}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    wb.save(response)
    return response
