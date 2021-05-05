"""Tests for the howard.issuers.invoice application views"""

import decimal

from howard.issuers.invoice import InvoiceDocument


def test_invoice_fetch_context():
    """Test Invoice fetch_context"""

    order = {
        "order": {
            "invoice_id": "20210228-7665t6",
            "customer": {
                "name": "John Doe",
                "address": """
                    11 rue Stine
                    75012 Paris
                    FRANCE""",
            },
            "product": {
                "name": "Product botany course",
                "description": "Master botany basics",
            },
            "price": {
                "subtotal": decimal.Decimal(59.1000),
                "total": decimal.Decimal(70.80),
                "vat_amount": decimal.Decimal(11.8),
                "vat": decimal.Decimal(20),
                "currency": "&euro;",
            },
            "company": """
                Life Sciences Training Center,
                2 rue Barbe, 75001 Paris
                RCS Paris XXX XXX XXX - SIRET XXX XXX XXX XXXXX - APE XXXXX
                VAT number XXXXXXXXX""",
        }
    }
    expected = order.copy()
    expected["order"]["price"]["subtotal"] = "59.10"
    expected["order"]["price"]["total"] = "70.80"
    expected["order"]["price"]["vat_amount"] = "11.80"
    test_invoice = InvoiceDocument(context_query=order)
    context = test_invoice.fetch_context()
    assert context == expected
