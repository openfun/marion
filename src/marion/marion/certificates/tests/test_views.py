"""Tests for the marion.certificates application views"""

import json
import tempfile
from pathlib import Path

from django.template import Context
from django.urls import reverse

import pytest
from pytest_django import asserts as django_assertions
from rest_framework import exceptions as drf_exceptions
from rest_framework import status
from rest_framework.test import APIClient

from marion.certificates import defaults, models
from marion.certificates.issuers import DummyCertificate

client = APIClient()


def count_certificates(root):
    """Return the number of generated PDF files in the root directory"""

    return len(list(root.glob("*.pdf")))


@pytest.mark.django_db
def test_certificate_request_viewset_post(monkeypatch):
    """Test the CertificateRequestViewSet create view"""

    monkeypatch.setattr(defaults, "CERTIFICATES_ROOT", Path(tempfile.mkdtemp()))

    url = reverse("certificaterequest-list")

    assert count_certificates(defaults.CERTIFICATES_ROOT) == 0

    # Request payload required parameters
    data = {}
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert isinstance(response.data.get("context_query")[0], drf_exceptions.ErrorDetail)
    assert response.data.get("context_query")[0].code == "required"
    assert isinstance(response.data.get("issuer")[0], drf_exceptions.ErrorDetail)
    assert response.data.get("issuer")[0].code == "required"
    assert models.CertificateRequest.objects.count() == 0
    assert count_certificates(defaults.CERTIFICATES_ROOT) == 0

    # Invalid issuer
    data = {
        "issuer": "marion.certificates.issuers.DumberCertificate",
        "context_query": json.dumps({"fullname": "Richie Cunningham"}),
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data.get("issuer")[0].code == "invalid_choice"
    assert models.CertificateRequest.objects.count() == 0
    assert count_certificates(defaults.CERTIFICATES_ROOT) == 0

    # Perform standard request
    data = {
        "issuer": "marion.certificates.issuers.DummyCertificate",
        "context_query": json.dumps({"fullname": "Richie Cunningham"}),
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert models.CertificateRequest.objects.count() == 1
    assert (
        models.CertificateRequest.objects.get().context.get("fullname")
        == "Richie Cunningham"
    )
    assert count_certificates(defaults.CERTIFICATES_ROOT) == 1


@pytest.mark.django_db
def test_certificate_request_viewset_post_context_query_json_schema_validation(
    monkeypatch,
):
    """Test the CertificateRequestViewSet create view context_query JSON schema
    validation.

    """

    monkeypatch.setattr(defaults, "CERTIFICATES_ROOT", Path(tempfile.mkdtemp()))

    url = reverse("certificaterequest-list")

    assert count_certificates(defaults.CERTIFICATES_ROOT) == 0

    # Refuse extra fields in context query
    data = {
        "issuer": "marion.certificates.issuers.DummyCertificate",
        "context_query": json.dumps({"fullname": "Richie Cunningham", "friends": 2}),
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert isinstance(response.data.get("context_query")[0], drf_exceptions.ErrorDetail)
    assert "Additional properties are not allowed ('friends' was unexpected)" in str(
        response.data.get("context_query")[0]
    )
    assert models.CertificateRequest.objects.count() == 0
    assert count_certificates(defaults.CERTIFICATES_ROOT) == 0

    # Input types checking
    data = {
        "issuer": "marion.certificates.issuers.DummyCertificate",
        "context_query": json.dumps({"fullname": 2}),
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert isinstance(response.data.get("context_query")[0], drf_exceptions.ErrorDetail)
    assert "2 is not of type 'string'" in str(response.data.get("context_query")[0])
    assert models.CertificateRequest.objects.count() == 0
    assert count_certificates(defaults.CERTIFICATES_ROOT) == 0

    # Input contraints checking (short fullname)
    data = {
        "issuer": "marion.certificates.issuers.DummyCertificate",
        "context_query": json.dumps({"fullname": "D"}),
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert isinstance(response.data.get("context_query")[0], drf_exceptions.ErrorDetail)
    assert "'D' is too short" in str(response.data.get("context_query")[0])
    assert models.CertificateRequest.objects.count() == 0
    assert count_certificates(defaults.CERTIFICATES_ROOT) == 0

    # Input contraints checking (too long fullname)
    data = {
        "issuer": "marion.certificates.issuers.DummyCertificate",
        "context_query": json.dumps({"fullname": "F" * 256}),
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert isinstance(response.data.get("context_query")[0], drf_exceptions.ErrorDetail)
    assert f"'{'F'*256}' is too long" in str(response.data.get("context_query")[0])
    assert models.CertificateRequest.objects.count() == 0
    assert count_certificates(defaults.CERTIFICATES_ROOT) == 0


@pytest.mark.django_db
def test_certificate_request_viewset_post_context_json_schema_validation(monkeypatch):
    """Test the CertificateRequestViewSet create view context JSON schema validation"""
    # pylint: disable=unused-argument,function-redefined

    monkeypatch.setattr(defaults, "CERTIFICATES_ROOT", Path(tempfile.mkdtemp()))

    url = reverse("certificaterequest-list")

    data = {
        "issuer": "marion.certificates.issuers.DummyCertificate",
        "context_query": json.dumps({"fullname": "Richie Cunningham"}),
    }

    # Refuse extra fields in context
    def mock_fetch_context(*args, **kwargs):
        """A mock that return invalid context"""
        return Context(
            {
                "fullname": "Richie Cunningham",
                "identifier": "0a1c3ccf-c67d-4071-ab1f-3b27628db9b1",
                "friends": 2,
            }
        )

    monkeypatch.setattr(DummyCertificate, "fetch_context", mock_fetch_context)
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "Certificate issuer context is not valid: "
        "Additional properties are not allowed ('friends' was unexpected)"
    ) in response.data.get("error")
    assert models.CertificateRequest.objects.count() == 0
    assert count_certificates(defaults.CERTIFICATES_ROOT) == 0

    # Types checking
    def mock_fetch_context(*args, **kwargs):
        """A mock that return invalid context"""
        return Context(
            {"fullname": 2, "identifier": "0a1c3ccf-c67d-4071-ab1f-3b27628db9b1"}
        )

    monkeypatch.setattr(DummyCertificate, "fetch_context", mock_fetch_context)
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "Certificate issuer context is not valid: 2 is not of type 'string'"
        in response.data.get("error")
    )
    assert models.CertificateRequest.objects.count() == 0
    assert count_certificates(defaults.CERTIFICATES_ROOT) == 0

    # Missing identifier
    def mock_fetch_context(*args, **kwargs):
        """A mock that return invalid context"""
        return Context({"fullname": "Richie Cunningham"})

    monkeypatch.setattr(DummyCertificate, "fetch_context", mock_fetch_context)
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "Certificate issuer context is not valid: 'identifier' is a required property"
        in response.data.get("error")
    )
    assert models.CertificateRequest.objects.count() == 0
    assert count_certificates(defaults.CERTIFICATES_ROOT) == 0

    # Constraints checking (short fullname)
    def mock_fetch_context(*args, **kwargs):
        """A mock that return invalid context"""
        return Context(
            {"fullname": "D", "identifier": "0a1c3ccf-c67d-4071-ab1f-3b27628db9b1"}
        )

    monkeypatch.setattr(DummyCertificate, "fetch_context", mock_fetch_context)
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "Certificate issuer context is not valid: 'D' is too short"
        in response.data.get("error")
    )
    assert models.CertificateRequest.objects.count() == 0
    assert count_certificates(defaults.CERTIFICATES_ROOT) == 0

    # Constraints checking (too long fullname)
    def mock_fetch_context(*args, **kwargs):
        """A mock that return invalid context"""
        return Context(
            {
                "fullname": "F" * 256,
                "identifier": "0a1c3ccf-c67d-4071-ab1f-3b27628db9b1",
            }
        )

    monkeypatch.setattr(DummyCertificate, "fetch_context", mock_fetch_context)
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        f"Certificate issuer context is not valid: '{'F'*256}' is too long"
        in response.data.get("error")
    )
    assert models.CertificateRequest.objects.count() == 0
    assert count_certificates(defaults.CERTIFICATES_ROOT) == 0


def test_certificate_template_debug_view_is_only_active_in_debug_mode(settings):
    """Test if the certificate_template_debug view is active when not in debug mode"""

    settings.DEBUG = False
    url = reverse("certificates-template-debug")

    response = client.get(url)
    assert response.status_code == 403


def test_certificate_template_debug_view(settings):
    """Test the certificate_template_debug view"""

    settings.DEBUG = True
    settings.MARION_CERTIFICATE_ISSUER_CHOICES_CLASS = (
        "marion.certificates.default.CertificateIssuerChoices"
    )
    url = reverse("certificates-template-debug")

    response = client.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert b"You should provide an issuer." in response.content

    response = client.get(url, {"issuer": "foo.bar.baz"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert b"Unknown issuer foo.bar.baz" in response.content

    response = client.get(
        url, {"issuer": "marion.certificates.issuers.DummyCertificate"}
    )
    assert response.status_code == 200
    # pylint: disable=no-member
    django_assertions.assertContains(response, "<h1>Dummy certificate</h1>")
