""""Invoice issuer"""

import datetime
import decimal
from pathlib import Path

from pydantic import BaseModel

from marion.issuers.base import AbstractDocument

from ..utils import StrEnum


class Type(StrEnum):
    """Type definition"""

    INVOICE = "invoice"
    CREDIT_NOTE = "credit_note"


class Customer(BaseModel):
    """Customer pydantic model"""

    name: str
    address: str


class Seller(BaseModel):
    """Seller pydantic model"""

    address: str


class Product(BaseModel):
    """Product pydantic model"""

    name: str
    description: str


class Amount(BaseModel):
    """Amount pydantic model"""

    total: decimal.Decimal
    subtotal: decimal.Decimal
    vat_amount: decimal.Decimal
    vat: decimal.Decimal
    currency: str


class Order(BaseModel):
    """Order pydantic model"""

    customer: Customer
    company: str
    product: Product
    amount: Amount
    seller: Seller


class Metadata(BaseModel):
    """Metadata pydantic model"""

    reference: str
    issued_on: datetime.datetime
    type: Type


class ContextModel(BaseModel):
    """Context pydantic model"""

    metadata: Metadata
    order: Order


class ContextQueryModel(BaseModel):
    """Context query pydantic model"""

    metadata: Metadata
    order: Order


class InvoiceDocument(AbstractDocument):
    """
    Invoicing Document
    to act debit (Invoice) or credit (Credit note) transaction.
    """

    keywords = ["invoice", "credit_note"]

    context_model = ContextModel
    context_query_model = ContextQueryModel

    css_template_path = Path("howard/invoice.css")
    html_template_path = Path("howard/invoice.html")

    def fetch_context(self) -> dict:
        """Invoice context"""
        return self.context_query.dict()

    def get_title(self) -> str:
        """Generate a PDF title that depends on the context"""
        return f"{self.context.metadata.type}-{self.context.metadata.reference}"
