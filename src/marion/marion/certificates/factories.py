"""Factories for the marion.certificates application"""

from factory.django import DjangoModelFactory

from . import models


class CertificateRequestFactory(DjangoModelFactory):
    """CertificateRequest factory"""

    class Meta:  # noqa
        model = models.CertificateRequest
