"""Dummy Certificate"""

from uuid import UUID

from django.template import Context

from pydantic import BaseModel, constr

from .base import AbstractCertificate


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


class DummyCertificate(AbstractCertificate):
    """A test certificate for marion"""

    context_model = ContextModel

    context_query_model = ContextQueryModel

    keywords = ["dummy", "test", "certificate"]

    def fetch_context(self, **context_query):
        """Fetch the context that will be used to compile the certificate template.

        This method is required by the AbstractCertificate interface. The
        context query parameters should be sufficient to get template context.

        """

        validated = self.validate_context_query(context_query)
        return Context({"fullname": validated.fullname, "identifier": self.identifier})

    def get_title(self):
        """Define a custom title for the generated PDF metadata"""

        return f"Dummy certificate {self.identifier}"
