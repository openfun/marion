"""Realisation Certificate"""

import datetime
import random

from enum import Enum

from django.template import Context

from marion.certificates.issuers.base import AbstractCertificate

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
                { # student schema
                    "type": "object",
                    "properties": {
                        "gender": {"type": "string", "enum": ["Mme", "Mr"]},
                        "organization": {"$ref": "#/definitions/organization"},
                    },
                    "required": ["gender", "organization"]
                },
                { # manager schema
                    "type": "object",
                    "properties": {
                        "position": {"type": "string"},
                    },
                    "required": ["position"]
                }
            ]
        },
    }
}


class CertificateScope(Enum):
    """Allowed scopes for the RealisationCertificate"""

    FORMATION = "action de formation"
    BILAN = "bilan de compétences"
    VAE = "action de VAE"
    APPRENTISSAGE = "action de formation par apprentissage"


class RealisationCertificate(AbstractCertificate):
    """Official 'Certificat de réalisation des actions de formation'"""

    context_schema = {
        **JSON_SCHEMA_DEFINITIONS,
        "type": "object",
        "properties": {
            "identifier": {"type": "string", "format": "uuid"},
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
                                "enum": [
                                    scope.value for scope in list(CertificateScope)
                                ],
                            },
                            "manager": {"$ref": "#/definitions/person"},
                        },
                        "required": ["date", "duration", "manager", "scope"], # "scope"
                        "additionalProperties": False,
                    },
                    "organization": {"$ref": "#/definitions/organization"},
                },
                "required": ["name", "session", "organization"],
                "additionalProperties": False,
            },
            "student": {"$ref": "#/definitions/person"},
            "creation_date": {"type": "string", "format": "date"},
        },
        "required": ["identifier", "course", "student", "creation_date"],
        "additionalProperties": False,
    }

    context_query_schema = {
        **JSON_SCHEMA_DEFINITIONS,
        "type": "object",
        "properties": {
            "student": {"$ref": "#/definitions/person"},
            "course_organization": {"$ref": "#/definitions/organization"},
            "scope": {"const": "action de formation par apprentissage"},
        },
        "required": ["student", "course_organization", "scope"],
        # FIXME
        # "additionalProperties": False,
    }

    keywords = ["certificat", "réalisation", "formation"]
    title = "Certificat de réalisation des actions de formation"

    def fetch_context(self, **context_query):
        """Fetch the context that will be used to compile the certificate template."""

        self.validate_context_query(context_query)

        # course_id = context_query.get("course_id", None)
        student = context_query.get("student", None)
        course_organization = context_query.get("course_organization", None)
        scope = context_query.get("scope", None)
        # https://github.com/edx/edx-platform/blob/fb6786d90c2a2a6b000527d239b6cc61bf018af0/openedx/core/djangoapps/enrollments/api.py#L101
        # TODO; Make request

        # course_enrollment_endpoint = f"/enrollment/v1/enrollment/{username},{course_id}"
        enrollment = {
            "created": "2014-10-20T20:18:00Z",
            "mode": "honor",
            "is_active": True,
            "user": "Bob",
            "course_details": {
                "course_id": "edX/DemoX/2014T2",
                "course_name": "edX Demonstration Course",
                "enrollment_end": "2014-12-20T20:18:00Z",
                "enrollment_start": "2014-10-15T20:18:00Z",
                "course_start": "2015-02-03T00:00:00Z",
                "course_end": "2015-05-06T00:00:00Z",
                "course_modes": [
                    {
                        "slug": "honor",
                        "name": "Honor Code Certificate",
                        "min_price": 0,
                        "suggested_prices": "",
                        "currency": "usd",
                        "expiration_datetime": None,
                        "description": None,
                        "sku": None,
                        "bulk_sku": None,
                    }
                ],
                "invite_only": False,
            },
        }

        # course_detail_endpoint = f"/courses/v1/courses/{course_id}/"
        course = {
            "blocks_url": "/api/courses/v1/blocks/?course_id=edX%2Fexample%2F2012_Fall",
            "media": {
                "course_image": {
                    "uri": "/c4x/edX/example/asset/just_a_test.jpg",
                    "name": "Course Image",
                }
            },
            "description": "An example course.",
            "effort": 23,
            "end": "2015-09-19T18:00:00Z",
            "enrollment_end": "2015-07-15T00:00:00Z",
            "enrollment_start": "2015-06-15T00:00:00Z",
            "course_id": "edX/example/2012_Fall",
            "name": "Example Course",
            "number": "example",
            "org": "edX",
            "overview": "<p>A verbose description of the course.</p>",
            "start": "2015-07-17T12:00:00Z",
            "start_display": "July 17, 2015",
            "start_type": "timestamp",
            "pacing": "instructor",
        }

        course_manager = {
            "position": "CHRO",
            "last_name": "Riggs",
            "first_name": "Martin",
        }

        return Context(
            {
                "identifier": self.identifier,
                "course": {
                    "name": enrollment.get("course_details").get("course_name"),
                    "session": {
                        "date": {
                            "from": enrollment.get("course_details").get(
                                "course_start"
                            ),
                            "to": enrollment.get("course_details").get("course_end"),
                        },
                        "duration": course.get("effort"),
                        "manager": course_manager,
                        "scope": scope,
                    },
                    "organization": course_organization,
                },
                "student": student,
                "creation_date": self.created,
            }
        )
