"""Marion, the documents factory"""

import importlib.metadata
from pathlib import Path

from setuptools.config import read_configuration


def _get_version():
    """Get version from installed package with a fallback to the setup.cfg version
    string.

    """

    try:
        return importlib.metadata.version("django-marion")
    except importlib.metadata.PackageNotFoundError:
        return read_configuration(Path(__file__).parent / ".." / "setup.cfg")[
            "metadata"
        ]["version"]


__version__ = _get_version()
