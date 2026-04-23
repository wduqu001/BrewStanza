"""Unit tests for ExportManager."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from brewstanza.exporter.export import ExportManager


class TestExportManagerJSON:
    """Tests for JSON export functionality."""

    def test_to_json_includes_timestamp(self) -> None:
        """JSON output should include an ISO 8601 timestamp."""
        # TODO: Mock a StorageReport fixture and verify timestamp is present
        result = ExportManager.to_json(None)  # placeholder
        data = json.loads(result)
        assert "timestamp" in data
        # Verify ISO 8601 format (basic check)
        assert "T" in data["timestamp"]

    def test_to_json_structure(self) -> None:
        """JSON output should have correct structure with totals and items."""
        # TODO: Implement with proper StorageReport fixture
        result = ExportManager.to_json(None)  # placeholder
        data = json.loads(result)
        assert "homebrew_total" in data
        assert "apps_total" in data
        assert "combined_total" in data
        assert "items" in data


class TestExportManagerBrewfile:
    """Tests for Brewfile export functionality."""

    def test_to_brewfile_format(self) -> None:
        """Brewfile should use standard brew bundle syntax."""
        packages: list[dict[str, Any]] = []
        result = ExportManager.to_brewfile(packages)
        # TODO: Add assertions for Brewfile format compliance
        assert isinstance(result, str)
        assert "Brewfile" in result or len(result) > 0


class TestExportManagerWriteFile:
    """Tests for file writing functionality."""

    def test_write_file_creates_directory(self) -> None:
        """write_file should create parent directories if missing."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "subdir" / "test.json"
            ExportManager.write_file("{}", path, overwrite=True)
            assert path.exists()
            assert path.read_text() == "{}"

    def test_write_file_respects_overwrite_flag(self) -> None:
        """write_file with overwrite=True should replace existing file."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            path.write_text("old")
            ExportManager.write_file("new", path, overwrite=True)
            assert path.read_text() == "new"
