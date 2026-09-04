from brewstanza.backups.ssh import backup


def test_backup_success(mocker, tmp_path):
    mocker.patch("brewstanza.backups.ssh.Path.exists", return_value=True)
    mock_copy2 = mocker.patch("brewstanza.backups.ssh.shutil.copy2")
    
    result = backup(tmp_path)
    
    assert result is True
    mock_copy2.assert_called_once()

def test_backup_refuses_home_destination(mocker, tmp_path):
    mocker.patch("brewstanza.backups.ssh.Path.home", return_value=tmp_path)
    (tmp_path / ".ssh").mkdir()
    (tmp_path / ".ssh" / "config").touch()
    mock_copy2 = mocker.patch("brewstanza.backups.ssh.shutil.copy2")

    result = backup(tmp_path)

    assert result is False
    mock_copy2.assert_not_called()
