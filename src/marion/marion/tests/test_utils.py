"""Tests for the marion.utils module"""

from pathlib import Path

from django.conf import settings

import marion
from marion.utils import static_file_fetcher


# pylint: disable=invalid-name
def test_static_file_fetcher(fs):
    """Test weasyprint custom static file fetcher."""

    # Create a fake static file for the marion app
    relative_static_file_path = "marion/test.txt"
    static_file_path = Path(f"{marion.__path__[0]}/static/{relative_static_file_path}")
    fs.create_file(static_file_path, contents="This is content.")

    # Fetch this file
    data = static_file_fetcher(
        f"file://{settings.STATIC_URL}{relative_static_file_path}"
    )
    assert data.get("filename") == static_file_path.name
    assert data.get("mime_type") == "text/plain"
    file_ = data.get("file_obj")
    assert file_.readlines() == [
        b"This is content.",
    ]
    file_.close()

    # Test Weasyprint fallback (if the file is not located in a Django static file path)
    file_path = "/tmp/foo.txt"
    fs.create_file(file_path, contents="This is a different content.")

    data = static_file_fetcher(f"file://{file_path}")
    assert data.get("mime_type") == "text/plain"
    file_ = data.get("file_obj")
    assert file_.readlines() == [
        b"This is a different content.",
    ]
    file_.close()
