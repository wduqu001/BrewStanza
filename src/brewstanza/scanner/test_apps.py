"""
Tests for BrewStanza app scanner.
"""

from pathlib import Path

from brewstanza.scanner.apps import AppScanner


def test_collect_app_paths_both_exist(tmp_path: Path) -> None:
    system_apps = tmp_path / "Applications"
    user_apps = tmp_path / "home" / "Applications"

    system_apps.mkdir(parents=True)
    user_apps.mkdir(parents=True)

    (system_apps / "Safari.app").mkdir()
    (system_apps / "Mail.app").mkdir()
    (system_apps / "NotAnApp.txt").touch()

    (user_apps / "Spotify.app").mkdir()

    scanner = AppScanner()
    scanner.system_apps = system_apps
    scanner.user_apps = user_apps

    apps = scanner.collect_app_paths()

    # Order depends on iteration, but let's check set equality
    expected = {
        system_apps / "Safari.app",
        system_apps / "Mail.app",
        user_apps / "Spotify.app",
    }
    assert set(apps) == expected


def test_collect_app_paths_missing_user_dir(tmp_path: Path) -> None:
    system_apps = tmp_path / "Applications"
    user_apps = tmp_path / "home" / "Applications"  # Does not exist

    system_apps.mkdir(parents=True)
    (system_apps / "Safari.app").mkdir()

    scanner = AppScanner()
    scanner.system_apps = system_apps
    scanner.user_apps = user_apps

    apps = scanner.collect_app_paths()
    assert apps == [system_apps / "Safari.app"]


def test_collect_app_paths_missing_both(tmp_path: Path) -> None:
    system_apps = tmp_path / "Applications"
    user_apps = tmp_path / "home" / "Applications"

    scanner = AppScanner()
    scanner.system_apps = system_apps
    scanner.user_apps = user_apps

    apps = scanner.collect_app_paths()
    assert apps == []


def test_collect_app_paths_is_file_not_dir(tmp_path: Path) -> None:
    system_apps = tmp_path / "Applications"
    user_apps = tmp_path / "home" / "Applications"

    # Create Applications as a file instead of dir
    system_apps.touch()

    scanner = AppScanner()
    scanner.system_apps = system_apps
    scanner.user_apps = user_apps

    apps = scanner.collect_app_paths()
    assert apps == []
