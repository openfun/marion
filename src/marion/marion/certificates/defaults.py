"""Default settings for the marion.certificates application.

Application settings should always be imported from here to ensure that:

1. they can be overriden in the Django project settings using the following
naming pattern: MARION_{{ << setting name >> }}, _e.g._ MARION_FOO for the FOO
setting of marion.

2. it has relevant, properly maintained defaults.

"""

from pathlib import Path

from django.conf import settings
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

CERTIFICATE_ISSUER_CHOICES_CLASS = getattr(
    settings,
    "MARION_CERTIFICATE_ISSUER_CHOICES_CLASS",
    "marion.certificates.defaults.CertificateIssuerChoices",
)
CERTIFICATES_ROOT = getattr(
    settings, "MARION_CERTIFICATES_ROOT", Path(settings.MEDIA_ROOT)
)
CERTIFICATES_TEMPLATE_ROOT = getattr(
    settings, "MARION_CERTIFICATES_TEMPLATE_ROOT", Path("marion/certificates")
)


class CertificateIssuerChoices(TextChoices):
    """Active certificate issuers.

    Note that changing the default choices for the list of allowed certificate
    issuers may require to create and apply a database migration.

    """

    DUMMY = "marion.certificates.issuers.DummyCertificate", _("Dummy")
