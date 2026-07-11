import pytest
from pathlib import Path
from click.testing import CliRunner
from brewstanza.cli import main

@pytest.fixture
def fake_env(tmp_path, mocker):
    # Create fake home directory
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    
    # Create fake source files
    (fake_home / ".claude").mkdir()
    (fake_home / ".claude" / "settings.json").touch()
    
    (fake_home / ".zsh").mkdir()
    (fake_home / ".zsh" / "custom.zsh").touch()
    (fake_home / ".zshrc").touch()
    
    fake_fonts = fake_home / "Library" / "Fonts"
    fake_fonts.mkdir(parents=True)
    (fake_fonts / "Arial.ttf").touch()
    
    (fake_home / ".gitconfig").write_text("[user]\nname=Test")
    
    fake_ssh = fake_home / ".ssh"
    fake_ssh.mkdir()
    (fake_ssh / "config").write_text("Host *")
    (fake_ssh / "id_rsa").touch() # Should not be copied
    
    fake_home_apps = fake_home / "Applications"
    fake_home_apps.mkdir()
    (fake_home_apps / "UserApp.app").mkdir()
    
    fake_root_apps = tmp_path / "Applications"
    fake_root_apps.mkdir()
    (fake_root_apps / "RootApp.app").mkdir()

    # Mock Path.home() to return our fake home
    mocker.patch("brewstanza.backups.claude.Path.home", return_value=fake_home)
    mocker.patch("brewstanza.backups.zsh.Path.home", return_value=fake_home)
    mocker.patch("brewstanza.backups.fonts.Path.home", return_value=fake_home)
    mocker.patch("brewstanza.backups.git.Path.home", return_value=fake_home)
    mocker.patch("brewstanza.backups.ssh.Path.home", return_value=fake_home)
    
    # For apps, we need to mock both /Applications and ~/Applications
    mocker.patch("brewstanza.backups.apps.Path.home", return_value=fake_home)
    
    # We must patch the specific hardcoded Path("/Applications") inside apps.py
    # A clean way is to patch Path itself inside apps.py, but it's easier to mock the list directly.
    # Instead, we can just let it check the real /Applications (which doesn't hurt) or mock it.
    # To be perfectly safe, let's mock sys.platform to "darwin" and patch the app_dirs list
    mocker.patch("brewstanza.backups.apps.sys.platform", "darwin")
    mocker.patch("brewstanza.backups.fonts.sys.platform", "darwin")
    
    # Replace the app_dirs list inside apps.backup with our fake paths
    # We can do this by mocking Path inside apps.py just for the root path
    original_path = Path
    def fake_path(*args, **kwargs):
        if args and args[0] == "/Applications":
            return fake_root_apps
        return original_path(*args, **kwargs)
        
    mocker.patch("brewstanza.backups.apps.Path", side_effect=fake_path)
    mocker.patch("brewstanza.backups.apps.Path.home", return_value=fake_home)
    
    # Mock Homebrew subprocess to just write a fake Brewfile so we don't actually run brew
    mocker.patch("brewstanza.backups.homebrew.shutil.which", return_value="/usr/local/bin/brew")
    def fake_run(args, **kwargs):
        if "dump" in args:
            # extract the file path
            for arg in args:
                if arg.startswith("--file="):
                    path_str = arg.split("=")[1]
                    Path(path_str).write_text("brew 'python'\ncask 'google-chrome'")
        mock_result = mocker.Mock()
        mock_result.returncode = 0
        return mock_result
    mocker.patch("brewstanza.backups.homebrew.subprocess.run", side_effect=fake_run)
    
    return fake_home

def test_integration_full_backup(fake_env, tmp_path):
    runner = CliRunner()
    dest = tmp_path / "backup_dest"
    
    result = runner.invoke(main, ["backup", "--dest", str(dest), "--all"])
    
    assert result.exit_code == 0
    assert "Backup complete!" in result.output
    
    # Verify Claude
    assert (dest / ".claude" / "settings.json").exists()
    
    # Verify Zsh
    assert (dest / ".zsh" / "custom.zsh").exists()
    assert (dest / ".zshrc").exists()
    
    # Verify Fonts
    assert (dest / "Fonts" / "Arial.ttf").exists()
    
    # Verify Git
    assert (dest / ".gitconfig").read_text() == "[user]\nname=Test"
    
    # Verify SSH
    assert (dest / ".ssh" / "config").read_text() == "Host *"
    assert not (dest / ".ssh" / "id_rsa").exists() # Should ignore keys!
    
    # Verify Apps (Should contain both RootApp and UserApp)
    apps_list = (dest / "apps_list.txt").read_text()
    assert "RootApp.app" in apps_list
    assert "UserApp.app" in apps_list
    
    # Verify Homebrew
    assert (dest / "Brewfile").read_text() == "brew 'python'\ncask 'google-chrome'"
