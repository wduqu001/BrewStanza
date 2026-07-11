import pytest
from pathlib import Path
from brewstanza.backups.homebrew import backup

def test_backup_success(mocker, tmp_path):
    mocker.patch("brewstanza.backups.homebrew.shutil.which", return_value="/usr/local/bin/brew")
    mock_run = mocker.patch("brewstanza.backups.homebrew.subprocess.run")
    mock_run.return_value.returncode = 0
    
    result = backup(tmp_path)
    
    assert result is True
    mock_run.assert_called_once()

def test_backup_no_brew(mocker, tmp_path):
    mocker.patch("brewstanza.backups.homebrew.shutil.which", return_value=None)
    mock_run = mocker.patch("brewstanza.backups.homebrew.subprocess.run")
    
    result = backup(tmp_path)
    
    assert result is False
    mock_run.assert_not_called()

def test_backup_error(mocker, tmp_path):
    mocker.patch("brewstanza.backups.homebrew.shutil.which", return_value="/usr/local/bin/brew")
    mock_run = mocker.patch("brewstanza.backups.homebrew.subprocess.run")
    mock_run.return_value.returncode = 1
    mock_run.return_value.stderr = "Command failed"
    
    result = backup(tmp_path)
    
    assert result is False
