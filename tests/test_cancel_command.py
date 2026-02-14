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
        args = Namespace(ids=["test-001"], reason=None, json=False)
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
        args = Namespace(ids=["test-001"], reason="duplicate of another task", json=False)
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
        args = Namespace(ids=["test-005"], reason="not needed anymore", json=False)
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
        args = Namespace(ids=["test-001", "test-002"], reason=None, json=False)
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
        args = Namespace(ids=["test-999"], reason=None, json=False)
        cancel_tasks(args)
        
        # Check error message
        captured = capsys.readouterr()
        assert "Error: Task test-999 not found" in captured.out
    
    def test_cancel_no_task_ids(self, tmp_storage, capsys):
        storage, filepath = tmp_storage
        
        # Try to cancel without providing task IDs
        args = Namespace(ids=[], reason=None, json=False)
        cancel_tasks(args)
        
        # Check error message
        captured = capsys.readouterr()
        assert "Must specify at least one task ID" in captured.out

