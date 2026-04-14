"""
Tests for BrewStanza storage analyzer.
"""

from brewstanza.analyzer.storage import StorageAnalyzer


def test_format_size_human_readable() -> None:
    assert StorageAnalyzer.format_size(0) == "0.0 B"
    assert StorageAnalyzer.format_size(512) == "512.0 B"
    assert StorageAnalyzer.format_size(1024) == "1.0 KB"
    assert StorageAnalyzer.format_size(1_048_576) == "1.0 MB"
    assert StorageAnalyzer.format_size(1_073_741_824) == "1.0 GB"


def test_get_top_consumers_sorted_by_size_desc() -> None:
    analyzer = StorageAnalyzer()
    data = [
        {"name": "one", "size": 100},
        {"name": "two", "size": 300},
        {"name": "three", "size": 200},
    ]

    top_two = analyzer.get_top_consumers(data, n=2)

    assert len(top_two) == 2
    assert top_two[0]["name"] == "two"
    assert top_two[1]["name"] == "three"


def test_get_percentage_distribution_values() -> None:
    analyzer = StorageAnalyzer()
    sizes = {"a": 100, "b": 300, "c": 600}

    dist = analyzer.get_percentage_distribution(sizes)

    assert dist["a"] == 10.0
    assert dist["b"] == 30.0
    assert dist["c"] == 60.0
