"""Documents generation utilities."""

import mimetypes
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.staticfiles.finders import find
from django.core.exceptions import SuspiciousFileOperation

import weasyprint


def static_file_fetcher(url, *args, **kwargs):
    """Weasyprint static files fetcher.

    If the file URL starts with 'file://', it will be fetched from the configured
    storage.

    The following code has been adapted from the django-weasyprint project [1].

    References:

    [1] https://github.com/fdemmer/django-weasyprint/
    """

    if url.startswith("file:"):
        mime_type, encoding = mimetypes.guess_type(url)
        url_path = urlparse(url).path
        data = {
            "mime_type": mime_type,
            "encoding": encoding,
            "filename": Path(url_path).name,
        }

        path = url_path.replace(settings.STATIC_URL, "", 1)
        try:
            data["file_obj"] = open(find(path), "rb")
        # A SuspiciousFileOperation is raised by Django if the file has been
        # found outside referenced static file paths. In this case, we ignore
        # this error and fallback to the default Weasyprint fetcher for files
        # referenced with the file:// protocol.
        except SuspiciousFileOperation:
            pass
        else:
            return data

    # Fall back to weasyprint default fetcher
    return weasyprint.default_url_fetcher(url, *args, **kwargs)
