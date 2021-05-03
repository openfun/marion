""""Invoice issuer"""

import decimal
from pathlib import Path

from pydantic import BaseModel, constr

from marion.issuers.base import AbstractDocument


class Customer(BaseModel):
    """Customer pydantic model"""

    name: str
    address: str


class Product(BaseModel):
    """Product pydantic model"""

    name: str
    description: str


class Price(BaseModel):
    """Price pydantic model"""

    total: decimal.Decimal
    subtotal: decimal.Decimal
    vat_amount: decimal.Decimal
    vat: decimal.Decimal
    currency: str


class Order(BaseModel):
    """Order pydantic model"""

    invoice_id: constr(regex=r"^[0-9]{14}-[a-zA-Z0-9]{8}$")  # noqa: F722
    customer: Customer
    product: Product
    price: Price
    company: str


class ContextModel(BaseModel):
    """Context pydantic model"""

    order: Order


class ContextQueryModel(BaseModel):
    """Context query pydantic model"""

    order: Order


class InvoiceDocument(AbstractDocument):
    """Invoice issuer"""

    keywords = ["invoice"]

    context_model = ContextModel
    context_query_model = ContextQueryModel

    css_template_path = Path("howard/invoice.css")
    html_template_path = Path("howard/invoice.html")

    def fetch_context(self) -> dict:
        """Invoice context"""
        return self.context_query.dict()

    def get_title(self):
        """Generate a PDF title that depends on the context"""
        return f"Invoice ref. {self.context.order.invoice_id}"
