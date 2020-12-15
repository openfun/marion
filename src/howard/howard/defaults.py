"""Default for the howard application"""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class CertificateIssuerChoices(TextChoices):
    """Active certificate issuers.

    Note that changing the default choices for the list of allowed certificate
    issuers may require to create and apply a database migration.

    """

    REALISATION = "howard.issuers.RealisationCertificate", _("Realisation")
