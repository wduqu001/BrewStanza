
import json

import pytest
from click.testing import CliRunner

from brewstanza.backups.results import BackupResult
from brewstanza.cli import MODULES, main


@pytest.fixture
def runner():
    return CliRunner()

def test_backup_all(runner, mocker, tmp_path):
    mocker.patch("brewstanza.backups.package._git_executable", return_value=None)
    mock_modules = {
        name: mocker.Mock(return_value=BackupResult.success(name, "ok"))
        for name in MODULES.keys()
    }
    mocker.patch("brewstanza.cli.MODULES", mock_modules)
    
    result = runner.invoke(main, ["backup", "--all", "--dest", str(tmp_path / "backup")])
    
    assert result.exit_code == 0
    assert "Starting backups for: Claude, Zsh, Homebrew, Fonts, Git, SSH, Apps" in result.output
    
    for mock_func in mock_modules.values():
        mock_func.assert_called_once()


def test_backup_dry_run_does_not_create_destination(runner, mocker, tmp_path):
    destination = tmp_path / "planned-backup"
    mock_modules = {
        name: mocker.Mock(return_value=BackupResult.success(name, "planned"))
        for name in MODULES.keys()
    }
    mocker.patch("brewstanza.cli.MODULES", mock_modules)

    result = runner.invoke(
        main, ["backup", "--all", "--dry-run", "--dest", str(destination)]
    )

    assert result.exit_code == 0
    assert "Dry run Orchestrator" in result.output
    assert not destination.exists()
    for mock_func in mock_modules.values():
        mock_func.assert_called_once_with(destination, dry_run=True)


def test_backup_prompt_selection(runner, mocker, tmp_path):
    mocker.patch("brewstanza.backups.package._git_executable", return_value=None)
    mock_modules = {
        name: mocker.Mock(return_value=BackupResult.success(name, "ok"))
        for name in MODULES.keys()
    }
    mocker.patch("brewstanza.cli.MODULES", mock_modules)
    
    # Simulate user typing "1, 2" for Claude and Zsh
    result = runner.invoke(
        main, ["backup", "--dest", str(tmp_path / "backup")], input="1, 2\n"
    )
    
    assert result.exit_code == 0
    assert "Starting backups for: Claude, Zsh" in result.output
    
    mock_modules["Claude"].assert_called_once()
    mock_modules["Zsh"].assert_called_once()
    mock_modules["Homebrew"].assert_not_called()

def test_backup_invalid_selection(runner, mocker, tmp_path):
    mock_modules = {
        name: mocker.Mock(return_value=BackupResult.success(name, "ok"))
        for name in MODULES.keys()
    }
    mocker.patch("brewstanza.cli.MODULES", mock_modules)
    
    result = runner.invoke(
        main, ["backup", "--dest", str(tmp_path / "backup")], input="999\n"
    )
    
    assert result.exit_code == 0
    assert "Invalid selection. Exiting." in result.output

def test_backup_returns_failure_for_failed_module(runner, mocker, tmp_path):
    mocker.patch("brewstanza.backups.package._git_executable", return_value=None)
    mock_modules = {
        name: mocker.Mock(return_value=BackupResult.failed(name, "failed"))
        for name in MODULES.keys()
    }
    mocker.patch("brewstanza.cli.MODULES", mock_modules)

    result = runner.invoke(
        main, ["backup", "--all", "--dest", str(tmp_path / "backup")]
    )

    assert result.exit_code == 1
    assert "0 succeeded, 0 skipped, 7 failed" in result.output
    assert "One or more backup components failed." in result.output
    snapshots = [path for path in (tmp_path / "backup").iterdir() if path.is_dir()]
    assert len(snapshots) == 1
    manifest = json.loads((snapshots[0] / "manifest.json").read_text())
    assert manifest["status"] == "partial"

def test_backup_reports_destination_creation_error(runner, mocker, tmp_path):
    destination = tmp_path / "backup"
    mocker.patch("brewstanza.cli.Path.mkdir", side_effect=PermissionError("Access denied"))

    result = runner.invoke(main, ["backup", "--dest", str(destination), "--all"])

    assert result.exit_code == 1
    assert "Invalid backup destination" in result.output

def test_backup_validates_sources_before_creating_destination(runner, mocker, tmp_path):
    destination = tmp_path / "backup"
    mocker.patch(
        "brewstanza.cli._validate_dest_for_choices",
        side_effect=ValueError("overlaps source"),
    )
    mkdir = mocker.patch("brewstanza.cli.Path.mkdir")

    result = runner.invoke(main, ["backup", "--dest", str(destination), "--all"])

    assert result.exit_code == 1
    assert "Invalid backup destination" in result.output
    mkdir.assert_not_called()

def test_backup_skips_macos_preflight_on_non_macos(runner, mocker, tmp_path):
    mocker.patch("brewstanza.backups.package._git_executable", return_value=None)
    mocker.patch("brewstanza.cli.sys.platform", "linux")
    mocker.patch("brewstanza.cli.Path.home", return_value=tmp_path)
    mocker.patch("brewstanza.cli.ensure_safe", side_effect=ValueError("overlaps source"))
    mock_modules = {"Apps": mocker.Mock(return_value=BackupResult.skipped("Apps", "unsupported"))}
    mocker.patch("brewstanza.cli.MODULES", mock_modules)

    result = runner.invoke(
        main, ["backup", "--dest", str(tmp_path / "Applications" / "backup"), "--all"]
    )

    assert result.exit_code == 0
    assert "1 skipped" in result.output
    mock_modules["Apps"].assert_called_once()

def test_version_option(runner):
    result = runner.invoke(main, ["--version"])

    assert result.exit_code == 0
    assert "1.1.0" in result.output

def test_backup_refuses_home_dest(runner, mocker, tmp_path):
    mocker.patch("brewstanza.backups.safety.Path.home", return_value=tmp_path)
    mock_modules = {
        name: mocker.Mock(return_value=BackupResult.success(name, "ok"))
        for name in MODULES.keys()
    }
    mocker.patch("brewstanza.cli.MODULES", mock_modules)

    result = runner.invoke(main, ["backup", "--dest", str(tmp_path), "--all"])

    assert result.exit_code == 1
    assert "Backup destination cannot be the home directory" in result.output
    for mock_func in mock_modules.values():
        mock_func.assert_not_called()


def test_init_creates_package_root(runner, mocker, tmp_path):
    destination = tmp_path / "backup"
    mocker.patch("brewstanza.backups.package._git_executable", return_value=None)

    result = runner.invoke(main, ["init", "--dest", str(destination)])

    assert result.exit_code == 0
    assert "Package initialized" in result.output
    assert (destination / ".brewstanza.json").is_file()


def test_backup_refuses_unrecognized_nonempty_destination(runner, mocker, tmp_path):
    destination = tmp_path / "backup"
    destination.mkdir()
    (destination / "keep.txt").write_text("untouched")
    modules = {"Claude": mocker.Mock(return_value=BackupResult.success("Claude", "ok"))}
    mocker.patch("brewstanza.cli.MODULES", modules)

    result = runner.invoke(main, ["backup", "--all", "--dest", str(destination)])

    assert result.exit_code == 1
    assert "not empty" in result.output
    modules["Claude"].assert_not_called()
    assert (destination / "keep.txt").read_text() == "untouched"
