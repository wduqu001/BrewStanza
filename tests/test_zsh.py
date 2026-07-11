import pytest
from pathlib import Path
from brewstanza.backups.zsh import backup

def test_backup_success(mocker, tmp_path):
    mock_exists = mocker.patch("brewstanza.backups.zsh.Path.exists")
    mock_exists.return_value = True
    
    mock_copytree = mocker.patch("brewstanza.backups.zsh.shutil.copytree")
    mock_copy2 = mocker.patch("brewstanza.backups.zsh.shutil.copy2")
    mock_rmtree = mocker.patch("brewstanza.backups.zsh.shutil.rmtree")
    
    result = backup(tmp_path)
    
    assert result is True
    mock_copytree.assert_called_once()
    mock_copy2.assert_called_once()
    mock_rmtree.assert_called_once()

def test_backup_error(mocker, tmp_path):
    mock_exists = mocker.patch("brewstanza.backups.zsh.Path.exists")
    mock_exists.return_value = True
    
    mock_copytree = mocker.patch("brewstanza.backups.zsh.shutil.copytree")
    mock_copytree.side_effect = PermissionError("Access denied")
    
    mock_rmtree = mocker.patch("brewstanza.backups.zsh.shutil.rmtree")
    
    # We still want to see it copy zshrc if zsh fails
    mock_copy2 = mocker.patch("brewstanza.backups.zsh.shutil.copy2")
    
    result = backup(tmp_path)
    
    assert result is True # Returns true because zshrc succeeded
    mock_copytree.assert_called_once()
    mock_copy2.assert_called_once()
