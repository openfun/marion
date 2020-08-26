"""Tests for the marion.certificates application models"""

from django.core.exceptions import FieldError as DjangoFieldError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models as django_models
from django.template import Context

import pytest

from marion.certificates import exceptions, factories, issuers, models


def test_json_schema_field_validation():
    """Test schema validation for the JSONSchema field"""
    # pylint: disable=missing-class-docstring

    # Missing schema attribute and field schema extraction method
    class TestModelA(django_models.Model):
        data = models.JSONSchemaField()

    instance = TestModelA(data={"fullname": "Richie"})
    with pytest.raises(
        DjangoFieldError, match="A schema is missing for the 'data' field."
    ):
        instance.full_clean()

    # With a schema attribute
    class TestModelB(django_models.Model):
        data = models.JSONSchemaField(
            schema={"type": "object", "properties": {"fullname": {"type": "string"}}}
        )

    instance = TestModelB(data={"fullname": "Richie"})
    instance.full_clean()

    with pytest.raises(DjangoValidationError, match="2 is not of type 'string'"):
        instance = TestModelB(data={"fullname": 2})
        instance.full_clean()

    # Missing schema attribute but with field schema extraction method
    class TestModelC(django_models.Model):
        data = models.JSONSchemaField()

        def get_data_schema(self):
            # pylint: disable=no-self-use,missing-function-docstring
            return {"type": "object", "properties": {"fullname": {"type": "string"}}}

    instance = TestModelC(data={"fullname": "Richie"})
    instance.full_clean()

    with pytest.raises(DjangoValidationError, match="2 is not of type 'string'"):
        instance = TestModelC(data={"fullname": 2})
        instance.full_clean()

    # If both schema attribute and schema extraction method are provided, the
    # schema attribute should prevail
    class TestModelD(django_models.Model):
        data = models.JSONSchemaField(
            schema={
                "type": "object",
                "properties": {"amount": {"type": "integer"}},
                "additionalProperties": False,
            }
        )

        def get_data_schema(self):
            # pylint: disable=no-self-use,missing-function-docstring
            return {"type": "object", "properties": {"fullname": {"type": "string"}}}

    instance = TestModelD(data={"amount": 2})
    instance.full_clean()

    with pytest.raises(
        DjangoValidationError,
        match=r"Additional properties are not allowed \('fullname' was unexpected\)",
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
        DjangoValidationError, match="context_query.*'' is too short",
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
