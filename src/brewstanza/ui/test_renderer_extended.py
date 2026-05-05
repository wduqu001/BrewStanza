"""
Extended UI renderer tests — covers methods not exercised by test_renderer.py.
"""


from rich.console import Console

from brewstanza.analyzer.storage import StorageItem, StorageReport
from brewstanza.ui.renderer import UIRenderer


def _renderer() -> UIRenderer:
    """Create a UIRenderer that records output for inspection."""
    r = UIRenderer(no_color=True)
    r.console = Console(record=True, no_color=True)
    return r


# ---------------------------------------------------------------------------
# render_app_table — rows
# ---------------------------------------------------------------------------


class TestRenderAppTable:
    """render_app_table with actual rows."""

    def test_renders_app_name_and_size(self) -> None:
        r = _renderer()
        r.render_app_table(
            [{"name": "Safari", "path": "/Applications/Safari.app", "size": 100 * 1024 * 1024}]
        )
        out = r.console.export_text()
        assert "Safari" in out
        assert "100.0 MB" in out

    def test_renders_path(self) -> None:
        r = _renderer()
        r.render_app_table(
            [{"name": "Xcode", "path": "/Applications/Xcode.app", "size": 0}]
        )
        out = r.console.export_text()
        assert "Xcode.app" in out

    def test_renders_multiple_apps(self) -> None:
        r = _renderer()
        r.render_app_table(
            [
                {"name": "App1", "path": "/Applications/App1.app", "size": 1024},
                {"name": "App2", "path": "/Applications/App2.app", "size": 2048},
            ]
        )
        out = r.console.export_text()
        assert "App1" in out
        assert "App2" in out


# ---------------------------------------------------------------------------
# render_storage_breakdown
# ---------------------------------------------------------------------------


class TestRenderStorageBreakdown:
    """render_storage_breakdown covers lines 77-113."""

    def _report(self, with_items: bool = True) -> StorageReport:
        items: list[StorageItem] = (
            [
                {"name": "git", "type": "homebrew", "size": 1_000_000, "percentage": 33.3},
                {"name": "Safari.app", "type": "app", "size": 2_000_000, "percentage": 66.7},
            ]
            if with_items
            else []
        )
        return {
            "homebrew_total": 1_000_000,
            "apps_total": 2_000_000,
            "combined_total": 3_000_000,
            "items": items,
        }

    def test_renders_homebrew_total(self) -> None:
        r = _renderer()
        r.render_storage_breakdown(self._report())
        out = r.console.export_text()
        assert "Homebrew" in out

    def test_renders_apps_total(self) -> None:
        r = _renderer()
        r.render_storage_breakdown(self._report())
        out = r.console.export_text()
        assert "Applications" in out

    def test_renders_top_consumers_section(self) -> None:
        r = _renderer()
        r.render_storage_breakdown(self._report(with_items=True))
        out = r.console.export_text()
        assert "git" in out
        assert "Safari.app" in out

    def test_no_top_consumers_when_items_empty(self) -> None:
        r = _renderer()
        r.render_storage_breakdown(self._report(with_items=False))
        out = r.console.export_text()
        # "Top Consumers" heading should NOT be present
        assert "Top Consumers" not in out

    def test_renders_percentage_bars(self) -> None:
        r = _renderer()
        r.render_storage_breakdown(self._report(with_items=True))
        out = r.console.export_text()
        # At least one percentage should be visible
        assert "%" in out


# ---------------------------------------------------------------------------
# render_package_detail
# ---------------------------------------------------------------------------


class TestRenderPackageDetail:
    """render_package_detail covers lines 115-142."""

    def _pkg(self) -> dict:  # type: ignore[type-arg]
        return {
            "name": "wget",
            "desc": "Internet file retriever",
            "version": "1.21.4",
            "size": 5_242_880,
            "path": "/opt/homebrew/Cellar/wget/1.21.4",
        }

    def test_renders_package_name(self) -> None:
        r = _renderer()
        r.render_package_detail(self._pkg())
        assert "wget" in r.console.export_text()

    def test_renders_description(self) -> None:
        r = _renderer()
        r.render_package_detail(self._pkg())
        assert "Internet file retriever" in r.console.export_text()

    def test_renders_version(self) -> None:
        r = _renderer()
        r.render_package_detail(self._pkg())
        assert "1.21.4" in r.console.export_text()

    def test_renders_size_human(self) -> None:
        r = _renderer()
        r.render_package_detail(self._pkg())
        assert "5.0 MB" in r.console.export_text()

    def test_renders_cellar_path(self) -> None:
        r = _renderer()
        r.render_package_detail(self._pkg())
        assert "/opt/homebrew/Cellar/wget/1.21.4" in r.console.export_text()

    def test_renders_uninstall_command(self) -> None:
        r = _renderer()
        r.render_package_detail(self._pkg())
        assert "brew uninstall wget" in r.console.export_text()

    def test_renders_panel_title(self) -> None:
        r = _renderer()
        r.render_package_detail(self._pkg())
        assert "Package Info" in r.console.export_text()


# ---------------------------------------------------------------------------
# render_removal_instructions
# ---------------------------------------------------------------------------


class TestRenderRemovalInstructions:
    """render_removal_instructions covers lines 144-159."""

    def test_renders_rm_command(self) -> None:
        r = _renderer()
        r.render_removal_instructions({"name": "Sketch", "path": "/Applications/Sketch.app"})
        out = r.console.export_text()
        assert "rm -rf" in out
        assert "Sketch.app" in out

    def test_renders_panel_title(self) -> None:
        r = _renderer()
        r.render_removal_instructions({"name": "Sketch", "path": "/Applications/Sketch.app"})
        assert "Uninstall Instructions" in r.console.export_text()
