import pytest
from pathlib import Path
from click.testing import CliRunner
from brewstanza.cli import main, MODULES

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
