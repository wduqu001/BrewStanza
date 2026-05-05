"""Unit tests for ExportManager."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from brewstanza.analyzer.storage import StorageItem, StorageReport
from brewstanza.exporter.export import ExportManager

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


def _make_report(
    homebrew_total: int = 1_000_000,
    apps_total: int = 2_000_000,
) -> StorageReport:
    """Build a minimal but realistic StorageReport for testing."""
    combined = homebrew_total + apps_total
    items: list[StorageItem] = [
        {
            "name": "git",
            "type": "homebrew",
            "size": 500_000,
            "percentage": 500_000 / combined * 100,
        },
        {
            "name": "python@3.11",
            "type": "homebrew",
            "size": 500_000,
            "percentage": 500_000 / combined * 100,
        },
        {
            "name": "Safari.app",
            "type": "app",
            "size": 2_000_000,
            "percentage": 2_000_000 / combined * 100,
        },
    ]
    return {
        "homebrew_total": homebrew_total,
        "apps_total": apps_total,
        "combined_total": combined,
        "items": items,
    }


# ---------------------------------------------------------------------------
# to_json
# ---------------------------------------------------------------------------


class TestToJSON:
    """Tests for ExportManager.to_json()."""

    def test_includes_iso8601_timestamp(self) -> None:
        """The JSON output must include a valid ISO 8601 timestamp."""
        result = json.loads(ExportManager.to_json(_make_report()))
        assert "timestamp" in result
        assert "T" in result["timestamp"]  # ISO 8601 uses 'T' separator

    def test_top_level_fields_present(self) -> None:
        """All expected top-level keys must be present."""
        result = json.loads(ExportManager.to_json(_make_report()))
        for key in (
            "homebrew_total_bytes",
            "homebrew_total_human",
            "apps_total_bytes",
            "apps_total_human",
            "combined_total_bytes",
            "combined_total_human",
            "items",
        ):
            assert key in result, f"Missing key: {key}"

    def test_totals_match_report(self) -> None:
        """Numeric totals must reflect the values in the StorageReport."""
        report = _make_report(homebrew_total=1_000_000, apps_total=2_000_000)
        result = json.loads(ExportManager.to_json(report))
        assert result["homebrew_total_bytes"] == 1_000_000
        assert result["apps_total_bytes"] == 2_000_000
        assert result["combined_total_bytes"] == 3_000_000

    def test_items_have_correct_structure(self) -> None:
        """Each item in the JSON must have name, type, size_bytes, size_human, percentage."""
        result = json.loads(ExportManager.to_json(_make_report()))
        for item in result["items"]:
            assert "name" in item
            assert "type" in item
            assert "size_bytes" in item
            assert "size_human" in item
            assert "percentage" in item

    def test_none_report_returns_empty_snapshot(self) -> None:
        """Passing None should return a valid empty snapshot, not raise."""
        result = json.loads(ExportManager.to_json(None))
        assert result["combined_total_bytes"] == 0
        assert result["items"] == []

    def test_output_is_valid_json(self) -> None:
        """The output must be parseable JSON."""
        raw = ExportManager.to_json(_make_report())
        parsed = json.loads(raw)
        assert isinstance(parsed, dict)


# ---------------------------------------------------------------------------
# to_brewfile
# ---------------------------------------------------------------------------


class TestToBrewfile:
    """Tests for ExportManager.to_brewfile()."""

    def _packages(self) -> list[dict]:  # type: ignore[type-arg]
        return [
            {"name": "git", "version": "2.43.0", "type": "formula"},
            {"name": "python@3.11", "version": "3.11.9", "type": "formula"},
            {"name": "visual-studio-code", "version": "1.88.0", "type": "cask"},
            {"name": "iterm2", "version": "3.5.0", "type": "cask"},
        ]

    def test_contains_brew_lines_for_formulae(self) -> None:
        """Formulae must be emitted as 'brew \"name\"' lines."""
        result = ExportManager.to_brewfile(self._packages())
        assert 'brew "git"' in result
        assert 'brew "python@3.11"' in result

    def test_contains_cask_lines_for_casks(self) -> None:
        """Casks must be emitted as 'cask \"name\"' lines."""
        result = ExportManager.to_brewfile(self._packages())
        assert 'cask "visual-studio-code"' in result
        assert 'cask "iterm2"' in result

    def test_header_comment_present(self) -> None:
        """The file must begin with the BrewStanza header comment."""
        result = ExportManager.to_brewfile(self._packages())
        assert "# Brewfile generated by BrewStanza" in result

    def test_generation_timestamp_present(self) -> None:
        """The header must include a 'Generated at' timestamp line."""
        result = ExportManager.to_brewfile(self._packages())
        assert "# Generated at:" in result

    def test_formulae_sorted_alphabetically(self) -> None:
        """Formulae lines should appear in alphabetical order."""
        result = ExportManager.to_brewfile(self._packages())
        git_pos = result.index('brew "git"')
        python_pos = result.index('brew "python@3.11"')
        assert git_pos < python_pos

    def test_casks_sorted_alphabetically(self) -> None:
        """Cask lines should appear in alphabetical order."""
        result = ExportManager.to_brewfile(self._packages())
        iterm_pos = result.index('cask "iterm2"')
        vscode_pos = result.index('cask "visual-studio-code"')
        assert iterm_pos < vscode_pos

    def test_empty_package_list(self) -> None:
        """An empty package list should return only the header."""
        result = ExportManager.to_brewfile([])
        assert "# Brewfile generated by BrewStanza" in result
        assert "brew " not in result
        assert "cask " not in result

    def test_no_casks_in_list(self) -> None:
        """No cask section should appear when no casks are provided."""
        packages = [{"name": "git", "type": "formula"}]
        result = ExportManager.to_brewfile(packages)
        assert "# Casks" not in result

    def test_no_formulae_in_list(self) -> None:
        """No formulae section should appear when no formulae are provided."""
        packages = [{"name": "iterm2", "type": "cask"}]
        result = ExportManager.to_brewfile(packages)
        assert "# Formulae" not in result


# ---------------------------------------------------------------------------
# write_file
# ---------------------------------------------------------------------------


class TestWriteFile:
    """Tests for ExportManager.write_file()."""

    def test_creates_parent_directories(self) -> None:
        """write_file must create missing parent directories."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "subdir" / "deep" / "test.json"
            ExportManager.write_file("{}", path, overwrite=True)
            assert path.exists()
            assert path.read_text() == "{}"

    def test_overwrites_when_flag_is_true(self) -> None:
        """overwrite=True must replace the existing file without prompting."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            path.write_text("old content")
            ExportManager.write_file("new content", path, overwrite=True)
            assert path.read_text() == "new content"

    def test_prompt_shown_when_file_exists_and_no_overwrite(self) -> None:
        """overwrite=False must call Confirm.ask when the file already exists."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            path.write_text("original")

            with patch("brewstanza.exporter.export.Confirm.ask", return_value=True) as mock_ask:
                ExportManager.write_file("updated", path, overwrite=False)
                mock_ask.assert_called_once()
                assert path.read_text() == "updated"

    def test_no_overwrite_when_user_declines(self) -> None:
        """When the user declines the overwrite prompt the file must be unchanged."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            path.write_text("keep this")

            with patch("brewstanza.exporter.export.Confirm.ask", return_value=False):
                ExportManager.write_file("discard this", path, overwrite=False)
                assert path.read_text() == "keep this"

    def test_no_prompt_for_new_file(self) -> None:
        """No Confirm prompt should be shown when the file doesn't exist yet."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "new_file.json"
            with patch("brewstanza.exporter.export.Confirm.ask") as mock_ask:
                ExportManager.write_file("{}", path, overwrite=False)
                mock_ask.assert_not_called()
            assert path.exists()


# ---------------------------------------------------------------------------
# Integration: to_json round-trip
# ---------------------------------------------------------------------------


class TestJSONRoundTrip:
    """Verifies that to_json produces output parseable by standard tools."""

    def test_json_is_indented(self) -> None:
        """Output should be pretty-printed (indented) for human readability."""
        raw = ExportManager.to_json(_make_report())
        assert "\n" in raw  # at least some line breaks

    def test_percentage_rounded_to_two_decimals(self) -> None:
        """Item percentages must be rounded to 2 decimal places."""
        result = json.loads(ExportManager.to_json(_make_report()))
        for item in result["items"]:
            pct = item["percentage"]
            assert pct == round(pct, 2)
