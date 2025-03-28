from django.views.generic import TemplateView

from process_manager.models import SystemProcessesSnapshot, SingleProcessKillRequest


# Create your views here.


class BrowseProcesses(TemplateView):
    template_name = "views/browse_processes.html"
    selected = "browse_processes"

    def get_context_data(self, **kwargs):
        context = super(BrowseProcesses, self).get_context_data(**kwargs)
        return context


class BrowseSnapshots(TemplateView):
    template_name = "views/browse_snapshots.html"
    selected = "browse_snapshots"

    def get_context_data(self, **kwargs):
        context = super(BrowseSnapshots, self).get_context_data(**kwargs)
        context['system_snapshots'] = SystemProcessesSnapshot.objects.all()
        return context


class BrowseKillLogsEntries(TemplateView):
    template_name = "views/browse_kill_logs.html"
    selected = "browse_kill_logs"

    def get_context_data(self, **kwargs):
        context = super(BrowseKillLogsEntries, self).get_context_data(**kwargs)
        context['killed_logs'] = SingleProcessKillRequest.objects.all()
        return context
