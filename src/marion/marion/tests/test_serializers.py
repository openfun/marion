"""Tests for the marion application serializers"""

from django.urls import reverse

import pytest
from rest_framework.test import APIRequestFactory

from marion import factories, serializers


@pytest.mark.django_db
def test_document_request_serializer_document_url_field():
    """Test the document request serializer document_url field"""

    document_request = factories.DocumentRequestFactory(
        issuer="marion.issuers.DummyDocument",
        context_query={"fullname": "Richie Cunningham"},
    )

    factory = APIRequestFactory()
    request = factory.get(reverse("documentrequest-list"))

    serialized_document_request = serializers.DocumentRequestSerializer(
        document_request, context={"request": request}
    )

    assert (
        serialized_document_request.data.get("document_url")
        == f"http://testserver/media/{document_request.document_id}.pdf"
    )
