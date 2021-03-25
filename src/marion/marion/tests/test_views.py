"""Tests for the marion application views"""

import json
import tempfile
from pathlib import Path

from django.urls import reverse

import pytest
from pytest_django import asserts as django_assertions
from rest_framework import exceptions as drf_exceptions
from rest_framework import status
from rest_framework.test import APIClient

from marion import defaults, models
from marion.issuers import DummyDocument

client = APIClient()


def count_documents(root):
    """Return the number of generated PDF files in the root directory"""

    return len(list(root.glob("*.pdf")))


@pytest.mark.django_db
def test_document_request_viewset_post(monkeypatch):
    """Test the DocumentRequestViewSet create view"""

    monkeypatch.setattr(defaults, "DOCUMENTS_ROOT", Path(tempfile.mkdtemp()))

    url = reverse("documentrequest-list")

    assert count_documents(defaults.DOCUMENTS_ROOT) == 0

    # Request payload required parameters
    data = {}
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert isinstance(response.data.get("context_query")[0], drf_exceptions.ErrorDetail)
    assert response.data.get("context_query")[0].code == "required"
    assert isinstance(response.data.get("issuer")[0], drf_exceptions.ErrorDetail)
    assert response.data.get("issuer")[0].code == "required"
    assert models.DocumentRequest.objects.count() == 0
    assert count_documents(defaults.DOCUMENTS_ROOT) == 0

    # Invalid issuer
    data = {
        "issuer": "marion.issuers.DumberDocument",
        "context_query": json.dumps({"fullname": "Richie Cunningham"}),
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data.get("issuer")[0].code == "invalid_choice"
    assert models.DocumentRequest.objects.count() == 0
    assert count_documents(defaults.DOCUMENTS_ROOT) == 0

    # Perform standard request
    data = {
        "issuer": "marion.issuers.DummyDocument",
        "context_query": json.dumps({"fullname": "Richie Cunningham"}),
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert models.DocumentRequest.objects.count() == 1
    assert (
        models.DocumentRequest.objects.get().context.get("fullname")
        == "Richie Cunningham"
    )
    assert count_documents(defaults.DOCUMENTS_ROOT) == 1


@pytest.mark.django_db
def test_document_request_viewset_post_context_query_pydantic_model_validation(
    monkeypatch,
):
    """Test the DocumentRequestViewSet create view context_query pydantic model
    validation.

    """

    monkeypatch.setattr(defaults, "DOCUMENTS_ROOT", Path(tempfile.mkdtemp()))

    url = reverse("documentrequest-list")

    assert count_documents(defaults.DOCUMENTS_ROOT) == 0

    # Refuse extra fields in context query
    data = {
        "issuer": "marion.issuers.DummyDocument",
        "context_query": json.dumps({"fullname": "Richie Cunningham", "friends": 2}),
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "extra fields not permitted" in str(response.data.get("error"))
    assert models.DocumentRequest.objects.count() == 0
    assert count_documents(defaults.DOCUMENTS_ROOT) == 0

    # Input types checking
    data = {
        "issuer": "marion.issuers.DummyDocument",
        "context_query": json.dumps({"fullname": None}),
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "none is not an allowed value" in str(response.data.get("error"))
    assert models.DocumentRequest.objects.count() == 0
    assert count_documents(defaults.DOCUMENTS_ROOT) == 0

    # Input contraints checking (short fullname)
    data = {
        "issuer": "marion.issuers.DummyDocument",
        "context_query": json.dumps({"fullname": "D"}),
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "ensure this value has at least 2 characters" in str(
        response.data.get("error")
    )
    assert models.DocumentRequest.objects.count() == 0
    assert count_documents(defaults.DOCUMENTS_ROOT) == 0

    # Input contraints checking (too long fullname)
    data = {
        "issuer": "marion.issuers.DummyDocument",
        "context_query": json.dumps({"fullname": "F" * 256}),
    }
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "ensure this value has at most 255 characters" in str(
        response.data.get("error")
    )
    assert models.DocumentRequest.objects.count() == 0
    assert count_documents(defaults.DOCUMENTS_ROOT) == 0


@pytest.mark.django_db
def test_document_request_viewset_post_context_pydantic_model_validation(
    monkeypatch,
):
    """Test the DocumentRequestViewSet create view context pydantic model
    validation.

    """
    # pylint: disable=unused-argument,function-redefined

    monkeypatch.setattr(defaults, "DOCUMENTS_ROOT", Path(tempfile.mkdtemp()))

    url = reverse("documentrequest-list")

    data = {
        "issuer": "marion.issuers.DummyDocument",
        "context_query": json.dumps({"fullname": "Richie Cunningham"}),
    }

    # Refuse extra fields in context
    def mock_fetch_context(*args, **kwargs):
        """A mock that returns invalid context"""
        return {
            "fullname": "Richie Cunningham",
            "identifier": "0a1c3ccf-c67d-4071-ab1f-3b27628db9b1",
            "friends": 2,
        }

    monkeypatch.setattr(DummyDocument, "fetch_context", mock_fetch_context)
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "extra fields not permitted" in response.data.get("error")
    assert models.DocumentRequest.objects.count() == 0
    assert count_documents(defaults.DOCUMENTS_ROOT) == 0

    # Types checking
    def mock_fetch_context(*args, **kwargs):
        """A mock that returns invalid context"""
        return {"fullname": None, "identifier": "0a1c3ccf-c67d-4071-ab1f-3b27628db9b1"}

    monkeypatch.setattr(DummyDocument, "fetch_context", mock_fetch_context)
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "none is not an allowed value" in response.data.get("error")
    assert models.DocumentRequest.objects.count() == 0
    assert count_documents(defaults.DOCUMENTS_ROOT) == 0

    # Missing identifier
    def mock_fetch_context(*args, **kwargs):
        """A mock that returns invalid context"""
        return {"fullname": "Richie Cunningham"}

    monkeypatch.setattr(DummyDocument, "fetch_context", mock_fetch_context)
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "identifier\n  field required" in response.data.get("error")
    assert models.DocumentRequest.objects.count() == 0
    assert count_documents(defaults.DOCUMENTS_ROOT) == 0

    # Constraints checking (short fullname)
    def mock_fetch_context(*args, **kwargs):
        """A mock that returns invalid context"""
        return {"fullname": "D", "identifier": "0a1c3ccf-c67d-4071-ab1f-3b27628db9b1"}

    monkeypatch.setattr(DummyDocument, "fetch_context", mock_fetch_context)
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "ensure this value has at least 2 characters" in response.data.get("error")
    assert models.DocumentRequest.objects.count() == 0
    assert count_documents(defaults.DOCUMENTS_ROOT) == 0

    # Constraints checking (too long fullname)
    def mock_fetch_context(*args, **kwargs):
        """A mock that returns invalid context"""
        return {
            "fullname": "F" * 256,
            "identifier": "0a1c3ccf-c67d-4071-ab1f-3b27628db9b1",
        }

    monkeypatch.setattr(DummyDocument, "fetch_context", mock_fetch_context)
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "ensure this value has at most 255 characters" in response.data.get("error")
    assert models.DocumentRequest.objects.count() == 0
    assert count_documents(defaults.DOCUMENTS_ROOT) == 0


def test_document_template_debug_view_is_only_active_in_debug_mode(settings):
    """Test if the document_template_debug view is active when not in debug mode"""

    settings.DEBUG = False
    url = reverse("documents-template-debug")

    response = client.get(url)
    assert response.status_code == 403


def test_document_template_debug_view(settings):
    """Test the document_template_debug view"""

    settings.DEBUG = True
    settings.MARION_DOCUMENT_ISSUER_CHOICES_CLASS = (
        "marion.default.DocumentIssuerChoices"
    )
    url = reverse("documents-template-debug")

    response = client.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert b"You should provide an issuer." in response.content

    response = client.get(url, {"issuer": "foo.bar.baz"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert b"Unknown issuer foo.bar.baz" in response.content

    response = client.get(url, {"issuer": "marion.issuers.DummyDocument"})
    assert response.status_code == 200
    # pylint: disable=no-member
    django_assertions.assertContains(response, "<h1>Dummy document</h1>")
