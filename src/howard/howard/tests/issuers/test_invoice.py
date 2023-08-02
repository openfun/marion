"""Tests for the howard.issuers.invoice application views"""

import re
import uuid
from datetime import timedelta

from django.utils import timezone

from howard.issuers.invoice import (
    Amount,
    ContextQueryModel,
    InvoiceDocument,
    Metadata,
    Order,
)
from hypothesis import given, settings
from hypothesis import strategies as st
from pdfminer.high_level import extract_text as pdf_extract_text


@given(
    st.builds(
        ContextQueryModel,
        order=st.builds(
            Order,
            amount=st.builds(
                Amount,
                total=st.decimals(allow_nan=False, allow_infinity=False),
                subtotal=st.decimals(allow_nan=False, allow_infinity=False),
                vat=st.decimals(allow_nan=False, allow_infinity=False),
                vat_amount=st.decimals(allow_nan=False, allow_infinity=False),
            ),
        ),
    )
)
def test_invoice_fetch_context(context_query):
    """Test Invoice fetch_context"""

    context_query.metadata.reference = (
        f"{timezone.now().strftime('%Y%m%d%H%M%S')}-"
        f"{str(uuid.uuid4()).split('-')[0]}"
    )
    expected = context_query.model_dump()

    test_invoice = InvoiceDocument(context_query=context_query)
    context = test_invoice.fetch_context()
    assert context == expected


@settings(max_examples=1, deadline=timedelta(seconds=1.5))
@given(
    st.builds(
        ContextQueryModel,
        metadata=st.builds(
            Metadata,
            type=st.just("credit_note"),
        ),
        order=st.builds(
            Order,
            amount=st.builds(
                Amount,
                total=st.decimals(allow_nan=False, allow_infinity=False),
                subtotal=st.decimals(allow_nan=False, allow_infinity=False),
                vat=st.decimals(allow_nan=False, allow_infinity=False),
                vat_amount=st.decimals(allow_nan=False, allow_infinity=False),
            ),
        ),
    )
)
def test_invoice_type_credit_note(context_query):
    """Test Invoice with type set to credit_note"""
    invoice_document = InvoiceDocument(context_query=context_query)
    invoice_document_path = invoice_document.create()

    with invoice_document_path.open("rb") as invoice_document_file:
        text_content = pdf_extract_text(invoice_document_file)
        assert re.search(".*CREDIT NOTE.*", text_content)
        assert re.search(".*Refunded by.*", text_content)
        assert re.search(".*Refunded to.*", text_content)
        assert re.search(".*Credit note information.*", text_content)


@settings(max_examples=1, deadline=timedelta(seconds=1.5))
@given(
    st.builds(
        ContextQueryModel,
        metadata=st.builds(
            Metadata,
            type=st.just("invoice"),
        ),
        order=st.builds(
            Order,
            amount=st.builds(
                Amount,
                total=st.decimals(allow_nan=False, allow_infinity=False),
                subtotal=st.decimals(allow_nan=False, allow_infinity=False),
                vat=st.decimals(allow_nan=False, allow_infinity=False),
                vat_amount=st.decimals(allow_nan=False, allow_infinity=False),
            ),
        ),
    )
)
def test_invoice_type_invoice(context_query):
    """Test Invoice with type set to invoice"""

    invoice_document = InvoiceDocument(context_query=context_query)
    invoice_document_path = invoice_document.create()

    with invoice_document_path.open("rb") as invoice_document_file:
        text_content = pdf_extract_text(invoice_document_file)
        assert re.search(".*Invoice.*", text_content)
        assert re.search(".*Sold by.*", text_content)
        assert re.search(".*Billed to.*", text_content)
        assert re.search(".*Invoice information.*", text_content)
