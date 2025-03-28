from django.shortcuts import render
from django.views.decorators.http import require_POST

from process_manager.models import SystemProcessesSnapshot


@require_POST
def get_chart_for_cpu(request):
    snapshots = SystemProcessesSnapshot.objects.all().order_by('created')
    context = {
        'system_snapshots': snapshots
    }
    return render(request, 'charts/cpu_chart.html', context)


@require_POST
def get_chart_for_memory(request):
    snapshots = SystemProcessesSnapshot.objects.all().order_by('created')
    context = {
        'system_snapshots': snapshots
    }
    return render(request, 'charts/memory_chart.html', context)


@require_POST
def get_chart_for_processes(request):
    snapshots = SystemProcessesSnapshot.objects.all().order_by('created')
    context = {
        'system_snapshots': snapshots
    }
    return render(request, 'charts/processes_chart.html', context)
