"""
Tests for BrewStanza app scanner.
"""

from pathlib import Path

from brewstanza.scanner.apps import AppScanner


def test_scan_directory_returns_list():
    scanner = AppScanner()

    result = scanner.scan_directory(Path("/Applications"))
    assert isinstance(result, list)
    assert result == []


def test_scan_all_applications_returns_list():
    scanner = AppScanner()

    result = scanner.scan_all_applications()
    assert isinstance(result, list)
    assert result == []


def test_parse_info_plist_returns_dict():
    scanner = AppScanner()

    result = scanner.parse_info_plist(Path("/Applications/Fake.app"))
    assert isinstance(result, dict)
    assert result == {}


def test_get_app_info_returns_dict():
    scanner = AppScanner()

    result = scanner.get_app_info(Path("/Applications/Fake.app"))
    assert isinstance(result, dict)
    assert result == {}


def test_calculate_app_size_returns_zero():
    scanner = AppScanner()

    result = scanner.calculate_app_size(Path("/Applications/Fake.app"))
    assert result == 0


def test_is_homebrew_cask_returns_false():
    scanner = AppScanner()

    result = scanner.is_homebrew_cask(Path("/Applications/Fake.app"))
    assert result is False


def test_deduplicate_apps_returns_input_when_ok():
    scanner = AppScanner()
    apps = [
        {"name": "AppA", "path": "/Applications/AppA.app"},
        {"name": "AppB", "path": "/Applications/AppB.app"},
    ]

    result = scanner.deduplicate_apps(apps)
    assert result == apps
