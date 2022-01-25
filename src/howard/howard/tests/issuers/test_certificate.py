"""Tests for the howard.issuers.certificate application views"""

import datetime
import re
import uuid

from howard.issuers.certificate import (
    CertificateDocument,
    ContextQueryModel,
    Course,
    Student,
)
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pdfminer.high_level import extract_text as pdf_extract_text


@given(
    st.builds(
        ContextQueryModel,
        student=st.builds(Student),
        course=st.builds(Course),
        creation_date=st.datetimes(),
    )
)
@settings(suppress_health_check=(HealthCheck.function_scoped_fixture,))
def test_certificate_fetch_context(monkeypatch, context_query):
    """Test Certificate fetch_context"""

    freezed_now = datetime.datetime(2021, 1, 1)
    monkeypatch.setattr("django.utils.timezone.now", lambda: freezed_now)

    identifier = uuid.uuid4()

    test_certificate = CertificateDocument(
        identifier=identifier,
        context_query=context_query,
    )
    expected = {
        "identifier": str(identifier),
        "delivery_stamp": freezed_now.isoformat(),
        **context_query.dict(),
    }
    context = test_certificate.fetch_context()
    assert context == expected


@given(
    st.builds(ContextQueryModel, student=st.builds(Student), course=st.builds(Course))
)
@settings(suppress_health_check=(HealthCheck.function_scoped_fixture,))
def test_certificate_default_creation_date(monkeypatch, context_query):
    """
    Context query `creation_date` property should be optional.
    If no value is provided, the document `created` metadata should be used.
    """

    freezed_now = datetime.datetime(2021, 1, 1)
    monkeypatch.setattr("django.utils.timezone.now", lambda: freezed_now)

    identifier = uuid.uuid4()

    test_certificate = CertificateDocument(
        identifier=identifier,
        context_query=context_query,
    )
    expected = {
        "identifier": str(identifier),
        "delivery_stamp": freezed_now.isoformat(),
        **context_query.dict(),
        "creation_date": freezed_now.isoformat(),
    }

    assert context_query.dict()["creation_date"] is None
    context = test_certificate.fetch_context()
    assert context == expected


@settings(max_examples=1, deadline=datetime.timedelta(seconds=1.5))
@given(
    st.builds(ContextQueryModel, student=st.builds(Student), course=st.builds(Course))
)
def test_certificate_should_render_without_error(context_query):
    """Test to render a certificate document"""
    certificate_document = CertificateDocument(context_query=context_query)
    certificate_document_path = certificate_document.create()

    with certificate_document_path.open("rb") as certificate_document_file:
        text_content = pdf_extract_text(certificate_document_file)
        assert re.search(".*CERTIFICATE.*", text_content)
