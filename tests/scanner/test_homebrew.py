"""
Tests for BrewStanza Homebrew scanner.
"""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from brewstanza.scanner.homebrew import HomebrewScanner


@pytest.fixture
def scanner() -> HomebrewScanner:
    return HomebrewScanner()


@patch("subprocess.run")
def test_run_brew_command_success(mock_run: MagicMock, scanner: HomebrewScanner) -> None:
    mock_run.return_value = MagicMock(stdout="some output\n")
    result = scanner._run_brew_command(["list"])
    assert result == "some output"
    mock_run.assert_called_once_with(["brew", "list"], check=True, capture_output=True, text=True)


@patch("subprocess.run")
def test_run_brew_command_failure(mock_run: MagicMock, scanner: HomebrewScanner) -> None:
    mock_run.side_effect = subprocess.CalledProcessError(1, ["brew", "fail"], stderr="error output")
    with pytest.raises(RuntimeError, match="Homebrew command failed: brew fail"):
        scanner._run_brew_command(["fail"])


@patch("subprocess.run")
def test_list_formulae(mock_run: MagicMock, scanner: HomebrewScanner) -> None:
    mock_run.return_value = MagicMock(stdout="python\ngit\n")
    assert scanner.list_formulae() == ["python", "git"]
    mock_run.assert_called_once_with(
        ["brew", "list", "--formula"], check=True, capture_output=True, text=True
    )


@patch("subprocess.run")
def test_list_formulae_empty(mock_run: MagicMock, scanner: HomebrewScanner) -> None:
    mock_run.return_value = MagicMock(stdout="")
    assert scanner.list_formulae() == []


@patch("subprocess.run")
def test_list_casks(mock_run: MagicMock, scanner: HomebrewScanner) -> None:
    mock_run.return_value = MagicMock(stdout="iterm2\nspotify\n")
    assert scanner.list_casks() == ["iterm2", "spotify"]
    mock_run.assert_called_once_with(
        ["brew", "list", "--cask"], check=True, capture_output=True, text=True
    )


@patch("subprocess.run")
def test_list_casks_empty(mock_run: MagicMock, scanner: HomebrewScanner) -> None:
    mock_run.return_value = MagicMock(stdout="")
    assert scanner.list_casks() == []


@patch("subprocess.run")
def test_get_info(mock_run: MagicMock, scanner: HomebrewScanner) -> None:
    fake_info = {"formulae": [{"name": "python"}]}
    mock_run.return_value = MagicMock(stdout=json.dumps(fake_info))
    assert scanner.get_info("python") == fake_info
    mock_run.assert_called_once_with(
        ["brew", "info", "--json=v2", "python"], check=True, capture_output=True, text=True
    )


@patch("subprocess.run")
def test_get_outdated(mock_run: MagicMock, scanner: HomebrewScanner) -> None:
    mock_run.return_value = MagicMock(stdout="python\nnode\n")
    assert scanner.get_outdated() == ["python", "node"]
    mock_run.assert_called_once_with(
        ["brew", "outdated", "--quiet"], check=True, capture_output=True, text=True
    )


@patch("subprocess.run")
def test_get_outdated_empty(mock_run: MagicMock, scanner: HomebrewScanner) -> None:
    mock_run.return_value = MagicMock(stdout="")
    assert scanner.get_outdated() == []


@patch.object(HomebrewScanner, "get_info")
@patch.object(HomebrewScanner, "_run_brew_command")
def test_get_cellar_path_success(
    mock_run: MagicMock, mock_get_info: MagicMock, scanner: HomebrewScanner
) -> None:
    mock_get_info.return_value = {
        "formulae": [{"installed": [{"version": "3.11.4"}], "linked_keg": "3.11.4"}]
    }
    mock_run.return_value = "/opt/homebrew/Cellar"

    path = scanner.get_cellar_path("python")
    assert path == Path("/opt/homebrew/Cellar/python/3.11.4")
    mock_run.assert_called_once_with(["--cellar"])


@patch.object(HomebrewScanner, "get_info")
@patch.object(HomebrewScanner, "_run_brew_command")
def test_get_cellar_path_uses_cached_base(
    mock_run: MagicMock, mock_get_info: MagicMock, scanner: HomebrewScanner
) -> None:
    mock_get_info.return_value = {
        "formulae": [{"installed": [{"version": "3.11.4"}], "linked_keg": "3.11.4"}]
    }
    # Pre-seed the cache
    scanner._cellar_base = Path("/usr/local/Cellar")

    path = scanner.get_cellar_path("python")
    assert path == Path("/usr/local/Cellar/python/3.11.4")
    # Shouldn't be called since it was cached
    mock_run.assert_not_called()


@patch.object(HomebrewScanner, "get_info")
def test_get_cellar_path_not_found(mock_get_info: MagicMock, scanner: HomebrewScanner) -> None:
    mock_get_info.side_effect = RuntimeError("Not found")
    assert scanner.get_cellar_path("nonexistent") is None


@patch.object(HomebrewScanner, "get_info")
def test_get_cellar_path_no_formulae(mock_get_info: MagicMock, scanner: HomebrewScanner) -> None:
    mock_get_info.return_value = {"formulae": []}
    assert scanner.get_cellar_path("python") is None


@patch.object(HomebrewScanner, "get_info")
def test_get_cellar_path_not_installed(mock_get_info: MagicMock, scanner: HomebrewScanner) -> None:
    mock_get_info.return_value = {"formulae": [{"installed": [], "linked_keg": None}]}
    assert scanner.get_cellar_path("python") is None
