"""Tests for the marion application models"""

from django.core.exceptions import FieldError as DjangoFieldError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models as django_models

import pytest
from pydantic import BaseModel

from marion import exceptions, factories, issuers, models


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
def test_document_request_default_ordering():
    """Test the `DocumentRequest` default ordering"""

    first_document_request = factories.DocumentRequestFactory(
        issuer="marion.issuers.DummyDocument",
        context_query={"fullname": "Richie Cunningham"},
    )
    second_document_request = factories.DocumentRequestFactory(
        issuer="marion.issuers.DummyDocument",
        context_query={"fullname": "Marion Cunningham"},
    )
    third_document_request = factories.DocumentRequestFactory(
        issuer="marion.issuers.DummyDocument",
        context_query={"fullname": "Howard Cunningham"},
    )
    fourth_document_request = factories.DocumentRequestFactory(
        issuer="marion.issuers.DummyDocument",
        context_query={"fullname": "Joanie Cunningham"},
    )

    document_requests = models.DocumentRequest.objects.all()
    assert document_requests[0] == fourth_document_request
    assert document_requests[1] == third_document_request
    assert document_requests[2] == second_document_request
    assert document_requests[3] == first_document_request


@pytest.mark.django_db
def test_document_request_save(monkeypatch):
    """Test the `DocumentRequest.save()` method"""

    document_request = factories.DocumentRequestFactory(
        issuer="marion.issuers.DummyDocument",
        context_query={"fullname": "Richie Cunningham"},
    )

    assert document_request.context_query.get("fullname") == "Richie Cunningham"

    # Test fetched context
    assert document_request.context.get("fullname") == "Richie Cunningham"
    assert "identifier" in document_request.context
    assert document_request.context.get("identifier") is not None

    # Test created document
    assert document_request.context.get("identifier") == str(
        document_request.document_id
    )
    assert document_request.id != document_request.document_id
    assert document_request.get_issuer().get_document_path().exists()

    # We should perform validation before saving
    document_request = factories.DocumentRequestFactory.build(
        issuer="marion.issuers.DummyDocument",
        context_query={"fullname": ""},
    )
    with pytest.raises(
        DjangoValidationError,
        match="ensure this value has at least 2 characters",
    ):
        document_request.save()

    document_request = factories.DocumentRequestFactory.build(
        issuer="marion.issuers.DummyDocument",
        context_query={"fullname": "Richie Cunningham"},
    )
    with monkeypatch.context() as mk_patch:
        mk_patch.setattr(
            issuers.DummyDocument,
            "fetch_context",
            lambda *args, **kwargs: {"fullname": "Richie Cunningham"},
        )
        with pytest.raises(
            exceptions.DocumentIssuerContextValidationError,
            match="identifier\n  field required",
        ):
            document_request.save()


def test_document_request_get_issuer_class(monkeypatch):
    """Test the `DocumentRequest.get_issuer_class()` method"""

    # pylint: disable=no-member
    monkeypatch.setattr(
        models.DocumentRequest.issuer.field,
        "choices",
        [
            ("marion.issuers.Arnold", "Arnold"),
            ("marion.issuers.DummyDocument", "Dummy"),
            ("marion.issuers.Marsha", "Marsha"),
            ("marion.issuers.Richie", "Richie"),
            ("howard.documents.issuers.Richie", "Richou"),
            ("issuers.Richie", "Richinou"),
            ("Richie", "Riccardo"),
        ],
    )

    with pytest.raises(
        exceptions.InvalidDocumentIssuer, match="Fonzy is not an allowed issuer"
    ):
        models.DocumentRequest.get_issuer_class("Fonzy")

    with pytest.raises(
        exceptions.InvalidDocumentIssuer,
        match="Issuer class name should be unique, found 4 for Richie",
    ):
        models.DocumentRequest.get_issuer_class("Richie")

    assert isinstance(
        models.DocumentRequest.get_issuer_class("DummyDocument")(),
        issuers.DummyDocument,
    )


@pytest.mark.django_db
def test_document_request_get_issuer():
    """Test the `DocumentRequest.get_issuer()` method"""

    document_request = factories.DocumentRequestFactory(
        issuer="marion.issuers.DummyDocument",
        context_query={"fullname": "Richie Cunningham"},
    )

    assert isinstance(document_request.get_issuer(), issuers.DummyDocument)


@pytest.mark.django_db
def test_document_request_get_document_url():
    """Test the `DocumentRequest.get_document_url()` method"""

    document_request = factories.DocumentRequestFactory(
        issuer="marion.issuers.DummyDocument",
        context_query={"fullname": "Richie Cunningham"},
    )

    assert (
        document_request.get_document_url()
        == f"/media/{document_request.document_id}.pdf"
    )
    assert (
        document_request.get_document_url(host="www.happy-days.com")
        == f"https://www.happy-days.com/media/{document_request.document_id}.pdf"
    )
    assert (
        document_request.get_document_url(host="www.happy-days.com", schema="http")
        == f"http://www.happy-days.com/media/{document_request.document_id}.pdf"
    )
