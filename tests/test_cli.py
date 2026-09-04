
import pytest
from click.testing import CliRunner

from brewstanza.cli import MODULES, main


@pytest.fixture
def runner():
    return CliRunner()

def test_backup_all(runner, mocker):
    mock_modules = {name: mocker.Mock(return_value=True) for name in MODULES.keys()}
    mocker.patch("brewstanza.cli.MODULES", mock_modules)
    
    result = runner.invoke(main, ["backup", "--all"])
    
    assert result.exit_code == 0
    assert "Starting backups for: Claude, Zsh, Homebrew, Fonts, Git, SSH, Apps" in result.output
    
    for mock_func in mock_modules.values():
        mock_func.assert_called_once()

def test_backup_prompt_selection(runner, mocker):
    mock_modules = {name: mocker.Mock(return_value=True) for name in MODULES.keys()}
    mocker.patch("brewstanza.cli.MODULES", mock_modules)
    
    # Simulate user typing "1, 2" for Claude and Zsh
    result = runner.invoke(main, ["backup"], input="1, 2\n")
    
    assert result.exit_code == 0
    assert "Starting backups for: Claude, Zsh" in result.output
    
    mock_modules["Claude"].assert_called_once()
    mock_modules["Zsh"].assert_called_once()
    mock_modules["Homebrew"].assert_not_called()

def test_backup_invalid_selection(runner, mocker):
    mock_modules = {name: mocker.Mock(return_value=True) for name in MODULES.keys()}
    mocker.patch("brewstanza.cli.MODULES", mock_modules)
    
    result = runner.invoke(main, ["backup"], input="999\n")
    
    assert result.exit_code == 0
    assert "Invalid selection. Exiting." in result.output

def test_version_option(runner):
    result = runner.invoke(main, ["--version"])

    assert result.exit_code == 0
    assert "1.1.0" in result.output

def test_backup_refuses_home_dest(runner, mocker, tmp_path):
    mocker.patch("brewstanza.backups.safety.Path.home", return_value=tmp_path)
    mock_modules = {name: mocker.Mock(return_value=True) for name in MODULES.keys()}
    mocker.patch("brewstanza.cli.MODULES", mock_modules)

    result = runner.invoke(main, ["backup", "--dest", str(tmp_path), "--all"])

    assert result.exit_code == 1
    assert "Backup destination cannot be the home directory" in result.output
    for mock_func in mock_modules.values():
        mock_func.assert_not_called()
