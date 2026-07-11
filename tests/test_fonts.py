from brewstanza.backups.fonts import backup


def test_backup_success(mocker, tmp_path):
    mocker.patch("brewstanza.backups.fonts.sys.platform", "darwin")
    mock_exists = mocker.patch("brewstanza.backups.fonts.Path.exists", return_value=True)
    mock_copytree = mocker.patch("brewstanza.backups.fonts.shutil.copytree")
    mock_rmtree = mocker.patch("brewstanza.backups.fonts.shutil.rmtree")
    
    result = backup(tmp_path)
    
    assert result is True
    mock_copytree.assert_called_once()

def test_backup_skipped_on_linux(mocker, tmp_path):
    mocker.patch("brewstanza.backups.fonts.sys.platform", "linux")
    mock_copytree = mocker.patch("brewstanza.backups.fonts.shutil.copytree")
    
    result = backup(tmp_path)
    
    assert result is False
    mock_copytree.assert_not_called()
