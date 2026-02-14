"""Tests for version command functionality."""

import json
from argparse import Namespace

import pytest

from ticketlog import __version__
from ticketlog.commands.version import show_version


class TestVersionCommand:
    """Test version command functionality."""

    def test_version_command_text_output(self, capsys):
        """Test version command with text output."""
        args = Namespace(json=False)
        show_version(args)
        
        captured = capsys.readouterr()
        assert f"ticketlog {__version__}" in captured.out
        assert captured.err == ""

    def test_version_command_json_output(self, capsys):
        """Test version command with JSON output."""
        args = Namespace(json=True)
        show_version(args)
        
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["version"] == __version__
        assert captured.err == ""

    def test_version_output_format(self, capsys):
        """Test that version output matches expected format."""
        args = Namespace(json=False)
        show_version(args)
        
        captured = capsys.readouterr()
        # Should be in format "ticketlog X.Y.Z\n"
        assert captured.out.strip().startswith("ticketlog ")
        version_parts = captured.out.strip().split(" ")[1].split(".")
        assert len(version_parts) == 3  # Major.Minor.Patch
