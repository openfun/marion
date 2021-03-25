"""Dummy Document"""

from uuid import UUID

from pydantic import BaseModel, constr

from .base import AbstractDocument


class ContextModel(BaseModel):
    """Context model definition"""

    identifier: UUID
    fullname: constr(min_length=2, max_length=255)

    class Config:
        """Context model configuration"""

        extra = "forbid"


class ContextQueryModel(BaseModel):
    """ContextQuery model definition"""

    fullname: constr(min_length=2, max_length=255)

    class Config:
        """ContextQuery model configuration"""

        extra = "forbid"


class DummyDocument(AbstractDocument):
    """A test document for marion"""

    context_model = ContextModel

    context_query_model = ContextQueryModel

    keywords = ["dummy", "test", "document"]

    def fetch_context(self) -> dict:
        """Fetch the context that will be used to compile the document template.

        This method is required by the AbstractDocument interface. The
        context query parameters should be sufficient to get template context.

        """

        return {"fullname": self.context_query.fullname, "identifier": self.identifier}

    def get_title(self):
        """Define a custom title for the generated PDF metadata"""

        return f"Dummy document {self.identifier}"
