"""Tests for cancel command functionality."""

import json
import os
from argparse import Namespace
from pathlib import Path

import pytest

from ticketlog.commands.cancel import cancel_tasks
from ticketlog.config import Config
from ticketlog.models import Task
from ticketlog.storage import Storage


@pytest.fixture
def tmp_storage(tmp_path, monkeypatch):
    """Create a temporary storage with some test tasks."""
    # Change to temp directory so Storage uses the test file
    monkeypatch.chdir(tmp_path)
    
    filepath = tmp_path / "ticketlog.jsonl"
    config = Config(prefix="test")
    storage = Storage(filepath=str(filepath), config=config)
    
    # Create test tasks
    tasks = [
        Task.create("test-001", "Task 1", status="open"),
        Task.create("test-002", "Task 2", status="to_review"),
        Task.create("test-003", "Task 3", status="to_review"),
        Task.create("test-004", "Task 4", status="in_progress"),
        Task.create("test-005", "Task 5", status="to_review", notes="Existing notes"),
    ]
    
    for task in tasks:
        storage.save_task(task)
    
    return storage, filepath


class TestCancelSpecificTasks:
    """Test canceling specific tasks by ID."""
    
    def test_cancel_single_task(self, tmp_storage, capsys):
        storage, filepath = tmp_storage
        
        # Cancel a specific task
        args = Namespace(ids=["test-001"], review=False, reason=None, json=False)
        cancel_tasks(args)
        
        # Verify task was canceled
        storage_reload = Storage(filepath=str(filepath), config=Config(prefix="test"))
        task = storage_reload.get_task_by_id("test-001")
        assert task.status == "closed"
        assert task.notes == "Canceled"
        
        # Check output
        captured = capsys.readouterr()
        assert "Canceled task test-001" in captured.out
    
    def test_cancel_single_task_with_reason(self, tmp_storage, capsys):
        storage, filepath = tmp_storage
        
        # Cancel a specific task with a reason
        args = Namespace(ids=["test-001"], review=False, reason="duplicate of another task", json=False)
        cancel_tasks(args)
        
        # Verify task was canceled with reason
        storage_reload = Storage(filepath=str(filepath), config=Config(prefix="test"))
        task = storage_reload.get_task_by_id("test-001")
        assert task.status == "closed"
        assert task.notes == "Canceled, with reason: duplicate of another task"
        
        # Check output
        captured = capsys.readouterr()
        assert "Canceled task test-001" in captured.out
    
    def test_cancel_task_with_existing_notes(self, tmp_storage, capsys):
        storage, filepath = tmp_storage
        
        # Cancel a task that has existing notes
        args = Namespace(ids=["test-005"], review=False, reason="not needed anymore", json=False)
        cancel_tasks(args)
        
        # Verify task was canceled and notes were appended
        storage_reload = Storage(filepath=str(filepath), config=Config(prefix="test"))
        task = storage_reload.get_task_by_id("test-005")
        assert task.status == "closed"
        assert task.notes == "Existing notes\nCanceled, with reason: not needed anymore"
        
        # Check output
        captured = capsys.readouterr()
        assert "Canceled task test-005" in captured.out
    
    def test_cancel_multiple_tasks(self, tmp_storage, capsys):
        storage, filepath = tmp_storage
        
        # Cancel multiple tasks
        args = Namespace(ids=["test-001", "test-002"], review=False, reason=None, json=False)
        cancel_tasks(args)
        
        # Verify tasks were canceled
        storage_reload = Storage(filepath=str(filepath), config=Config(prefix="test"))
        task1 = storage_reload.get_task_by_id("test-001")
        task2 = storage_reload.get_task_by_id("test-002")
        assert task1.status == "closed"
        assert task1.notes == "Canceled"
        assert task2.status == "closed"
        assert task2.notes == "Canceled"
        
        # Check output
        captured = capsys.readouterr()
        assert "Canceled 2 tasks" in captured.out
    
    def test_cancel_nonexistent_task(self, tmp_storage, capsys):
        storage, filepath = tmp_storage
        
        # Try to cancel nonexistent task
        args = Namespace(ids=["test-999"], review=False, reason=None, json=False)
        cancel_tasks(args)
        
        # Check error message
        captured = capsys.readouterr()
        assert "Error: Task test-999 not found" in captured.out


class TestCancelReview:
    """Test canceling all tasks in to_review status."""
    
    def test_cancel_review_tasks(self, tmp_storage, capsys):
        storage, filepath = tmp_storage
        
        # Cancel all to_review tasks
        args = Namespace(ids=[], review=True, reason=None, json=False)
        cancel_tasks(args)
        
        # Verify all to_review tasks were canceled
        storage_reload = Storage(filepath=str(filepath), config=Config(prefix="test"))
        all_tasks = storage_reload.get_all_tasks()
        
        # Check that the 3 to_review tasks are now closed
        canceled_tasks = [t for t in all_tasks if t.id in ["test-002", "test-003", "test-005"]]
        assert len(canceled_tasks) == 3
        for task in canceled_tasks:
            assert task.status == "closed"
            assert "Canceled" in task.notes
        
        # Other tasks should remain unchanged
        task1 = storage_reload.get_task_by_id("test-001")
        task4 = storage_reload.get_task_by_id("test-004")
        assert task1.status == "open"
        assert task4.status == "in_progress"
        
        # Check output
        captured = capsys.readouterr()
        assert "Canceled 3 tasks" in captured.out
    
    def test_cancel_review_tasks_with_reason(self, tmp_storage, capsys):
        storage, filepath = tmp_storage
        
        # Cancel all to_review tasks with a reason
        args = Namespace(ids=[], review=True, reason="batch cleanup", json=False)
        cancel_tasks(args)
        
        # Verify all to_review tasks were canceled with reason
        storage_reload = Storage(filepath=str(filepath), config=Config(prefix="test"))
        canceled_tasks = [t for t in storage_reload.get_all_tasks() if t.id in ["test-002", "test-003", "test-005"]]
        assert len(canceled_tasks) == 3
        for task in canceled_tasks:
            assert task.status == "closed"
            assert "Canceled, with reason: batch cleanup" in task.notes
    
    def test_cancel_review_no_tasks(self, tmp_path, monkeypatch, capsys):
        # Change to temp directory
        monkeypatch.chdir(tmp_path)
        
        # Create storage with no to_review tasks
        filepath = tmp_path / "ticketlog.jsonl"
        config = Config(prefix="test")
        storage = Storage(filepath=str(filepath), config=config)
        
        tasks = [
            Task.create("test-001", "Task 1", status="open"),
            Task.create("test-002", "Task 2", status="closed"),
        ]
        
        for task in tasks:
            storage.save_task(task)
        
        # Try to cancel all to_review tasks
        args = Namespace(ids=[], review=True, reason=None, json=False)
        cancel_tasks(args)
        
        # Check error message
        captured = capsys.readouterr()
        assert "No tasks found in to_review status" in captured.out
    
    def test_cancel_review_json_output(self, tmp_storage, capsys):
        storage, filepath = tmp_storage
        
        # Cancel all to_review tasks with JSON output
        args = Namespace(ids=[], review=True, reason="cleanup", json=True)
        cancel_tasks(args)
        
        # Check JSON output
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        
        assert len(output) == 3
        assert all(task["status"] == "closed" for task in output)
        assert set(task["id"] for task in output) == {"test-002", "test-003", "test-005"}
        assert all("Canceled, with reason: cleanup" in task["notes"] for task in output)


class TestMutuallyExclusiveOptions:
    """Test that --review and specific IDs are mutually exclusive."""
    
    def test_cannot_use_both_review_and_ids(self, tmp_storage, capsys):
        storage, filepath = tmp_storage
        
        # Try to use both options
        args = Namespace(ids=["test-001"], review=True, reason=None, json=False)
        cancel_tasks(args)
        
        # Check error message
        captured = capsys.readouterr()
        assert "Cannot specify both --review and specific task IDs" in captured.out
        
        # Verify no tasks were canceled
        storage_reload = Storage(filepath=str(filepath), config=Config(prefix="test"))
        task = storage_reload.get_task_by_id("test-001")
        assert task.status == "open"
    
    def test_must_specify_either_option(self, tmp_storage, capsys):
        storage, filepath = tmp_storage
        
        # Try to use neither option
        args = Namespace(ids=[], review=False, reason=None, json=False)
        cancel_tasks(args)
        
        # Check error message
        captured = capsys.readouterr()
        assert "Must specify either --review or at least one task ID" in captured.out
