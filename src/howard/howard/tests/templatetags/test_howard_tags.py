"""Test suite for howard template tags"""
from pathlib import Path

from howard.templatetags.howard_tags import is_path
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.provisional import urls


@given(st.builds(Path, urls()), urls())
def test_howard_tags_is_path(path, not_path):
    """Test the filter template tag howard_tags.is_path."""

    assert is_path(path) is True
    assert is_path(not_path) is False
