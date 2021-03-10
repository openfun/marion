"""Tests for the marion.certificates application serializers"""

from django.urls import reverse

import pytest
from pydantic import BaseModel
from rest_framework import exceptions as drf_exceptions
from rest_framework.serializers import Serializer
from rest_framework.test import APIRequestFactory

from marion.certificates import factories, serializers


def test_pydantic_model_field_validation():
    """Test the pydantic model validation for a PydanticModelField"""
    # pylint: disable=missing-class-docstring

    # Missing pydantic model attribute and field pydantic model extraction method
    class TestSerializerA(Serializer):
        # pylint: disable=abstract-method

        misc = serializers.PydanticModelField()

    instance = TestSerializerA(data={"misc": {"fullname": "Richie"}})
    assert instance.is_valid() is False
    assert len(instance.validated_data) == 0
    assert isinstance(instance.errors.get("misc")[0], drf_exceptions.ErrorDetail)
    assert (
        "A pydantic model is missing for the 'misc' field."
        in instance.errors.get("misc")[0]
    )

    # With a pydantic model attribute
    class PydanticModelA(BaseModel):
        fullname: str

    class TestSerializerB(Serializer):
        # pylint: disable=abstract-method

        misc = serializers.PydanticModelField(pydantic_model=PydanticModelA)

    instance = TestSerializerB(data={"misc": {"fullname": "Richie"}})
    assert instance.is_valid()

    instance = TestSerializerB(data={"misc": {"fullname": None}})
    assert instance.is_valid() is False
    assert isinstance(instance.errors.get("misc")[0], drf_exceptions.ErrorDetail)
    assert "none is not an allowed value" in instance.errors.get("misc")[0]

    # Missing pydantic model attribute but with field pydantic model extraction method
    class TestSerializerC(Serializer):
        # pylint: disable=abstract-method

        misc = serializers.PydanticModelField()

        def get_misc_pydantic_model(self):
            # pylint: disable=no-self-use,missing-function-docstring
            return PydanticModelA

    instance = TestSerializerC(data={"misc": {"fullname": "Richie"}})
    assert instance.is_valid()

    instance = TestSerializerC(data={"misc": {"fullname": None}})
    assert instance.is_valid() is False
    assert isinstance(instance.errors.get("misc")[0], drf_exceptions.ErrorDetail)
    assert "none is not an allowed value" in instance.errors.get("misc")[0]

    # If both pydantic model attribute and pydantic mode extraction method are provided,
    # the pydantic model attribute should prevail.
    class PydanticModelB(BaseModel):
        amount: int

        class Config:
            extra = "forbid"

    class TestSerializerD(Serializer):
        # pylint: disable=abstract-method

        misc = serializers.PydanticModelField(pydantic_model=PydanticModelB)

        def get_misc_pydantic_model(self):
            # pylint: disable=no-self-use,missing-function-docstring
            return PydanticModelB

    instance = TestSerializerD(data={"misc": {"amount": 2}})
    assert instance.is_valid()

    instance = TestSerializerD(data={"misc": {"fullname": "Richie"}})
    assert instance.is_valid() is False
    assert isinstance(instance.errors.get("misc")[0], drf_exceptions.ErrorDetail)
    assert "extra fields not permitted" in instance.errors.get("misc")[0]


@pytest.mark.django_db
def test_certificate_request_serializer_certificate_url_field():
    """Test the certificate request serializer certificate_url field"""

    certificate_request = factories.CertificateRequestFactory(
        issuer="marion.certificates.issuers.DummyCertificate",
        context_query={"fullname": "Richie Cunningham"},
    )

    factory = APIRequestFactory()
    request = factory.get(reverse("certificaterequest-list"))

    serialized_certificate_request = serializers.CertificateRequestSerializer(
        certificate_request, context={"request": request}
    )

    assert (
        serialized_certificate_request.data.get("certificate_url")
        == f"http://testserver/media/{certificate_request.certificate_id}.pdf"
    )
