"""
Tests for BrewStanza Homebrew scanner.
"""

from pathlib import Path
import pytest

from brewstanza.scanner.homebrew import HomebrewScanner


def test_run_brew_command_not_implemented():
    scanner = HomebrewScanner()

    with pytest.raises(NotImplementedError, match="Homebrew scanner not yet implemented"):
        scanner.run_brew_command(["list"])


def test_list_formulae_returns_list():
    scanner = HomebrewScanner()

    assert isinstance(scanner.list_formulae(), list)
    assert scanner.list_formulae() == []


def test_list_casks_returns_list():
    scanner = HomebrewScanner()

    assert isinstance(scanner.list_casks(), list)
    assert scanner.list_casks() == []


def test_get_package_info_empty_dict():
    scanner = HomebrewScanner()

    assert isinstance(scanner.get_package_info("nonexistent"), dict)
    assert scanner.get_package_info("nonexistent") == {}


def test_get_outdated_packages_returns_list():
    scanner = HomebrewScanner()

    assert isinstance(scanner.get_outdated_packages(), list)
    assert scanner.get_outdated_packages() == []


def test_calculate_package_size_returns_zero_for_missing_path():
    scanner = HomebrewScanner()

    size = scanner.calculate_package_size(Path("/does/not/exist"))
    assert size == 0


def test_get_total_size_returns_zero():
    scanner = HomebrewScanner()

    assert scanner.get_total_size() == 0
