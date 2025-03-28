from __future__ import annotations

from datetime import datetime
from typing import Optional

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum


class SystemProcessesSnapshot(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    is_system_snapshot = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    #
    # Dzięki poniższej linijce django-stubs „zrozumie”,
    # że SystemProcessesSnapshot ma atrybut `processes`, który jest
    # menedżerem do SingleProcessSnapshot.
    #
    # related_name="processes" => 'self.processes' zwróci wszystkie powiązane SingleProcessSnapshot
    #

    @property
    def get_total_cpu_usage(self) -> float:
        # Tutaj odwołujemy się do self.processes
        result = (
            self.processes.exclude(pid=0)
            .aggregate(total_cpu=Sum('cpu_usage'))
        )
        return float(result['total_cpu']) if result['total_cpu'] else 0.0

    @property
    def get_total_memory_usage(self) -> float:
        result = (
            self.processes.exclude(pid=0)
            .aggregate(total_memory=Sum('memory_usage'))
        )
        total_memory = result['total_memory']
        if total_memory:
            return float(total_memory) / (1024.0 * 1024.0 * 1024.0)
        return 0.0

    @property
    def get_total_processes_count(self) -> int:
        return self.processes.exclude(pid=0).count()

    def __str__(self) -> str:
        return f"Snapshot {self.id} ({self.created})"


class ProcessStatus(models.TextChoices):
    RUNNING = 'running', 'Running'
    SLEEPING = 'sleeping', 'Sleeping'
    ZOMBIE = 'zombie', 'Zombie'
    UNKNOWN = 'unknown', 'Unknown'


class SingleProcessSnapshot(models.Model):
    snapshot = models.ForeignKey(
        SystemProcessesSnapshot,
        on_delete=models.CASCADE,
        related_name='processes',  # Zmieniony related_name
        null=True
    )

    name = models.CharField(max_length=255)
    pid = models.IntegerField()
    status = models.CharField(
        choices=ProcessStatus.choices,
        default=ProcessStatus.UNKNOWN,
        max_length=50
    )
    start_time = models.DateTimeField(null=True)
    duration = models.DurationField()
    memory_usage = models.IntegerField(null=True, blank=True)
    cpu_usage = models.FloatField(null=True, blank=True)

    def formatted_cpu_usage(self) -> str:
        if self.cpu_usage is not None:
            return f"{self.cpu_usage:.2f} %"
        return "0 %"

    def formatted_memory_usage(self) -> str:
        if not self.memory_usage:
            return "0 MB"
        size_in_mb = float(self.memory_usage) / (1024.0 * 1024.0)
        return f"{size_in_mb:.2f} MB"

    @property
    def created(self) -> Optional[datetime]:
        return self.snapshot.created if self.snapshot else None

    class Meta:
        verbose_name = "Single Process Snapshot"
        verbose_name_plural = "Single Process Snapshots"

    def __str__(self) -> str:
        return (f"{self.created} | PID: {self.pid} | "
                f"Name: {self.name} | Status: {self.status}")


class SingleProcessKillRequest(models.Model):
    pid = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=256)
    process_exists = models.BooleanField(default=False)
    process_kill_access = models.BooleanField(default=False)
    killed_successfully = models.BooleanField(default=False)
    message = models.TextField(default="")

    def __str__(self) -> str:
        return f"KillRequest [pid={self.pid}, name={self.name}]"
