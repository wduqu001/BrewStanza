"""
Extended CLI tests — covers commands not exercised by the existing test_cli.py.

All external I/O (brew, disk scanning) is mocked so tests run offline and fast.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from brewstanza.cli import main
from brewstanza.scanner.disk import ScanResult, ScanSummary

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _empty_summary(**kwargs: object) -> MagicMock:
    """Return a mock ScanSummary with no results."""
    m = MagicMock(spec=ScanSummary)
    m.results = []
    m.failed_paths = []
    m.total_bytes = 0
    return m


def _summary_with(*results: ScanResult) -> MagicMock:
    """Return a mock ScanSummary pre-loaded with the given ScanResults."""
    m = MagicMock(spec=ScanSummary)
    m.results = list(results)
    m.failed_paths = []
    m.total_bytes = sum(r.size_bytes for r in results)
    return m


# ---------------------------------------------------------------------------
# brew list
# ---------------------------------------------------------------------------


class TestBrewList:
    """Tests for `brewstanza brew list`."""

    def _brew_info_fixture(self) -> dict:  # type: ignore[type-arg]
        return {
            "formulae": [{"name": "git", "installed": [{"version": "2.43.0"}]}],
            "casks": [{"token": "iterm2", "installed": "3.5.0"}],
        }

    @patch("brewstanza.cli.scan_paths")
    @patch("brewstanza.cli.HomebrewScanner")
    def test_brew_list_table_output(
        self, mock_scanner: MagicMock, mock_scan: MagicMock
    ) -> None:
        """Default output renders a table (not JSON)."""
        inst = mock_scanner.return_value
        inst.get_all_installed_info.return_value = self._brew_info_fixture()
        inst.get_outdated.return_value = []
        inst._run_brew_command.return_value = "/opt/homebrew/Cellar"
        mock_scan.return_value = _summary_with(
            ScanResult(path=Path("/opt/homebrew/Cellar/git/2.43.0"), size_bytes=1024 * 1024),
            ScanResult(path=Path("/opt/homebrew/Caskroom/iterm2"), size_bytes=2048 * 1024),
        )

        result = CliRunner().invoke(main, ["brew", "list"])
        assert result.exit_code == 0
        assert "git" in result.output

    @patch("brewstanza.cli.scan_paths")
    @patch("brewstanza.cli.HomebrewScanner")
    def test_brew_list_formula_only(
        self, mock_scanner: MagicMock, mock_scan: MagicMock
    ) -> None:
        """--formula flag excludes casks."""
        inst = mock_scanner.return_value
        inst.get_all_installed_info.return_value = self._brew_info_fixture()
        inst.get_outdated.return_value = []
        inst._run_brew_command.return_value = "/opt/homebrew/Cellar"
        mock_scan.return_value = _summary_with(
            ScanResult(path=Path("/opt/homebrew/Cellar/git/2.43.0"), size_bytes=512)
        )

        result = CliRunner().invoke(main, ["brew", "list", "--formula", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        names = [p["name"] for p in data]
        assert "git" in names
        assert "iterm2" not in names

    @patch("brewstanza.cli.scan_paths")
    @patch("brewstanza.cli.HomebrewScanner")
    def test_brew_list_cask_only(
        self, mock_scanner: MagicMock, mock_scan: MagicMock
    ) -> None:
        """--cask flag excludes formulae."""
        inst = mock_scanner.return_value
        inst.get_all_installed_info.return_value = self._brew_info_fixture()
        inst.get_outdated.return_value = []
        inst._run_brew_command.return_value = "/opt/homebrew"
        mock_scan.return_value = _summary_with(
            ScanResult(path=Path("/opt/homebrew/Caskroom/iterm2"), size_bytes=512)
        )

        result = CliRunner().invoke(main, ["brew", "list", "--cask", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        names = [p["name"] for p in data]
        assert "iterm2" in names
        assert "git" not in names

    @patch("brewstanza.cli.scan_paths")
    @patch("brewstanza.cli.HomebrewScanner")
    def test_brew_list_marks_outdated(
        self, mock_scanner: MagicMock, mock_scan: MagicMock
    ) -> None:
        """Packages in get_outdated() appear as outdated=True in JSON."""
        inst = mock_scanner.return_value
        inst.get_all_installed_info.return_value = {
            "formulae": [{"name": "wget", "installed": [{"version": "1.21"}]}],
            "casks": [],
        }
        inst.get_outdated.return_value = ["wget"]
        inst._run_brew_command.return_value = "/opt/homebrew/Cellar"
        mock_scan.return_value = _summary_with(
            ScanResult(path=Path("/opt/homebrew/Cellar/wget/1.21"), size_bytes=100)
        )

        result = CliRunner().invoke(main, ["brew", "list", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        wget_entry = next(p for p in data if p["name"] == "wget")
        assert wget_entry["outdated"] is True

    @patch("brewstanza.cli.scan_paths")
    @patch("brewstanza.cli.HomebrewScanner")
    def test_brew_list_cask_info(
        self, mock_scanner: MagicMock, mock_scan: MagicMock
    ) -> None:
        """Cask info is rendered in brew info when the formula list is empty."""
        inst = mock_scanner.return_value
        inst.get_info.return_value = {
            "formulae": [],
            "casks": [{"token": "firefox", "desc": "Web browser", "version": "125.0"}],
        }
        inst._run_brew_command.return_value = "/opt/homebrew"
        mock_scan.return_value = MagicMock(total_bytes=50_000_000)

        result = CliRunner().invoke(main, ["brew", "info", "firefox"])
        assert result.exit_code == 0
        assert "firefox" in result.output


# ---------------------------------------------------------------------------
# brew outdated
# ---------------------------------------------------------------------------


class TestBrewOutdated:
    """Tests for `brewstanza brew outdated`."""

    @patch("brewstanza.cli.HomebrewScanner")
    def test_outdated_lists_packages(self, mock_scanner: MagicMock) -> None:
        mock_scanner.return_value.get_outdated.return_value = ["wget", "curl"]
        result = CliRunner().invoke(main, ["brew", "outdated"])
        assert result.exit_code == 0
        assert "wget" in result.output
        assert "curl" in result.output

    @patch("brewstanza.cli.HomebrewScanner")
    def test_outdated_shows_uptodate_message(self, mock_scanner: MagicMock) -> None:
        mock_scanner.return_value.get_outdated.return_value = []
        result = CliRunner().invoke(main, ["brew", "outdated"])
        assert result.exit_code == 0
        assert "up to date" in result.output

    @patch("brewstanza.cli.scan_paths")
    @patch("brewstanza.cli.HomebrewScanner")
    def test_brew_info_package_not_found(
        self, mock_scanner: MagicMock, mock_scan: MagicMock
    ) -> None:
        """brew info with empty formulae and casks shows an error."""
        inst = mock_scanner.return_value
        inst.get_info.return_value = {"formulae": [], "casks": []}
        result = CliRunner().invoke(main, ["brew", "info", "nosuchpkg"])
        assert result.exit_code == 0
        assert "not found" in result.output.lower() or "✗" in result.output

    @patch("brewstanza.cli.HomebrewScanner")
    def test_brew_info_runtime_error(self, mock_scanner: MagicMock) -> None:
        """brew info surfaces RuntimeError as an error message."""
        mock_scanner.return_value.get_info.side_effect = RuntimeError("brew failed")
        result = CliRunner().invoke(main, ["brew", "info", "nosuchpkg"])
        assert result.exit_code == 0
        assert "brew failed" in result.output


# ---------------------------------------------------------------------------
# apps list (table rendering path)
# ---------------------------------------------------------------------------


class TestAppsList:
    """Tests for `brewstanza apps list` (table output path)."""

    @patch("brewstanza.cli.scan_paths")
    @patch("brewstanza.cli.AppScanner")
    def test_apps_list_renders_table(
        self, mock_scanner: MagicMock, mock_scan: MagicMock
    ) -> None:
        """Default output (no --json) renders a table."""
        inst = mock_scanner.return_value
        inst.collect_app_paths.return_value = [Path("/Applications/Safari.app")]
        mock_scan.return_value = _summary_with(
            ScanResult(path=Path("/Applications/Safari.app"), size_bytes=50_000_000)
        )

        result = CliRunner().invoke(main, ["apps", "list"])
        assert result.exit_code == 0
        assert "Safari" in result.output

    @patch("brewstanza.cli.AppScanner")
    def test_apps_info_not_found(self, mock_scanner: MagicMock) -> None:
        """apps info shows error when app is not in the scanned list."""
        mock_scanner.return_value.collect_app_paths.return_value = []
        result = CliRunner().invoke(main, ["apps", "info", "NoSuchApp"])
        assert result.exit_code == 0
        assert "not found" in result.output.lower() or "✗" in result.output


# ---------------------------------------------------------------------------
# storage (table rendering path)
# ---------------------------------------------------------------------------


class TestStorage:
    """Tests for `brewstanza storage` (Rich table output path)."""

    @patch("brewstanza.cli.scan_paths")
    @patch("brewstanza.cli.AppScanner")
    @patch("brewstanza.cli.HomebrewScanner")
    def test_storage_renders_table(
        self,
        mock_brew: MagicMock,
        mock_app: MagicMock,
        mock_scan: MagicMock,
    ) -> None:
        """Default output renders a Rich breakdown panel."""
        brew_inst = mock_brew.return_value
        brew_inst.get_all_installed_info.return_value = {"formulae": [], "casks": []}
        brew_inst._run_brew_command.return_value = "/opt/homebrew/Cellar"
        mock_app.return_value.collect_app_paths.return_value = []
        mock_scan.return_value = _empty_summary()

        result = CliRunner().invoke(main, ["storage"])
        assert result.exit_code == 0
        # The storage breakdown panel should mention totals
        assert "Storage" in result.output or "Homebrew" in result.output


# ---------------------------------------------------------------------------
# export json
# ---------------------------------------------------------------------------


class TestExportJSON:
    """Tests for `brewstanza export json`."""

    @patch("brewstanza.cli.ExportManager")
    @patch("brewstanza.cli.scan_paths")
    @patch("brewstanza.cli.AppScanner")
    @patch("brewstanza.cli.HomebrewScanner")
    def test_export_json_writes_file(
        self,
        mock_brew: MagicMock,
        mock_app: MagicMock,
        mock_scan: MagicMock,
        mock_exporter: MagicMock,
    ) -> None:
        """export json should call ExportManager.to_json and write_file."""
        brew_inst = mock_brew.return_value
        brew_inst.get_all_installed_info.return_value = {"formulae": [], "casks": []}
        brew_inst._run_brew_command.return_value = "/opt/homebrew/Cellar"
        mock_app.return_value.collect_app_paths.return_value = []
        mock_scan.return_value = _empty_summary()
        mock_exporter.to_json.return_value = "{}"
        mock_exporter.write_file.return_value = None

        result = CliRunner().invoke(main, ["export", "json"])
        assert result.exit_code == 0
        mock_exporter.to_json.assert_called_once()
        mock_exporter.write_file.assert_called_once()

    @patch("brewstanza.cli.ExportManager")
    @patch("brewstanza.cli.scan_paths")
    @patch("brewstanza.cli.AppScanner")
    @patch("brewstanza.cli.HomebrewScanner")
    def test_export_json_custom_output_path(
        self,
        mock_brew: MagicMock,
        mock_app: MagicMock,
        mock_scan: MagicMock,
        mock_exporter: MagicMock,
    ) -> None:
        """--output flag should be passed as the destination path."""
        brew_inst = mock_brew.return_value
        brew_inst.get_all_installed_info.return_value = {"formulae": [], "casks": []}
        brew_inst._run_brew_command.return_value = "/opt/homebrew/Cellar"
        mock_app.return_value.collect_app_paths.return_value = []
        mock_scan.return_value = _empty_summary()
        mock_exporter.to_json.return_value = "{}"
        mock_exporter.write_file.return_value = None

        result = CliRunner().invoke(main, ["export", "json", "--output", "custom.json"])
        assert result.exit_code == 0
        call_args = mock_exporter.write_file.call_args
        assert "custom.json" in str(call_args)


# ---------------------------------------------------------------------------
# export brewfile
# ---------------------------------------------------------------------------


class TestExportBrewfile:
    """Tests for `brewstanza export brewfile`."""

    @patch("brewstanza.cli.ExportManager")
    @patch("brewstanza.cli.HomebrewScanner")
    def test_export_brewfile_writes_file(
        self, mock_brew: MagicMock, mock_exporter: MagicMock
    ) -> None:
        """export brewfile should call ExportManager.to_brewfile and write_file."""
        brew_inst = mock_brew.return_value
        brew_inst.get_all_installed_info.return_value = {
            "formulae": [{"name": "git", "installed": [{"version": "2.43"}]}],
            "casks": [{"token": "iterm2", "installed": "3.5"}],
        }
        mock_exporter.to_brewfile.return_value = 'brew "git"\ncask "iterm2"\n'
        mock_exporter.write_file.return_value = None

        result = CliRunner().invoke(main, ["export", "brewfile"])
        assert result.exit_code == 0
        mock_exporter.to_brewfile.assert_called_once()
        mock_exporter.write_file.assert_called_once()

    @patch("brewstanza.cli.ExportManager")
    @patch("brewstanza.cli.HomebrewScanner")
    def test_export_brewfile_custom_output(
        self, mock_brew: MagicMock, mock_exporter: MagicMock
    ) -> None:
        """--output flag is forwarded to write_file."""
        brew_inst = mock_brew.return_value
        brew_inst.get_all_installed_info.return_value = {"formulae": [], "casks": []}
        mock_exporter.to_brewfile.return_value = ""
        mock_exporter.write_file.return_value = None

        result = CliRunner().invoke(
            main, ["export", "brewfile", "--output", "MyBrewfile"]
        )
        assert result.exit_code == 0
        call_args = mock_exporter.write_file.call_args
        assert "MyBrewfile" in str(call_args)


# ---------------------------------------------------------------------------
# sync
# ---------------------------------------------------------------------------


class TestSync:
    """Tests for `brewstanza sync`."""

    def _patch_all(
        self,
        mock_brew: MagicMock,
        mock_app: MagicMock,
        mock_scan: MagicMock,
        mock_exporter: MagicMock,
    ) -> None:
        brew_inst = mock_brew.return_value
        brew_inst.get_all_installed_info.return_value = {"formulae": [], "casks": []}
        brew_inst._run_brew_command.return_value = "/opt/homebrew/Cellar"
        mock_app.return_value.collect_app_paths.return_value = []
        mock_scan.return_value = _empty_summary()
        mock_exporter.to_json.return_value = "{}"
        mock_exporter.to_brewfile.return_value = ""

    @patch("brewstanza.cli.needs_wizard", return_value=False)
    @patch("brewstanza.cli.GitHubSync")
    @patch("brewstanza.cli.ExportManager")
    @patch("brewstanza.cli.scan_paths")
    @patch("brewstanza.cli.AppScanner")
    @patch("brewstanza.cli.HomebrewScanner")
    def test_sync_dry_run(
        self,
        mock_brew: MagicMock,
        mock_app: MagicMock,
        mock_scan: MagicMock,
        mock_exporter: MagicMock,
        mock_gh_sync: MagicMock,
        mock_needs_wizard: MagicMock,
    ) -> None:
        """sync --dry-run calls GitHubSync.sync with dry_run=True."""
        self._patch_all(mock_brew, mock_app, mock_scan, mock_exporter)
        mock_gh_sync.return_value.sync.return_value = "[DRY RUN] Would push..."

        result = CliRunner().invoke(main, ["sync", "--dry-run"])
        assert result.exit_code == 0
        sync_call = mock_gh_sync.return_value.sync.call_args
        assert sync_call.kwargs.get("dry_run") is True or sync_call.args[1] is True

    @patch("brewstanza.cli.needs_wizard", return_value=False)
    @patch("brewstanza.cli.GitHubSync")
    @patch("brewstanza.cli.ExportManager")
    @patch("brewstanza.cli.scan_paths")
    @patch("brewstanza.cli.AppScanner")
    @patch("brewstanza.cli.HomebrewScanner")
    def test_sync_surfaces_github_sync_error(
        self,
        mock_brew: MagicMock,
        mock_app: MagicMock,
        mock_scan: MagicMock,
        mock_exporter: MagicMock,
        mock_gh_sync: MagicMock,
        mock_needs_wizard: MagicMock,
    ) -> None:
        """sync shows error message when GitHubSyncError is raised."""
        from brewstanza.exporter.github_sync import GitHubSyncError

        self._patch_all(mock_brew, mock_app, mock_scan, mock_exporter)
        mock_gh_sync.return_value.sync.side_effect = GitHubSyncError("Token expired")

        result = CliRunner().invoke(main, ["sync"])
        assert result.exit_code == 0
        assert "Token expired" in result.output

    @patch("brewstanza.cli.run_wizard", return_value=False)
    @patch("brewstanza.cli.needs_wizard", return_value=True)
    def test_sync_triggers_wizard_when_config_missing(
        self, mock_needs_wizard: MagicMock, mock_run_wizard: MagicMock
    ) -> None:
        """sync invokes the wizard when config has no GitHub token."""
        result = CliRunner().invoke(main, ["sync"])
        assert result.exit_code == 0
        mock_run_wizard.assert_called_once()

    @patch("brewstanza.cli.needs_wizard", return_value=False)
    @patch("brewstanza.cli.GitHubSync")
    @patch("brewstanza.cli.ExportManager")
    @patch("brewstanza.cli.scan_paths")
    @patch("brewstanza.cli.AppScanner")
    @patch("brewstanza.cli.HomebrewScanner")
    def test_sync_commits_both_files(
        self,
        mock_brew: MagicMock,
        mock_app: MagicMock,
        mock_scan: MagicMock,
        mock_exporter: MagicMock,
        mock_gh_sync: MagicMock,
        mock_needs_wizard: MagicMock,
    ) -> None:
        """sync passes both Brewfile and JSON snapshot to GitHubSync.sync()."""
        self._patch_all(mock_brew, mock_app, mock_scan, mock_exporter)
        mock_gh_sync.return_value.sync.return_value = "✓ Synced"

        CliRunner().invoke(main, ["sync"])

        files_arg = mock_gh_sync.return_value.sync.call_args[0][0]
        assert "Brewfile" in files_arg
        assert "brewstanza-snapshot.json" in files_arg


# ---------------------------------------------------------------------------
# Global flags
# ---------------------------------------------------------------------------


class TestGlobalFlags:
    """Tests for root-level flags."""

    def test_no_color_flag_accepted(self) -> None:
        """--no-color is a valid flag that doesn't crash the CLI."""
        result = CliRunner().invoke(main, ["--no-color", "--help"])
        assert result.exit_code == 0
