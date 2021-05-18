"""Default for the howard application"""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class DocumentIssuerChoices(TextChoices):
    """Active document issuers.

    Note that changing the default choices for the list of allowed document
    issuers may require to create and apply a database migration.

    """

    REALISATION = "howard.issuers.RealisationCertificate", _("Realisation")
    INVOICE = "howard.issuers.InvoiceDocument", _("Invoice")
    CERTIFICATE = "howard.issuers.CertificateDocument", _("Certificate")
