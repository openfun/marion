"""Tests for the howard.issuers.invoice application views"""

import uuid

from django.utils import timezone

from howard.issuers.invoice import ContextQueryModel, InvoiceDocument, Order
from hypothesis import given
from hypothesis import strategies as st


@given(st.builds(ContextQueryModel, order=st.builds(Order)))
def test_invoice_fetch_context(context_query):
    """Test Invoice fetch_context"""

    context_query.order.invoice_id = (
        f"{timezone.now().strftime('%Y%m%d%H%M%S')}-"
        f"{str(uuid.uuid4()).split('-')[0]}"
    )
    expected = context_query.dict()

    test_invoice = InvoiceDocument(context_query=context_query)
    context = test_invoice.fetch_context()

    assert context == expected
