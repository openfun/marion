"""Default settings for the marion application.

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

DOCUMENT_ISSUER_CHOICES_CLASS = getattr(
    settings,
    "MARION_DOCUMENT_ISSUER_CHOICES_CLASS",
    "marion.defaults.DocumentIssuerChoices",
)
DOCUMENTS_ROOT = getattr(settings, "MARION_DOCUMENTS_ROOT", Path(settings.MEDIA_ROOT))
DOCUMENTS_TEMPLATE_ROOT = getattr(
    settings, "MARION_DOCUMENTS_TEMPLATE_ROOT", Path("marion")
)


class DocumentIssuerChoices(TextChoices):
    """Active document issuers.

    Note that changing the default choices for the list of allowed document
    issuers may require to create and apply a database migration.

    """

    DUMMY = "marion.issuers.DummyDocument", _("Dummy")
