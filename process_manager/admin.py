from django.contrib import admin

from process_manager.models import SingleProcessSnapshot, SystemProcessesSnapshot, SingleProcessKillRequest


# Register your models here.


# Add to admin
@admin.register(SingleProcessSnapshot)
class SingleProcessSnapshotAdmin(admin.ModelAdmin):
    list_display = ('snapshot', 'name', 'pid', 'status', 'memory_usage', 'cpu_usage')


class SingleProcessSnapshotInline(admin.TabularInline):
    model = SingleProcessSnapshot
    extra = 0  # brak dodatkowych pustych formularzy
    ordering = ('-cpu_usage',)
    exclude = ('cpu_usage', 'memory_usage')
    readonly_fields = (
        'start_time', 'duration', 'snapshot', 'name', 'pid', 'status', 'display_memory_usage', 'display_cpu_usage'
    )
    can_delete = False

    @admin.display(description='CPU usage')
    def display_cpu_usage(self, obj):
        return obj.formatted_cpu_usage()

    @admin.display(description='Memory usage')
    def display_memory_usage(self, obj):
        return obj.formatted_memory_usage()


@admin.register(SystemProcessesSnapshot)
class SystemProcessesSnapshotAdmin(admin.ModelAdmin):
    list_display = ['display_total_usage', 'created', 'user']
    inlines = [SingleProcessSnapshotInline]

    @admin.display(description='Total CPU usage')
    def display_total_usage(self, obj):
        return f"{obj.get_total_cpu_usage:.2f} %"


@admin.register(SingleProcessKillRequest)
class SingleProcessKillRequestAdmin(admin.ModelAdmin):
    pass
