from django.urls import path

from process_manager.routes.actions import kill_process, take_snapshot
from process_manager.routes.charts import get_chart_for_cpu, get_chart_for_memory, get_chart_for_processes
from process_manager.routes.exports import export_snapshot_processes
from process_manager.routes.tables import get_processes_table, refresh_processes_table
from process_manager.routes.views import BrowseProcesses, BrowseSnapshots, BrowseKillLogsEntries

urlpatterns = [

    # Views URLs
    path('browse_processes', BrowseProcesses.as_view(), name="browse_processes"),
    path('browse_snapshots', BrowseSnapshots.as_view(), name="browse_snapshots"),
    path('browse_kill_logs', BrowseKillLogsEntries.as_view(), name="browse_kill_logs"),

    # Actions URLs
    path('kill_process/<int:pid>/<str:name>', kill_process, name="kill_process"),
    path('take_snapshot', take_snapshot, name="take_snapshot"),

    # Charts URLs
    path('get_chart_for_cpu/', get_chart_for_cpu, name='get_chart_for_cpu'),
    path('get_chart_for_memory/', get_chart_for_memory, name='get_chart_for_memory'),
    path('get_chart_for_processes/', get_chart_for_processes, name='get_chart_for_processes'),

    # Tables URLs
    path('get_processes_table/<int:pk>', get_processes_table, name='get_processes_table'),
    path('refresh_processes_table', refresh_processes_table, name='refresh_processes_table'),

    # Export URLs
    path('export_snapshot_processes/<int:pk>', export_snapshot_processes, name='export_snapshot_processes'),

]
