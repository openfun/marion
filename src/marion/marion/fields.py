"""Custom fields for the marion application"""

from django.db import models
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from .defaults import DOCUMENT_ISSUER_CHOICES_CLASS

DocumentIssuerChoices = import_string(DOCUMENT_ISSUER_CHOICES_CLASS)


class LazyChoiceField(models.CharField):
    """
    LazyChoiceField is a CharField with choices defined at class level.
    This class allows to update choices without creating a migration.
    """

    description = "Text field with lazy choices"
    lazy_choices = []

    def __init__(self, *args, **kwargs):
        """Set field choices with the class attribute `lazy_choices`"""
        kwargs["choices"] = self.lazy_choices
        super().__init__(*args, **kwargs)


class IssuerLazyChoiceField(LazyChoiceField):
    """A LazyChoiceField with DocumentIssuer classes as choices."""

    description = _("Document issuer type")
    lazy_choices = DocumentIssuerChoices.choices
