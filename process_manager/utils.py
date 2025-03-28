from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import psutil
from django.utils import timezone

from process_manager.models import SingleProcessSnapshot, SystemProcessesSnapshot, SingleProcessKillRequest

num_cores = psutil.cpu_count(logical=True) or 1


def fetch_process_children(process: psutil.Process) -> List[Tuple[psutil.Process, bool]]:
    """
    Pobiera bezpośrednich potomków procesu i sprawdza, czy mają oni własne procesy potomne.
    """
    try:
        return [(child, bool(child.children(recursive=False))) for child in process.children(recursive=False)]
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return []


def fetch_process_data(proc: psutil.Process, current_time: datetime) -> Dict[str, Any]:
    """
    Zwraca dane procesu w formie słownika.
    """
    try:
        pid = proc.info['pid']
        status = proc.info['status']
        start_time = timezone.make_aware(datetime.fromtimestamp(proc.info['create_time']))
        duration = timedelta(seconds=int(current_time.timestamp() - proc.info['create_time']))
        name = proc.info['name']
        memory_usage = proc.info['memory_info'].rss
        cpu_usage = proc.cpu_percent(interval=None) / num_cores

        return {
            'pid': pid,
            'status': status,
            'start_time': start_time,
            'duration': duration,
            'name': name,
            'memory_usage': memory_usage,
            'cpu_usage': cpu_usage,
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return {}


def fetch_processes() -> Dict[int, Dict[str, Any]]:
    """
    Zwraca słownik procesów, w którym kluczem jest PID.
    """
    return_dict: Dict[int, Dict[str, Any]] = {}
    processes = list(psutil.process_iter(['pid', 'status', 'create_time', 'name', 'memory_info', 'cpu_percent']))

    # Inicjalizacja CPU bez opóźnienia
    for proc in processes:
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    current_time = timezone.now()

    # Druga pętla po upływie krótkiego czasu na zebranie danych o CPU
    for proc in processes:
        proc_data = fetch_process_data(proc, current_time)
        if proc_data:
            return_dict[proc_data['pid']] = proc_data

    return return_dict


def create_processes_snapshot(processes_data: Dict[int, Dict[str, Any]],
                              user: Optional[Any] = None) -> SystemProcessesSnapshot:
    """
    Tworzy zrzut procesów w modelu SingleProcessSnapshot poprzez batch create.
    """
    system_snapshot = SystemProcessesSnapshot.objects.create(
        user=user) if user else SystemProcessesSnapshot.objects.create(is_system_snapshot=True)

    snapshots_to_create = [
        SingleProcessSnapshot(
            snapshot=system_snapshot,
            pid=proc_info['pid'],
            status=proc_info['status'],
            start_time=proc_info['start_time'],
            duration=proc_info['duration'],
            name=proc_info['name'],
            memory_usage=proc_info['memory_usage'],
            cpu_usage=proc_info['cpu_usage'],
        )
        for proc_info in processes_data.values()
    ]

    SingleProcessSnapshot.objects.bulk_create(snapshots_to_create)
    return system_snapshot


def kill_the_process(pid: int, name: str) -> Tuple[bool, str]:
    try:
        proc = psutil.Process(pid)
        try:
            proc_name = proc.name()
        except psutil.AccessDenied:
            return False, "Access denied to process details"
        # Sprawdzamy, czy nazwa procesu zgadza się z podaną
        if proc_name == name:
            try:
                # proc.kill()  # Zabijamy proces
                pass
            except psutil.AccessDenied:
                return False, "Access denied to kill process"
            return True, f"Killed successfully (PID: {pid})"
        else:
            return False, "Process name mismatch"
    except psutil.NoSuchProcess:
        return False, "Process not found"
    except Exception as e:
        return False, f"Error: {e}"


def kill_process_and_log(pid: int, name: str, author: Optional[Any] = None) -> Tuple[bool, str]:
    # Próba zabicia procesu
    success, message = kill_the_process(pid, name)

    # Ustalenie statusu na podstawie komunikatu
    process_exists = message not in ("Process not found",)
    process_kill_access = "Access denied" not in message

    # Utworzenie i zapisanie obiektu SingleProcessKillRequest
    log_entry = SingleProcessKillRequest(
        pid=pid,
        author=author,
        name=name,
        process_exists=process_exists,
        process_kill_access=process_kill_access,
        killed_successfully=success,
        message=message
    )
    log_entry.save()

    return success, message