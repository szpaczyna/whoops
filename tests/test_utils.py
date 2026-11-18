import pytest

from src.utils import parseRange


@pytest.mark.parametrize(
    "range_str, expected",
    [
        ("7d", 7),
        ("6m", 180),
        ("1y", 365),
        ("0d", 0),
    ],
)
def test_parse_range_valid(range_str, expected):
    assert parseRange(range_str) == expected


@pytest.mark.parametrize(
    "range_str",
    ["-3d", "999999y", "11y", "xd", "3w", "", "3"],
)
def test_parse_range_invalid(range_str):
    with pytest.raises(ValueError):
        parseRange(range_str)
