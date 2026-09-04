from brewstanza.backups.git import backup


def test_backup_success(mocker, tmp_path):
    mocker.patch("brewstanza.backups.git.Path.exists", return_value=True)
    mock_copy2 = mocker.patch("brewstanza.backups.git.shutil.copy2")
    
    result = backup(tmp_path)
    
    assert result is True
    mock_copy2.assert_called_once()

def test_backup_missing(mocker, tmp_path):
    mocker.patch("brewstanza.backups.git.Path.exists", return_value=False)
    mock_copy2 = mocker.patch("brewstanza.backups.git.shutil.copy2")
    
    result = backup(tmp_path)
    
    assert result is False
    mock_copy2.assert_not_called()

def test_backup_refuses_home_destination(mocker, tmp_path):
    mocker.patch("brewstanza.backups.git.Path.home", return_value=tmp_path)
    (tmp_path / ".gitconfig").touch()
    mock_copy2 = mocker.patch("brewstanza.backups.git.shutil.copy2")

    result = backup(tmp_path)

    assert result is False
    mock_copy2.assert_not_called()
