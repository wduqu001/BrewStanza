"""
Tests for BrewStanza CLI.
"""

import pytest
from click.testing import CliRunner

from brewstanza.cli import main


class TestCLI:
    """Test CLI commands."""
    
    def test_version(self):
        """Test --version flag."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output
    
    def test_help(self):
        """Test --help flag."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "BrewStanza" in result.output
        assert "brew" in result.output
        assert "apps" in result.output
    
    def test_brew_help(self):
        """Test brew --help."""
        runner = CliRunner()
        result = runner.invoke(main, ["brew", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "info" in result.output
    
    def test_apps_help(self):
        """Test apps --help."""
        runner = CliRunner()
        result = runner.invoke(main, ["apps", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output
    
    def test_brew_list_placeholder(self):
        """Test brew list placeholder message."""
        runner = CliRunner()
        result = runner.invoke(main, ["brew", "list"])
        assert result.exit_code == 0
        assert "not yet implemented" in result.output
