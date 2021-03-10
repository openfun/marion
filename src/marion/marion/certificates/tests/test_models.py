"""Tests for the marion.certificates application models"""

from django.core.exceptions import FieldError as DjangoFieldError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models as django_models
from django.template import Context

import pytest
from pydantic import BaseModel

from marion.certificates import exceptions, factories, issuers, models


def test_pydantic_model_field_validation():
    """Test the pydanticmodel validation for a PydanticModelField"""
    # pylint: disable=missing-class-docstring

    # Missing schema attribute and field schema extraction method
    class TestModelA(django_models.Model):
        data = models.PydanticModelField()

    instance = TestModelA(data={"fullname": "Richie"})

    with pytest.raises(
        DjangoFieldError, match="A pydantic model is missing for the 'data' field."
    ):
        instance.full_clean()

    # With a schema attribute
    class PydanticModelA(BaseModel):
        fullname: str

    class TestModelB(django_models.Model):
        data = models.PydanticModelField(pydantic_model=PydanticModelA)

    instance = TestModelB(data={"fullname": "Richie"})
    instance.full_clean()

    with pytest.raises(DjangoValidationError, match="none is not an allowed value"):
        instance = TestModelB(data={"fullname": None})
        instance.full_clean()

    # Missing schema attribute but with field schema extraction method
    class TestModelC(django_models.Model):
        data = models.PydanticModelField()

        def get_data_pydantic_model(self):
            # pylint: disable=no-self-use,missing-function-docstring
            return PydanticModelA

    instance = TestModelC(data={"fullname": "Richie"})
    instance.full_clean()

    with pytest.raises(DjangoValidationError, match="none is not an allowed value"):
        instance = TestModelC(data={"fullname": None})
        instance.full_clean()

    # If both schema attribute and schema extraction method are provided, the
    # schema attribute should prevail
    class PydanticModelB(BaseModel):
        amount: int

        class Config:
            extra = "forbid"

    class TestModelD(django_models.Model):
        data = models.PydanticModelField(pydantic_model=PydanticModelB)

        def get_data_pydantic_model(self):
            # pylint: disable=no-self-use,missing-function-docstring
            return PydanticModelB

    instance = TestModelD(data={"amount": 2})
    instance.full_clean()

    with pytest.raises(
        DjangoValidationError,
        match="extra fields not permitted",
    ):
        instance = TestModelD(data={"fullname": "Richie"})
        instance.full_clean()


@pytest.mark.django_db
def test_certificate_request_default_ordering():
    """Test the `CertificateRequest` default ordering"""

    first_certificate_request = factories.CertificateRequestFactory(
        issuer="marion.certificates.issuers.DummyCertificate",
        context_query={"fullname": "Richie Cunningham"},
    )
    second_certificate_request = factories.CertificateRequestFactory(
        issuer="marion.certificates.issuers.DummyCertificate",
        context_query={"fullname": "Marion Cunningham"},
    )
    third_certificate_request = factories.CertificateRequestFactory(
        issuer="marion.certificates.issuers.DummyCertificate",
        context_query={"fullname": "Howard Cunningham"},
    )
    fourth_certificate_request = factories.CertificateRequestFactory(
        issuer="marion.certificates.issuers.DummyCertificate",
        context_query={"fullname": "Joanie Cunningham"},
    )

    certificate_requests = models.CertificateRequest.objects.all()
    assert certificate_requests[0] == fourth_certificate_request
    assert certificate_requests[1] == third_certificate_request
    assert certificate_requests[2] == second_certificate_request
    assert certificate_requests[3] == first_certificate_request


@pytest.mark.django_db
def test_certificate_request_save(monkeypatch):
    """Test the `CertificateRequest.save()` method"""

    certificate_request = factories.CertificateRequestFactory(
        issuer="marion.certificates.issuers.DummyCertificate",
        context_query={"fullname": "Richie Cunningham"},
    )

    assert certificate_request.context_query.get("fullname") == "Richie Cunningham"

    # Test fetched context
    assert certificate_request.context.get("fullname") == "Richie Cunningham"
    assert "identifier" in certificate_request.context
    assert certificate_request.context.get("identifier") is not None

    # Test created certificate
    assert certificate_request.context.get("identifier") == str(
        certificate_request.certificate_id
    )
    assert certificate_request.id != certificate_request.certificate_id
    assert certificate_request.get_issuer().get_certificate_path().exists()

    # We should perform validation before saving
    certificate_request = factories.CertificateRequestFactory.build(
        issuer="marion.certificates.issuers.DummyCertificate",
        context_query={"fullname": ""},
    )
    with pytest.raises(
        DjangoValidationError,
        match="ensure this value has at least 2 characters",
    ):
        certificate_request.save()

    certificate_request = factories.CertificateRequestFactory.build(
        issuer="marion.certificates.issuers.DummyCertificate",
        context_query={"fullname": "Richie Cunningham"},
    )
    with monkeypatch.context() as mk_patch:
        mk_patch.setattr(
            issuers.DummyCertificate,
            "fetch_context",
            lambda *args, **kwargs: Context({"fullname": "Richie Cunningham"}),
        )
        with pytest.raises(
            exceptions.CertificateIssuerContextValidationError,
            match="Certificate issuer context is not valid",
        ):
            certificate_request.save()


def test_certificate_request_get_issuer_class(monkeypatch):
    """Test the `CertificateRequest.get_issuer_class()` method"""

    # pylint: disable=no-member
    monkeypatch.setattr(
        models.CertificateRequest.issuer.field,
        "choices",
        [
            ("marion.certificates.issuers.Arnold", "Arnold"),
            ("marion.certificates.issuers.DummyCertificate", "Dummy"),
            ("marion.certificates.issuers.Marsha", "Marsha"),
            ("marion.certificates.issuers.Richie", "Richie"),
            ("howard.certificates.issuers.Richie", "Richou"),
            ("issuers.Richie", "Richinou"),
            ("Richie", "Riccardo"),
        ],
    )

    with pytest.raises(
        exceptions.InvalidCertificateIssuer, match="Fonzy is not an allowed issuer"
    ):
        models.CertificateRequest.get_issuer_class("Fonzy")

    with pytest.raises(
        exceptions.InvalidCertificateIssuer,
        match="Issuer class name should be unique, found 4 for Richie",
    ):
        models.CertificateRequest.get_issuer_class("Richie")

    assert isinstance(
        models.CertificateRequest.get_issuer_class("DummyCertificate")(),
        issuers.DummyCertificate,
    )


@pytest.mark.django_db
def test_certificate_request_get_issuer():
    """Test the `CertificateRequest.get_issuer()` method"""

    certificate_request = factories.CertificateRequestFactory(
        issuer="marion.certificates.issuers.DummyCertificate",
        context_query={"fullname": "Richie Cunningham"},
    )

    assert isinstance(certificate_request.get_issuer(), issuers.DummyCertificate)


@pytest.mark.django_db
def test_certificate_request_get_certificate_url():
    """Test the `CertificateRequest.get_certificate_url()` method"""

    certificate_request = factories.CertificateRequestFactory(
        issuer="marion.certificates.issuers.DummyCertificate",
        context_query={"fullname": "Richie Cunningham"},
    )

    assert (
        certificate_request.get_certificate_url()
        == f"/media/{certificate_request.certificate_id}.pdf"
    )
    assert (
        certificate_request.get_certificate_url(host="www.happy-days.com")
        == f"https://www.happy-days.com/media/{certificate_request.certificate_id}.pdf"
    )
    assert (
        certificate_request.get_certificate_url(
            host="www.happy-days.com", schema="http"
        )
        == f"http://www.happy-days.com/media/{certificate_request.certificate_id}.pdf"
    )
