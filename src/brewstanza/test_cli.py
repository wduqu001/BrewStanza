"""
Tests for BrewStanza CLI.
"""

from unittest.mock import MagicMock, patch

from pathlib import Path

from click.testing import CliRunner

from brewstanza.cli import main


class TestCLI:
    """Test CLI commands."""

    def test_version(self) -> None:
        """Test --version flag."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_help(self) -> None:
        """Test --help flag."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "BrewStanza" in result.output
        assert "brew" in result.output
        assert "apps" in result.output

    def test_brew_help(self) -> None:
        """Test brew --help."""
        runner = CliRunner()
        result = runner.invoke(main, ["brew", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "info" in result.output

    def test_apps_help(self) -> None:
        """Test apps --help."""
        runner = CliRunner()
        result = runner.invoke(main, ["apps", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output

    @patch("brewstanza.cli.scan_paths")
    @patch("brewstanza.cli.HomebrewScanner")
    def test_brew_list_json(
        self, mock_scanner: MagicMock, mock_scan_paths: MagicMock
    ) -> None:
        """Test brew list --json."""
        instance = mock_scanner.return_value
        instance.get_all_installed_info.return_value = {
            "formulae": [{"name": "python", "installed": [{"version": "3.11"}]}],
            "casks": [],
        }
        instance.get_outdated.return_value = []
        instance._run_brew_command.return_value = "/opt/homebrew/Cellar"

        # Mock scan_paths to return an empty summary
        mock_scan_paths.return_value = MagicMock(results=[MagicMock(size_bytes=1024)])

        runner = CliRunner()
        result = runner.invoke(main, ["brew", "list", "--json"])
        assert result.exit_code == 0
        assert "python" in result.output
        assert "3.11" in result.output

    @patch("brewstanza.cli.scan_paths")
    @patch("brewstanza.cli.HomebrewScanner")
    def test_brew_info(
        self, mock_scanner: MagicMock, mock_scan_paths: MagicMock
    ) -> None:
        """Test brew info."""
        instance = mock_scanner.return_value
        instance.get_info.return_value = {
            "formulae": [
                {
                    "name": "wget",
                    "desc": "Internet file retriever",
                    "installed": [{"version": "1.21"}],
                }
            ],
            "casks": [],
        }
        instance._run_brew_command.return_value = "/opt/homebrew/Cellar"

        mock_scan_paths.return_value = MagicMock(total_bytes=2048)

        runner = CliRunner()
        result = runner.invoke(main, ["brew", "info", "wget"])
        assert result.exit_code == 0
        assert "wget" in result.output
        assert "Internet file retriever" in result.output

    @patch("brewstanza.cli.scan_paths")
    @patch("brewstanza.cli.AppScanner")
    def test_apps_list_json(
        self, mock_scanner: MagicMock, mock_scan_paths: MagicMock
    ) -> None:
        """Test apps list --json."""
        instance = mock_scanner.return_value
        instance.collect_app_paths.return_value = [Path("/Applications/TestApp.app")]

        mock_scan_paths.return_value = MagicMock(
            results=[MagicMock(path=Path("/Applications/TestApp.app"), size_bytes=4096)]
        )

        runner = CliRunner()
        result = runner.invoke(main, ["apps", "list", "--json"])
        assert result.exit_code == 0
        assert "TestApp" in result.output

    @patch("brewstanza.cli.AppScanner")
    def test_apps_info(self, mock_scanner: MagicMock) -> None:
        """Test apps info."""
        instance = mock_scanner.return_value
        instance.collect_app_paths.return_value = [Path("/Applications/TestApp.app")]

        runner = CliRunner()
        result = runner.invoke(main, ["apps", "info", "TestApp"])
        assert result.exit_code == 0
        assert "Uninstall Instructions" in result.output
        assert "TestApp.app" in result.output

    @patch("brewstanza.cli.scan_paths")
    @patch("brewstanza.cli.AppScanner")
    @patch("brewstanza.cli.HomebrewScanner")
    def test_storage_json(
        self,
        mock_brew_scanner: MagicMock,
        mock_app_scanner: MagicMock,
        mock_scan_paths: MagicMock,
    ) -> None:
        """Test storage --json."""
        brew_instance = mock_brew_scanner.return_value
        brew_instance.get_all_installed_info.return_value = {"formulae": [], "casks": []}
        brew_instance._run_brew_command.return_value = "/opt/homebrew/Cellar"

        app_instance = mock_app_scanner.return_value
        app_instance.collect_app_paths.return_value = []

        mock_scan_paths.return_value = MagicMock(results=[])

        runner = CliRunner()
        result = runner.invoke(main, ["storage", "--json"])
        assert result.exit_code == 0
        assert "homebrew_total" in result.output
        assert "apps_total" in result.output
