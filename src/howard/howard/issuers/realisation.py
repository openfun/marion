"""Realisation Certificate"""

from enum import Enum

from django.template import Context

from dateutil import parser

from marion.certificates.issuers.base import AbstractCertificate


class CertificateScope(Enum):
    """Allowed scopes for the RealisationCertificate"""

    FORMATION = "action de formation"
    BILAN = "bilan de compétences"
    VAE = "action de VAE"
    APPRENTISSAGE = "action de formation par apprentissage"


JSON_SCHEMA_DEFINITIONS = {
    "definitions": {
        "organization": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "manager": {"$ref": "#/definitions/person"},
                "location": {"type": "string"},
            },
            "required": ["name"],
        },
        "person": {
            "type": "object",
            "properties": {
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
            },
            "required": ["first_name", "last_name"],
            "oneOf": [
                {  # student schema
                    "type": "object",
                    "properties": {
                        "gender": {"type": "string", "enum": ["Mme", "Mr"]},
                        "organization": {"$ref": "#/definitions/organization"},
                    },
                    "required": ["gender", "organization"],
                },
                {  # manager schema
                    "type": "object",
                    "properties": {
                        "position": {"type": "string"},
                    },
                    "required": ["position"],
                },
            ],
        },
        "course": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "session": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "object",
                            "properties": {
                                "from": {"type": "string", "format": "date"},
                                "to": {"type": "string", "format": "date"},
                            },
                        },
                        "duration": {"type": "integer"},
                        "scope": {
                            "type": "string",
                            "enum": [scope.value for scope in list(CertificateScope)],
                        },
                        "manager": {"$ref": "#/definitions/person"},
                    },
                    "required": ["date", "duration", "manager", "scope"],
                    "additionalProperties": False,
                },
                "organization": {"$ref": "#/definitions/organization"},
            },
            "required": ["name", "session", "organization"],
        },
    }
}


class RealisationCertificate(AbstractCertificate):
    """Official 'Certificat de réalisation des actions de formation'"""

    context_schema = {
        **JSON_SCHEMA_DEFINITIONS,
        "type": "object",
        "properties": {
            "identifier": {"type": "string", "format": "uuid"},
            "student": {"$ref": "#/definitions/person"},
            "course": {"$ref": "#/definitions/course"},
            "creation_date": {"type": "string", "format": "date"},
            "delivery_stamp": {"type": "string", "format": "date"},
        },
        "required": [
            "identifier",
            "course",
            "student",
            "creation_date",
            "delivery_stamp",
        ],
        "additionalProperties": False,
    }

    context_query_schema = {
        **JSON_SCHEMA_DEFINITIONS,
        "type": "object",
        "properties": {
            "student": {"$ref": "#/definitions/person"},
            "course": {"$ref": "#/definitions/course"},
        },
        "required": ["course", "student"],
        "additionalProperties": False,
    }

    keywords = ["certificat", "réalisation", "formation"]
    title = "Certificat de réalisation des actions de formation"

    def fetch_context(self, **context_query):
        """Fetch the context that will be used to compile the certificate template."""

        short_date_format = "%d/%m/%Y"

        self.validate_context_query(context_query)

        return Context(
            {
                "identifier": self.identifier,
                "course": context_query.get("course", None),
                "student": context_query.get("student", None),
                "creation_date": parser.isoparse(self.created).strftime(
                    short_date_format
                ),
                "delivery_stamp": self.created,
            }
        )
