"""Dummy Certificate"""

from django.template import Context

from .base import AbstractCertificate


class DummyCertificate(AbstractCertificate):
    """A test certificate for marion"""

    context_schema = {
        "type": "object",
        "properties": {
            "identifier": {"type": "string", "format": "uuid"},
            "fullname": {"type": "string", "minLength": 2, "maxLength": 255},
        },
        "required": ["identifier", "fullname"],
        "additionalProperties": False,
    }

    context_query_schema = {
        "type": "object",
        "properties": {
            "fullname": {"type": "string", "minLength": 2, "maxLength": 255},
        },
        "required": ["fullname"],
        "additionalProperties": False,
    }

    keywords = ["dummy", "test", "certificate"]

    def fetch_context(self, **context_query):
        """Fetch the context that will be used to compile the certificate template.

        This method is required by the AbstractCertificate interface. The
        context query parameters should be sufficient to get template context.

        """

        self.validate_context_query(context_query)
        fullname = context_query.get("fullname", None)
        return Context({"fullname": fullname, "identifier": self.identifier})

    def get_title(self):
        """Define a custom title for the generated PDF metadata"""

        return f"Dummy certificate {self.identifier}"
