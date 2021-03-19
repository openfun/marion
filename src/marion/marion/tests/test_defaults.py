"""Tests for the marion application defaults"""

import importlib
from pathlib import Path

from marion import defaults


def test_defaults_overrides_with_settings(settings):
    """Test marion.defaults overrides with settings definition"""

    settings.MARION_DOCUMENT_ISSUER_CHOICES_CLASS = (
        "howard.documents.DocumentIssuerChoices"
    )
    settings.MARION_DOCUMENTS_ROOT = Path("/tmp/documents/abc")
    settings.MARION_DOCUMENTS_TEMPLATE_ROOT = Path("howard/documents/abc")

    # Force module reload to take into account setting override as it is loaded
    # very early in the stack
    importlib.reload(defaults)

    assert (
        defaults.DOCUMENT_ISSUER_CHOICES_CLASS
        == "howard.documents.DocumentIssuerChoices"
    )
    assert defaults.DOCUMENTS_ROOT == Path("/tmp/documents/abc")
    assert defaults.DOCUMENTS_TEMPLATE_ROOT == Path("howard/documents/abc")


def teardown_function():
    """Executed at the end of the current test suite"""

    # Force module reload as the default test settings have been restored
    importlib.reload(defaults)
