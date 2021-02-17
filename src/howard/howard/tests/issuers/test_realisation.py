"""Tests for the howard.issuers.realisation application views"""

import uuid
from datetime import datetime

from django.template import Context

from howard.issuers import RealisationCertificate


def test_realisation_certificate_fetch_context(monkeypatch):
    """Test Realisation Certificate fetch_context"""

    class TestCertificate(RealisationCertificate):
        pass
    
    identifier = uuid.uuid4()
    test_certificate = TestCertificate(identifier=identifier)

    freezed_now = datetime(2021, 1, 1, 0, 0, 0)
    monkeypatch.setattr('django.utils.timezone.now', lambda: freezed_now)

    test_context = Context(
        {
            "identifier": str(identifier),
            "course": {
                "name": "edX Demonstration Course",
                "session": {
                    "date": {
                        "from": "2015-02-03T00:00:00Z", 
                        "to": "2015-05-06T00:00:00Z",                      
                    },
                    "scope": "action de formation par apprentissage",
                    "duration": 23,
                    "manager": {
                        "position": "CHRO",
                        "last_name": "Riggs",
                        "first_name": "Martin",
                    },
                },
                "organization": {
                    "name": "edx",
                    "manager": {
                        "position": "CEO",
                        "last_name": "Agarwal",
                        "first_name": "Anant",
                    },
                    "location": "Boston, MA",
                },
            },
            "student": {
                "gender": "Mme", 
                "first_name": "Jane", 
                "last_name": "Doe", 
                "organization": {"name": "ACME inc."},
            },
            "creation_date": freezed_now.isoformat(), 
        }
    )
    
    context = test_certificate.fetch_context(
        student = {
            "first_name": "Jane", 
            "last_name": "Doe", 
            "gender":"Mme", 
            "organization": {"name": "ACME inc."}
        }, 
        course_organization = {
            "name": "edx",
            "manager": {
                "position": "CEO",
                "last_name": "Agarwal",
                "first_name": "Anant",
            },
            "location": "Boston, MA",
        },
        scope = "action de formation par apprentissage"
    )

    assert context == test_context