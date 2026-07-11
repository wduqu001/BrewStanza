import pytest
from pathlib import Path
from brewstanza.backups.claude import backup

def test_backup_success(mocker, tmp_path):
    mock_exists = mocker.patch("brewstanza.backups.claude.Path.exists")
    mock_exists.return_value = True
    
    mock_copytree = mocker.patch("brewstanza.backups.claude.shutil.copytree")
    mock_rmtree = mocker.patch("brewstanza.backups.claude.shutil.rmtree")
    
    result = backup(tmp_path)
    
    assert result is True
    mock_rmtree.assert_called_once()
    mock_copytree.assert_called_once()

def test_backup_skipped_when_missing(mocker, tmp_path):
    mock_exists = mocker.patch("brewstanza.backups.claude.Path.exists")
    mock_exists.return_value = False
    
    mock_copytree = mocker.patch("brewstanza.backups.claude.shutil.copytree")
    
    result = backup(tmp_path)
    
    assert result is False
    mock_copytree.assert_not_called()

def test_backup_error(mocker, tmp_path):
    mock_exists = mocker.patch("brewstanza.backups.claude.Path.exists")
    mock_exists.return_value = True
    
    mock_copytree = mocker.patch("brewstanza.backups.claude.shutil.copytree")
    mock_copytree.side_effect = PermissionError("Access denied")
    
    result = backup(tmp_path)
    
    assert result is False
