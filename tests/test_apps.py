from brewstanza.backups.apps import backup


def test_backup_success(mocker, tmp_path):
    mocker.patch("brewstanza.backups.apps.sys.platform", "darwin")
    mocker.patch("brewstanza.backups.apps.Path.exists", return_value=True)
    
    mock_path_obj = mocker.Mock()
    mock_path_obj.name = "TestApp.app"
    mocker.patch("brewstanza.backups.apps.Path.glob", return_value=[mock_path_obj])
    
    result = backup(tmp_path)
    
    assert result.succeeded
    assert (tmp_path / "apps_list.txt").exists()
    with open(tmp_path / "apps_list.txt", "r") as f:
        assert "TestApp.app" in f.read()

def test_backup_skipped_on_linux(mocker, tmp_path):
    mocker.patch("brewstanza.backups.apps.sys.platform", "linux")
    
    result = backup(tmp_path)
    
    assert result.status == "skipped"
    assert not (tmp_path / "apps_list.txt").exists()

def test_backup_refuses_application_source_destination(mocker, tmp_path):
    mocker.patch("brewstanza.backups.apps.sys.platform", "darwin")
    mocker.patch("brewstanza.backups.apps.Path.home", return_value=tmp_path)

    source_dir = tmp_path / "Applications"
    source_dir.mkdir()
    destination = source_dir / "backup"

    result = backup(destination)

    assert result.status == "failed"
    assert not (source_dir / "apps_list.txt").exists()

def test_backup_preserves_existing_app_list_on_write_failure(mocker, tmp_path):
    mocker.patch("brewstanza.backups.apps.sys.platform", "darwin")
    mocker.patch("brewstanza.backups.apps.Path.exists", return_value=True)
    app = mocker.Mock()
    app.name = "TestApp.app"
    mocker.patch("brewstanza.backups.apps.Path.glob", return_value=[app])
    existing = tmp_path / "apps_list.txt"
    existing.write_text("old\n")
    mocker.patch(
        "brewstanza.backups.apps.replace_text",
        side_effect=PermissionError("Access denied"),
    )

    result = backup(tmp_path)

    assert result.status == "failed"
    assert existing.read_text() == "old\n"

def test_backup_reports_application_scan_error(mocker, tmp_path):
    mocker.patch("brewstanza.backups.apps.sys.platform", "darwin")
    mocker.patch("brewstanza.backups.apps.Path.home", return_value=tmp_path)
    mocker.patch(
        "brewstanza.backups.apps.Path.exists",
        side_effect=PermissionError("Access denied"),
    )

    result = backup(tmp_path / "backup")

    assert result.status == "failed"
