"""Tests for dead history warning feature."""

import json
import sys
from pathlib import Path

import pytest

from ticketlog.config import Config
from ticketlog.models import Task
from ticketlog.storage import Storage


@pytest.fixture
def tmp_jsonl(tmp_path):
    """Return a helper that writes tasks to a temp JSONL file and returns a Storage."""
    filepath = tmp_path / "ticketlog.jsonl"

    def _make_storage(lines, threshold=0.3):
        filepath.write_text("".join(json.dumps(line) + "\n" for line in lines))
        config = Config(dead_history_threshold=threshold)
        return Storage(filepath=str(filepath), config=config)

    return _make_storage


def _task_dict(task_id="tl-abc", title="Test task", **overrides):
    """Build a minimal task dict."""
    base = {
        "id": task_id,
        "title": title,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
    }
    base.update(overrides)
    return base


class TestDeadHistoryRatio:
    def test_empty_file_ratio_is_zero(self, tmp_path):
        filepath = tmp_path / "ticketlog.jsonl"
        filepath.write_text("")
        storage = Storage(filepath=str(filepath))
        storage.load_tasks()
        assert storage.dead_history_ratio == 0.0

    def test_no_file_ratio_is_zero(self, tmp_path):
        filepath = tmp_path / "ticketlog.jsonl"
        storage = Storage(filepath=str(filepath))
        storage.load_tasks()
        assert storage.dead_history_ratio == 0.0

    def test_no_duplicates_ratio_is_zero(self, tmp_jsonl):
        storage = tmp_jsonl([
            _task_dict("tl-001"),
            _task_dict("tl-002"),
            _task_dict("tl-003"),
        ])
        storage.load_tasks()
        assert storage.dead_history_ratio == 0.0

    def test_all_duplicates(self, tmp_jsonl):
        storage = tmp_jsonl([
            _task_dict("tl-001", title="v1"),
            _task_dict("tl-001", title="v2"),
            _task_dict("tl-001", title="v3"),
        ])
        tasks = storage.load_tasks()
        # 3 lines, 1 unique → ratio = 2/3
        assert len(tasks) == 1
        assert tasks[0].title == "v3"
        assert storage.dead_history_ratio == pytest.approx(2 / 3)

    def test_mixed_duplicates(self, tmp_jsonl):
        storage = tmp_jsonl([
            _task_dict("tl-001", title="v1"),
            _task_dict("tl-002"),
            _task_dict("tl-001", title="v2"),
            _task_dict("tl-003"),
        ])
        storage.load_tasks()
        # 4 lines, 3 unique → ratio = 1/4
        assert storage.dead_history_ratio == pytest.approx(0.25)


class TestCheckDeadHistory:
    def test_warns_when_above_threshold(self, tmp_jsonl, capsys):
        storage = tmp_jsonl([
            _task_dict("tl-001", title="v1"),
            _task_dict("tl-001", title="v2"),
            _task_dict("tl-001", title="v3"),
            _task_dict("tl-001", title="v4"),
        ], threshold=0.3)
        storage.load_tasks()
        storage.check_dead_history()

        captured = capsys.readouterr()
        assert "dead history" in captured.err
        assert "tl clean" in captured.err
        assert "75.0%" in captured.err

    def test_no_warning_below_threshold(self, tmp_jsonl, capsys):
        storage = tmp_jsonl([
            _task_dict("tl-001"),
            _task_dict("tl-002"),
            _task_dict("tl-003"),
            _task_dict("tl-001", title="v2"),
        ], threshold=0.3)
        storage.load_tasks()
        # ratio = 1/4 = 0.25, threshold = 0.3
        storage.check_dead_history()

        captured = capsys.readouterr()
        assert captured.err == ""

    def test_no_warning_at_exact_threshold(self, tmp_jsonl, capsys):
        # ratio must exceed threshold, not equal it
        storage = tmp_jsonl([
            _task_dict("tl-001", title="v1"),
            _task_dict("tl-002"),
            _task_dict("tl-001", title="v2"),
        ], threshold=1 / 3)
        storage.load_tasks()
        # ratio = 1/3, threshold = 1/3 → no warning
        storage.check_dead_history()

        captured = capsys.readouterr()
        assert captured.err == ""

    def test_warns_only_once(self, tmp_jsonl, capsys):
        storage = tmp_jsonl([
            _task_dict("tl-001", title="v1"),
            _task_dict("tl-001", title="v2"),
            _task_dict("tl-001", title="v3"),
        ], threshold=0.3)
        storage.load_tasks()
        storage.check_dead_history()
        storage.check_dead_history()
        storage.check_dead_history()

        captured = capsys.readouterr()
        # Warning should appear exactly once
        assert captured.err.count("dead history") == 1

    def test_custom_threshold(self, tmp_jsonl, capsys):
        storage = tmp_jsonl([
            _task_dict("tl-001", title="v1"),
            _task_dict("tl-001", title="v2"),
            _task_dict("tl-001", title="v3"),
        ], threshold=0.9)
        storage.load_tasks()
        # ratio = 2/3 ≈ 0.67, threshold = 0.9 → no warning
        storage.check_dead_history()

        captured = capsys.readouterr()
        assert captured.err == ""

    def test_warning_includes_threshold_pct(self, tmp_jsonl, capsys):
        storage = tmp_jsonl([
            _task_dict("tl-001", title="v1"),
            _task_dict("tl-001", title="v2"),
        ], threshold=0.3)
        storage.load_tasks()
        storage.check_dead_history()

        captured = capsys.readouterr()
        assert "30%" in captured.err


class TestConfigDeadHistoryThreshold:
    def test_default_threshold(self):
        config = Config()
        assert config.dead_history_threshold == 0.3

    def test_from_file_reads_threshold(self, tmp_path):
        toml_file = tmp_path / ".ticketlog.toml"
        toml_file.write_text('[project]\nprefix = "xx"\ndead_history_threshold = 0.5\n')
        config = Config.from_file(toml_file)
        assert config.dead_history_threshold == 0.5

    def test_from_file_default_when_missing(self, tmp_path):
        toml_file = tmp_path / ".ticketlog.toml"
        toml_file.write_text('[project]\nprefix = "xx"\n')
        config = Config.from_file(toml_file)
        assert config.dead_history_threshold == 0.3
