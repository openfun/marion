"""Factories for the marion.documents application"""

from factory.django import DjangoModelFactory

from . import models


class DocumentRequestFactory(DjangoModelFactory):
    """DocumentRequest factory"""

    class Meta:  # noqa
        model = models.DocumentRequest
