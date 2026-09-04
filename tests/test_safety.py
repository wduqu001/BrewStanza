import pytest

from brewstanza.backups.safety import ensure_dest_not_home, ensure_safe


def test_refuses_home_destination(mocker, tmp_path):
    mocker.patch("brewstanza.backups.safety.Path.home", return_value=tmp_path)

    with pytest.raises(ValueError):
        ensure_dest_not_home(tmp_path)


def test_accepts_normal_destination(tmp_path):
    dest = tmp_path / "backup"
    source = tmp_path / ".claude"

    ensure_safe(dest, source)


def test_refuses_dest_equal_to_source(tmp_path):
    with pytest.raises(ValueError):
        ensure_safe(tmp_path, tmp_path)


def test_refuses_source_inside_dest(tmp_path):
    with pytest.raises(ValueError):
        ensure_safe(tmp_path, tmp_path / ".claude")


def test_refuses_dest_inside_source(tmp_path):
    source = tmp_path / ".claude"

    with pytest.raises(ValueError):
        ensure_safe(source / "backups", source)
