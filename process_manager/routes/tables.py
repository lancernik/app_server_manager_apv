from django.shortcuts import render

from process_manager.models import SystemProcessesSnapshot
from process_manager.utils import fetch_processes


def get_processes_table(request, pk):
    snapshot = SystemProcessesSnapshot.objects.filter(pk=pk).first()
    if not snapshot:
        return 'No such snapshot'

    context = {
        'processes': snapshot.processes.all(),
        'snapshot': snapshot
    }
    return render(request, 'tables/process_table.html', context)


def refresh_processes_table(request):
    processes = fetch_processes()
    process_list = [
        {
            "pid": pid,
            "name": info['name'],
            "status": info['status'],
            "start_time": info['start_time'],
            "duration": info['duration'],
            "memory_usage": f"{info['memory_usage'] / (1024 * 1024):.2f} MB",
            "cpu_usage": f"{info['cpu_usage']:.2f}%"
        }
        for pid, info in processes.items()
    ]
    return render(request, "utils/processes_rows_update.html", {"processes": process_list})
