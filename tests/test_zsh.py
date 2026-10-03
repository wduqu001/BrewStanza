from brewstanza.backups.zsh import backup


def test_backup_success(mocker, tmp_path):
    mock_exists = mocker.patch("brewstanza.backups.zsh.Path.exists")
    mock_exists.return_value = True
    
    mock_copytree = mocker.patch("brewstanza.backups.zsh.replace_directory")
    mock_copy2 = mocker.patch("brewstanza.backups.zsh.replace_file")
    
    result = backup(tmp_path)
    
    assert result.succeeded
    mock_copytree.assert_called_once()
    mock_copy2.assert_called_once()

def test_backup_error(mocker, tmp_path):
    mock_exists = mocker.patch("brewstanza.backups.zsh.Path.exists")
    mock_exists.return_value = True
    
    mock_copytree = mocker.patch("brewstanza.backups.zsh.replace_directory")
    mock_copytree.side_effect = PermissionError("Access denied")
    
    
    # We still want to see it copy zshrc if zsh fails
    mock_copy2 = mocker.patch("brewstanza.backups.zsh.replace_file")
    
    result = backup(tmp_path)
    
    assert result.status == "failed"
    assert result.artifacts_copied == 1
    mock_copytree.assert_called_once()
    mock_copy2.assert_called_once()

def test_backup_refuses_home_destination(mocker, tmp_path):
    mocker.patch("brewstanza.backups.zsh.Path.home", return_value=tmp_path)
    (tmp_path / ".zsh").mkdir()
    (tmp_path / ".zshrc").touch()
    mock_copy2 = mocker.patch("brewstanza.backups.zsh.replace_file")

    result = backup(tmp_path)

    assert result.status == "failed"
    mock_copy2.assert_not_called()
