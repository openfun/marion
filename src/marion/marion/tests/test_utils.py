"""Tests for the marion.utils module"""

import re
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles.management.commands import collectstatic
from django.templatetags.static import StaticNode
from django.test import override_settings

import marion
from marion.utils import static_file_fetcher


# pylint: disable=invalid-name
def test_static_file_fetcher(fs):
    """Test weasyprint custom static file fetcher."""

    # Create a fake static file for the marion app
    relative_static_file_path = "marion/test.txt"
    static_file_path = Path(f"{settings.STATIC_ROOT}/{relative_static_file_path}")
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


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
)
def test_static_file_fetcher_with_hashed_statics(fs):
    """Test weasyprint custom static file fetcher with hashed static files."""

    # Create a fake static file into marion app
    relative_static_file_path = "marion/test.txt"
    static_file_path = Path(f"{marion.__path__[0]}/static/{relative_static_file_path}")
    fs.create_file(static_file_path, contents="This is content.")

    # Collect static files to process the fresh new created static file test.txt
    # As ManifestStaticFilesStorage is the active backend storage for static,
    # it stores the file names it handles by appending the MD5 hash of the file’s
    # content to the filename.
    # In this way, we are able below to ensure that `static_file_fetcher` is able to
    # access to those static files.
    collectstatic.Command().handle(
        clear=True,
        dry_run=False,
        ignore_patterns=[],
        interactive=False,
        link=False,
        post_process=True,
        use_default_ignore_patterns=True,
        verbosity=0,
    )

    # Retrieve the static file path
    path = f'file://{StaticNode.handle_simple("marion/test.txt")}'
    # The file path should target the hashed static file
    assert re.search(r"\/static\/marion\/test\.[a-f0-9]*\.txt$", path)

    # Fetch the file
    data = static_file_fetcher(path)

    # The filename should contain a hash
    assert re.search(r"^test\.[a-f0-9]*\.txt$", data.get("filename"))
    assert data.get("mime_type") == "text/plain"
    file_ = data.get("file_obj")
    assert file_.readlines() == [
        b"This is content.",
    ]
    file_.close()
