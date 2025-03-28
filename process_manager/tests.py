# tests/test_utils.py

from datetime import timedelta
from unittest.mock import patch, MagicMock

import psutil
from django.test import TestCase
from django.utils import timezone

from process_manager.models import SingleProcessSnapshot, SystemProcessesSnapshot
from process_manager.utils import (
    fetch_process_children,
    fetch_process_data,
    fetch_processes,
    create_processes_snapshot,
    num_cores
)


class TestUtils(TestCase):
    def setUp(self):
        self.now = timezone.now()

    def test_fetch_process_children_success(self):
        """
        Sprawdzamy, czy funkcja zwraca listę krotek (proces potomny, bool informujący o istnieniu
        kolejnych dzieci), ustawiając metodę children tylko dla instancji rodzica.
        """
        # Utwórz instancję rodzica oraz dwóch procesów potomnych
        parent_process = MagicMock(spec=psutil.Process)
        child_process_1 = MagicMock(spec=psutil.Process)
        child_process_2 = MagicMock(spec=psutil.Process)
        # Ustaw dla potomków metodę children zwracającą konkretne wyniki
        child_process_1.children.return_value = []
        child_process_2.children.return_value = [MagicMock(spec=psutil.Process)]
        # Przypisz metodę children tylko do rodzica
        parent_process.children = MagicMock(return_value=[child_process_1, child_process_2])

        results = fetch_process_children(parent_process)
        parent_process.children.assert_called_with(recursive=False)
        self.assertEqual(len(results), 2)
        self.assertFalse(results[0][1])  # child_process_1 nie ma dzieci
        self.assertTrue(results[1][1])  # child_process_2 ma dzieci

    def test_fetch_process_children_access_denied(self):
        """
        W przypadku wystąpienia AccessDenied funkcja ma zwrócić pustą listę.
        """
        parent_process = MagicMock(spec=psutil.Process)
        parent_process.children.side_effect = psutil.AccessDenied(pid=9999)
        results = fetch_process_children(parent_process)
        self.assertEqual(results, [])

    def test_fetch_process_data_success(self):
        """
        Sprawdzamy poprawne pobranie danych o procesie.
        """
        process_mock = MagicMock(spec=psutil.Process)
        process_mock.info = {
            'pid': 1234,
            'status': 'running',
            'create_time': (self.now - timedelta(seconds=100)).timestamp(),
            'name': 'test_process',
            'memory_info': MagicMock(rss=2048),
        }
        # Ustawiamy metodę cpu_percent dla tej instancji
        process_mock.cpu_percent.return_value = 50.0

        result = fetch_process_data(process_mock, self.now)

        self.assertIsNotNone(result)
        self.assertEqual(result['pid'], 1234)
        self.assertEqual(result['status'], 'running')
        self.assertEqual(result['name'], 'test_process')
        self.assertEqual(result['memory_usage'], 2048)
        expected_cpu_usage = 50.0 / num_cores
        self.assertAlmostEqual(result['cpu_usage'], expected_cpu_usage)
        self.assertTrue(isinstance(result['duration'], timedelta))
        self.assertEqual(result['duration'].total_seconds(), 100)

    def test_fetch_process_data_access_denied(self):
        """
        Jeśli metoda cpu_percent rzuci wyjątek AccessDenied, funkcja powinna zwrócić pusty słownik.
        """
        process_mock = MagicMock(spec=psutil.Process)
        process_mock.info = {
            'pid': 9999,
            'status': 'running',
            'create_time': self.now.timestamp(),
            'name': 'test_process',
            'memory_info': MagicMock(rss=2048),
        }
        process_mock.cpu_percent.side_effect = psutil.AccessDenied(pid=9999)

        result = fetch_process_data(process_mock, self.now)
        self.assertEqual(result, {})

    def test_fetch_processes_success(self):
        """
        Sprawdzamy, czy funkcja fetch_processes zwraca słownik procesów, gdzie klucze to PID.
        """
        # Przygotowujemy dwa mockowane procesy
        proc_1 = MagicMock(spec=psutil.Process)
        proc_1.info = {
            'pid': 1,
            'status': 'running',
            'create_time': (self.now - timedelta(seconds=10)).timestamp(),
            'name': 'proc1',
            'memory_info': MagicMock(rss=1024),
            'cpu_percent': 10.0
        }
        proc_2 = MagicMock(spec=psutil.Process)
        proc_2.info = {
            'pid': 2,
            'status': 'sleeping',
            'create_time': (self.now - timedelta(seconds=20)).timestamp(),
            'name': 'proc2',
            'memory_info': MagicMock(rss=2048),
            'cpu_percent': 20.0
        }
        proc_1.cpu_percent.return_value = 10.0
        proc_2.cpu_percent.return_value = 20.0

        with patch("psutil.process_iter", return_value=[proc_1, proc_2]):
            processes = fetch_processes()

        self.assertEqual(len(processes), 2)
        self.assertIn(1, processes)
        self.assertIn(2, processes)
        self.assertEqual(processes[1]['name'], 'proc1')
        self.assertEqual(processes[2]['status'], 'sleeping')
        self.assertEqual(processes[1]['memory_usage'], 1024)

    def test_fetch_processes_access_denied(self):
        """
        Symulujemy sytuację, w której jeden z procesów przy próbie pobrania cpu_percent rzuca wyjątek AccessDenied.
        Powinien być on pominięty, a pozostałe procesy powinny zostać przetworzone.
        """
        proc_bad = MagicMock(spec=psutil.Process)
        proc_bad.info = {
            'pid': 9999,
            'status': 'running',
            'create_time': self.now.timestamp(),
            'name': 'bad_process',
            'memory_info': MagicMock(rss=2048),
            'cpu_percent': 0,
        }
        proc_bad.cpu_percent.side_effect = psutil.AccessDenied(pid=9999)

        proc_good = MagicMock(spec=psutil.Process)
        proc_good.info = {
            'pid': 1000,
            'status': 'running',
            'create_time': (self.now - timedelta(seconds=100)).timestamp(),
            'name': 'good_process',
            'memory_info': MagicMock(rss=4096),
            'cpu_percent': 10.0,
        }
        proc_good.cpu_percent.return_value = 10.0

        with patch("psutil.process_iter", return_value=[proc_bad, proc_good]):
            processes = fetch_processes()
        # Oczekujemy, że proces problematyczny zostanie pominięty
        self.assertEqual(len(processes), 1)
        self.assertIn(1000, processes)

    def test_create_processes_snapshot_no_user(self):
        """
        Test tworzenia snapshotu systemowego (bez usera) i sprawdzenie, czy tworzone są odpowiednie
        instancje SingleProcessSnapshot.
        """
        processes_data = {
            1: {
                'pid': 1,
                'status': 'running',
                'start_time': self.now - timedelta(seconds=10),
                'duration': timedelta(seconds=10),
                'name': 'proc1',
                'memory_usage': 12345,
                'cpu_usage': 5.0,
            },
            2: {
                'pid': 2,
                'status': 'sleeping',
                'start_time': self.now - timedelta(seconds=20),
                'duration': timedelta(seconds=20),
                'name': 'proc2',
                'memory_usage': 23456,
                'cpu_usage': 10.0,
            },
        }

        snapshot = create_processes_snapshot(processes_data)
        self.assertEqual(SystemProcessesSnapshot.objects.count(), 1)
        self.assertEqual(SingleProcessSnapshot.objects.count(), 2)
        self.assertTrue(snapshot.is_system_snapshot)
        self.assertIsNone(snapshot.user)

        proc_snapshots = SingleProcessSnapshot.objects.all().order_by('pid')
        self.assertEqual(proc_snapshots[0].pid, 1)
        self.assertEqual(proc_snapshots[0].name, 'proc1')
        self.assertEqual(proc_snapshots[0].cpu_usage, 5.0)
        self.assertEqual(proc_snapshots[1].pid, 2)
        self.assertEqual(proc_snapshots[1].name, 'proc2')
        self.assertEqual(proc_snapshots[1].cpu_usage, 10.0)

    def test_create_processes_snapshot_with_user(self):
        """
        Test tworzenia snapshotu z przekazanym użytkownikiem – pole user powinno być ustawione, a
        is_system_snapshot powinno być False.
        """
        from django.contrib.auth.models import User
        user = User.objects.create(username='testuser', password='testpass')

        processes_data = {
            10: {
                'pid': 10,
                'status': 'running',
                'start_time': self.now - timedelta(seconds=5),
                'duration': timedelta(seconds=5),
                'name': 'proc10',
                'memory_usage': 9999,
                'cpu_usage': 2.0,
            },
        }

        snapshot = create_processes_snapshot(processes_data, user=user)
        self.assertEqual(SystemProcessesSnapshot.objects.count(), 1)
        self.assertEqual(SingleProcessSnapshot.objects.count(), 1)
        self.assertEqual(snapshot.user, user)
        self.assertFalse(snapshot.is_system_snapshot)

        proc_snapshot = SingleProcessSnapshot.objects.first()
        self.assertEqual(proc_snapshot.pid, 10)
        self.assertEqual(proc_snapshot.name, 'proc10')
