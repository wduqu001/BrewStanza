import subprocess
from pathlib import Path

from brewstanza.backups.homebrew import backup


def test_backup_success(mocker, tmp_path):
    mocker.patch("brewstanza.backups.homebrew.shutil.which", return_value="/usr/local/bin/brew")
    mock_run = mocker.patch("brewstanza.backups.homebrew.subprocess.run")
    def create_brewfile(args, **kwargs):
        file_arg = next(arg for arg in args if arg.startswith("--file="))
        Path(file_arg.split("=", 1)[1]).write_text("brew 'python'\n")
        return mocker.Mock(returncode=0, stderr="", stdout="")
    mock_run.side_effect = create_brewfile
    
    result = backup(tmp_path)
    
    assert result.succeeded
    mock_run.assert_called_once()

def test_backup_no_brew(mocker, tmp_path):
    mocker.patch("brewstanza.backups.homebrew.shutil.which", return_value=None)
    mock_run = mocker.patch("brewstanza.backups.homebrew.subprocess.run")
    
    result = backup(tmp_path)
    
    assert result.status == "skipped"
    mock_run.assert_not_called()

def test_backup_error(mocker, tmp_path):
    mocker.patch("brewstanza.backups.homebrew.shutil.which", return_value="/usr/local/bin/brew")
    mock_run = mocker.patch("brewstanza.backups.homebrew.subprocess.run")
    mock_run.return_value.returncode = 1
    mock_run.return_value.stderr = "Command failed"
    
    result = backup(tmp_path)
    
    assert result.status == "failed"
    assert "exit code 1" in result.message

def test_backup_timeout(mocker, tmp_path):
    mocker.patch("brewstanza.backups.homebrew.shutil.which", return_value="/usr/local/bin/brew")
    mocker.patch(
        "brewstanza.backups.homebrew.subprocess.run",
        side_effect=subprocess.TimeoutExpired("brew", 30),
    )

    result = backup(tmp_path)

    assert result.status == "failed"
    assert "timed out" in result.message

def test_backup_timeout_preserves_partial_output(mocker, tmp_path):
    mocker.patch("brewstanza.backups.homebrew.shutil.which", return_value="/usr/local/bin/brew")
    mocker.patch(
        "brewstanza.backups.homebrew.subprocess.run",
        side_effect=subprocess.TimeoutExpired("brew", 30, stderr=b"package stalled"),
    )

    result = backup(tmp_path)

    assert "package stalled" in result.message

def test_backup_preserves_existing_brewfile_on_failure(mocker, tmp_path):
    mocker.patch("brewstanza.backups.homebrew.shutil.which", return_value="/usr/local/bin/brew")
    existing = tmp_path / "Brewfile"
    existing.write_text("old\n")
    process = mocker.patch("brewstanza.backups.homebrew.subprocess.run")
    process.return_value.returncode = 1
    process.return_value.stderr = "failed"

    result = backup(tmp_path)

    assert result.status == "failed"
    assert existing.read_text() == "old\n"

def test_backup_reports_temp_file_creation_error(mocker, tmp_path):
    mocker.patch("brewstanza.backups.homebrew.shutil.which", return_value="/usr/local/bin/brew")
    mocker.patch(
        "brewstanza.backups.homebrew.tempfile.mkstemp",
        side_effect=PermissionError("Access denied"),
    )

    result = backup(tmp_path)

    assert result.status == "failed"

def test_backup_uses_stdout_when_stderr_is_whitespace(mocker, tmp_path):
    mocker.patch("brewstanza.backups.homebrew.shutil.which", return_value="/usr/local/bin/brew")
    process = mocker.patch("brewstanza.backups.homebrew.subprocess.run")
    process.return_value.returncode = 1
    process.return_value.stderr = " \n"
    process.return_value.stdout = "useful diagnostic"

    result = backup(tmp_path)

    assert "useful diagnostic" in result.message
