import pytest
from pathlib import Path
from brewstanza.backups.apps import backup

def test_backup_success(mocker, tmp_path):
    mocker.patch("brewstanza.backups.apps.sys.platform", "darwin")
    mock_exists = mocker.patch("brewstanza.backups.apps.Path.exists", return_value=True)
    
    mock_path_obj = mocker.Mock()
    mock_path_obj.name = "TestApp.app"
    mock_glob = mocker.patch("brewstanza.backups.apps.Path.glob", return_value=[mock_path_obj])
    
    result = backup(tmp_path)
    
    assert result is True
    assert (tmp_path / "apps_list.txt").exists()
    with open(tmp_path / "apps_list.txt", "r") as f:
        assert "TestApp.app" in f.read()

def test_backup_skipped_on_linux(mocker, tmp_path):
    mocker.patch("brewstanza.backups.apps.sys.platform", "linux")
    
    result = backup(tmp_path)
    
    assert result is False
    assert not (tmp_path / "apps_list.txt").exists()
