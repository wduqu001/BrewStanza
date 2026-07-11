from brewstanza.backups.ssh import backup


def test_backup_success(mocker, tmp_path):
    mock_exists = mocker.patch("brewstanza.backups.ssh.Path.exists", return_value=True)
    mock_copy2 = mocker.patch("brewstanza.backups.ssh.shutil.copy2")
    
    result = backup(tmp_path)
    
    assert result is True
    mock_copy2.assert_called_once()
