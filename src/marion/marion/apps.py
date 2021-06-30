"""AppConfig for the marion application"""

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from .defaults import DOCUMENT_ISSUER_CHOICES


# pylint: disable=unused-argument
def create_issuer_objects(sender, **kwargs):
    """Creates Issuer Model instances based on marion settings"""

    # pylint: disable=import-outside-toplevel
    from .models import IssuerChoice

    for issuer in DOCUMENT_ISSUER_CHOICES:
        IssuerChoice.objects.get_or_create(**issuer)


class MarionConfig(AppConfig):
    """Marion application configuration"""

    default = False
    name = "marion"

    def ready(self):
        post_migrate.connect(create_issuer_objects, sender=self)
