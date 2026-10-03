from brewstanza.backups.claude import backup


def test_backup_success(mocker, tmp_path):
    source_dir = tmp_path / ".claude"
    source_dir.mkdir()
    source_file = source_dir / "settings.json"
    source_file.write_text('{"theme": "dark"}')
    mocker.patch("brewstanza.backups.claude.Path.home", return_value=tmp_path)
    
    result = backup(tmp_path / "backup")

    assert result.succeeded
    assert (tmp_path / "backup" / ".claude" / "settings.json").read_text() == (
        '{"theme": "dark"}'
    )

def test_backup_skipped_when_missing(mocker, tmp_path):
    mocker.patch("brewstanza.backups.claude.Path.home", return_value=tmp_path)

    result = backup(tmp_path / "backup")

    assert result.status == "skipped"

def test_backup_error(mocker, tmp_path):
    source_dir = tmp_path / ".claude"
    source_dir.mkdir()
    (source_dir / "settings.json").write_text("{}")
    mocker.patch("brewstanza.backups.claude.Path.home", return_value=tmp_path)
    mocker.patch(
        "brewstanza.backups.claude.os.replace",
        side_effect=PermissionError("Access denied"),
    )
    
    result = backup(tmp_path / "backup")

    assert result.status == "failed"

def test_backup_refuses_home_destination(mocker, tmp_path):
    mocker.patch("brewstanza.backups.claude.Path.home", return_value=tmp_path)
    source_dir = tmp_path / ".claude"
    source_dir.mkdir()
    (source_dir / "settings.json").write_text("{}")

    result = backup(tmp_path)

    assert result.status == "failed"

def test_backup_excludes_sensitive_and_unknown_files(tmp_path, mocker):
    source_dir = tmp_path / ".claude"
    source_dir.mkdir()
    (source_dir / "settings.json").write_text("{}")
    (source_dir / "credentials.json").write_text("token")
    (source_dir / "history.jsonl").write_text("prompt")
    (source_dir / "cache.db").write_text("cache")
    mocker.patch("brewstanza.backups.claude.Path.home", return_value=tmp_path)

    result = backup(tmp_path / "backup")

    assert result.succeeded
    assert (tmp_path / "backup" / ".claude" / "settings.json").exists()
    assert not (tmp_path / "backup" / ".claude" / "credentials.json").exists()
    assert not (tmp_path / "backup" / ".claude" / "history.jsonl").exists()
    assert not (tmp_path / "backup" / ".claude" / "cache.db").exists()

def test_backup_skips_symlinked_source_file(tmp_path, mocker):
    source_dir = tmp_path / ".claude"
    source_dir.mkdir()
    sensitive_file = tmp_path / "credentials.json"
    sensitive_file.write_text("token")
    (source_dir / "settings.json").symlink_to(sensitive_file)
    mocker.patch("brewstanza.backups.claude.Path.home", return_value=tmp_path)

    result = backup(tmp_path / "backup")

    assert result.status == "failed"
    assert not (tmp_path / "backup").exists()

def test_backup_rejects_symlinked_destination(tmp_path, mocker):
    source_dir = tmp_path / ".claude"
    source_dir.mkdir()
    (source_dir / "settings.json").write_text("{}")
    outside = tmp_path / "outside"
    outside.mkdir()
    (tmp_path / "backup").mkdir()
    (tmp_path / "backup" / ".claude").symlink_to(outside, target_is_directory=True)
    mocker.patch("brewstanza.backups.claude.Path.home", return_value=tmp_path)

    result = backup(tmp_path / "backup")

    assert result.status == "failed"
    assert not (outside / "settings.json").exists()

def test_backup_rejects_symlinked_destination_ancestor(tmp_path, mocker):
    source_dir = tmp_path / ".claude"
    source_dir.mkdir()
    (source_dir / "settings.json").write_text("{}")
    outside = tmp_path / "outside"
    outside.mkdir()
    link = tmp_path / "link"
    link.symlink_to(outside, target_is_directory=True)
    mocker.patch("brewstanza.backups.claude.Path.home", return_value=tmp_path)

    result = backup(link / "backup")

    assert result.status == "failed"
    assert not (outside / "backup" / ".claude" / "settings.json").exists()

def test_backup_preserves_existing_file_when_replace_fails(tmp_path, mocker):
    source_dir = tmp_path / ".claude"
    source_dir.mkdir()
    (source_dir / "settings.json").write_text("new")
    destination = tmp_path / "backup" / ".claude"
    destination.mkdir(parents=True)
    existing = destination / "settings.json"
    existing.write_text("old")
    mocker.patch("brewstanza.backups.claude.Path.home", return_value=tmp_path)
    mocker.patch("brewstanza.backups.claude.os.replace", side_effect=OSError("replace failed"))

    result = backup(tmp_path / "backup")

    assert result.status == "failed"
    assert existing.read_text() == "old"
