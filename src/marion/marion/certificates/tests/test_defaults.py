"""Tests for the marion.certificates application defaults"""

import importlib
from pathlib import Path

from marion.certificates import defaults


def test_defaults_overrides_with_settings(settings):
    """Test marion.certificates.defaults overrides with settings definition"""

    settings.MARION_CERTIFICATE_ISSUER_CHOICES_CLASS = (
        "howard.certificates.CertificateIssuerChoices"
    )
    settings.MARION_CERTIFICATES_ROOT = Path("/tmp/certificates/abc")
    settings.MARION_CERTIFICATES_TEMPLATE_ROOT = Path("howard/certificates/abc")

    # Force module reload to take into account setting override as it is loaded
    # very early in the stack
    importlib.reload(defaults)

    assert (
        defaults.CERTIFICATE_ISSUER_CHOICES_CLASS
        == "howard.certificates.CertificateIssuerChoices"
    )
    assert defaults.CERTIFICATES_ROOT == Path("/tmp/certificates/abc")
    assert defaults.CERTIFICATES_TEMPLATE_ROOT == Path("howard/certificates/abc")


def teardown_function():
    """Executed at the end of the current test suite"""

    # Force module reload as the default test settings have been restored
    importlib.reload(defaults)
