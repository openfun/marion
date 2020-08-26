"""Tests for the marion.certificates application serializers"""

from django.urls import reverse

import pytest
from rest_framework import exceptions as drf_exceptions
from rest_framework.serializers import Serializer
from rest_framework.test import APIRequestFactory

from marion.certificates import factories, serializers


def test_json_schema_field_validation():
    """Test the schema validation for a JSONSchemaField"""
    # pylint: disable=missing-class-docstring

    # Missing schema attribute and field schema extraction method
    class TestSerializerA(Serializer):
        # pylint: disable=abstract-method

        misc = serializers.JSONSchemaField()

    instance = TestSerializerA(data={"misc": {"fullname": "Richie"}})
    assert instance.is_valid() is False
    assert len(instance.validated_data) == 0
    assert isinstance(instance.errors.get("misc")[0], drf_exceptions.ErrorDetail)
    assert "A schema is missing for the 'misc' field." in instance.errors.get("misc")[0]

    # With a schema attribute
    class TestSerializerB(Serializer):
        # pylint: disable=abstract-method

        misc = serializers.JSONSchemaField(
            schema={"type": "object", "properties": {"fullname": {"type": "string"}}}
        )

    instance = TestSerializerB(data={"misc": {"fullname": "Richie"}})
    assert instance.is_valid()

    instance = TestSerializerB(data={"misc": {"fullname": 2}})
    assert instance.is_valid() is False
    assert isinstance(instance.errors.get("misc")[0], drf_exceptions.ErrorDetail)
    assert "2 is not of type 'string'" in instance.errors.get("misc")[0]

    # Missing schema attribute but with field schema extraction method
    class TestSerializerC(Serializer):
        # pylint: disable=abstract-method

        misc = serializers.JSONSchemaField()

        def get_misc_schema(self):
            # pylint: disable=no-self-use,missing-function-docstring
            return {"type": "object", "properties": {"fullname": {"type": "string"}}}

    instance = TestSerializerC(data={"misc": {"fullname": "Richie"}})
    assert instance.is_valid()

    instance = TestSerializerC(data={"misc": {"fullname": 2}})
    assert instance.is_valid() is False
    assert isinstance(instance.errors.get("misc")[0], drf_exceptions.ErrorDetail)
    assert "2 is not of type 'string'" in instance.errors.get("misc")[0]

    # If both schema attribute and schema extraction method are provided, the
    # schema attribute should prevail
    class TestSerializerD(Serializer):
        # pylint: disable=abstract-method

        misc = serializers.JSONSchemaField(
            schema={
                "type": "object",
                "properties": {"amount": {"type": "integer"}},
                "additionalProperties": False,
            }
        )

        def get_misc_schema(self):
            # pylint: disable=no-self-use,missing-function-docstring
            return {"type": "object", "properties": {"fullname": {"type": "string"}}}

    instance = TestSerializerD(data={"misc": {"amount": 2}})
    assert instance.is_valid()

    instance = TestSerializerD(data={"misc": {"fullname": "Richie"}})
    assert instance.is_valid() is False
    assert isinstance(instance.errors.get("misc")[0], drf_exceptions.ErrorDetail)
    assert (
        "Additional properties are not allowed ('fullname' was unexpected)"
        in instance.errors.get("misc")[0]
    )


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
