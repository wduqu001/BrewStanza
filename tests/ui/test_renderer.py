"""
Tests for BrewStanza UI renderer.
"""

from rich.console import Console

from brewstanza.ui.renderer import UIRenderer


def test_render_package_table_includes_package_values():
    renderer = UIRenderer(no_color=True)
    renderer.console = Console(record=True, no_color=True)

    packages = [
        {"name": "pkgA", "version": "1.2.3", "size": "10 MB"},
        {"name": "pkgB", "version": "4.5.6", "size": "25 MB"},
    ]

    renderer.render_package_table(packages, title="Test Packages")
    output = renderer.console.export_text()

    assert "Test Packages" in output
    assert "pkgA" in output
    assert "1.2.3" in output
    assert "10 MB" in output
    assert "pkgB" in output
    assert "25 MB" in output


def test_render_app_table_with_no_rows_prints_header():
    renderer = UIRenderer(no_color=True)
    renderer.console = Console(record=True, no_color=True)

    renderer.render_app_table([], title="Test Apps")
    output = renderer.console.export_text()

    assert "Test Apps" in output
    assert "Name" in output
    assert "Category" in output
    assert "Version" in output
    assert "Size" in output


def test_print_helpers_display_markers():
    renderer = UIRenderer(no_color=True)
    renderer.console = Console(record=True, no_color=True)

    renderer.print_success("Successful")
    renderer.print_error("Failed")
    renderer.print_warning("Watch out")
    renderer.print_info("For your information")

    output = renderer.console.export_text()

    assert "✓" in output
    assert "Successful" in output
    assert "✗" in output
    assert "Failed" in output
    assert "⚠" in output
    assert "Watch out" in output
    assert "ℹ" in output
    assert "For your information" in output
