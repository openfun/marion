"""Tests for the howard.issuers.realisation application views"""

import uuid
from datetime import date, datetime

from django.template import Context

import pytest
from howard.issuers.realisation import (
    ArrowDate,
    CertificateScope,
    ContextModel,
    ContextQueryModel,
    Course,
    DateSpan,
    Gender,
    Manager,
    Organization,
    RealisationCertificate,
    Session,
    Student,
)
from pydantic.error_wrappers import ValidationError


@pytest.mark.parametrize(
    "kwargs",
    [
        {"start": ArrowDate("2021/01/01"), "end": ArrowDate("2021/12/31")},
        {"start": ArrowDate(1609459200), "end": ArrowDate(1640908800)},
        {"start": ArrowDate(date(2021, 1, 1)), "end": ArrowDate(date(2021, 12, 31))},
    ],
)
def test_datespan_model_with_valid_content(kwargs):
    """Tests a valid DateSpan model does not raise ValidationError."""

    try:
        DateSpan(**kwargs)
    except ValidationError:
        pytest.fail(f"Valid DateSpan model with {kwargs} should not raise exceptions.")


@pytest.mark.parametrize(
    "kwargs, error",
    [
        (
            {"start": None, "end": ArrowDate("31-12-2021")},
            "start\n  none is not an allowed value",
        ),
        (
            {"start": ArrowDate("31-12-2021"), "end": None},
            "end\n  none is not an allowed value",
        ),
        (
            {"start": "01-01-2021", "end": ArrowDate("31-12-2021")},
            "start\n  Invalid value",
        ),
        (
            {"start": ArrowDate("01-01-2021"), "end": "31-12-2021"},
            "end\n  Invalid value",
        ),
        ({"start": 1609459200, "end": ArrowDate(1640908800)}, "start\n  Invalid value"),
        ({"start": ArrowDate(1609459200), "end": 1640908800}, "end\n  Invalid value"),
        (
            {"start": date(2021, 1, 1), "end": ArrowDate(date(2021, 12, 31))},
            "start\n  Invalid value",
        ),
        (
            {"start": ArrowDate(date(2021, 1, 1)), "end": date(2021, 12, 31)},
            "end\n  Invalid value",
        ),
        (
            {"start": ArrowDate("foo"), "end": ArrowDate(date(2021, 12, 31))},
            "start\n  Could not match input 'foo'",
        ),
        (
            {"start": ArrowDate(date(2021, 1, 1)), "end": ArrowDate("foo")},
            "end\n  Could not match input 'foo'",
        ),
        (
            {"start": ArrowDate(True), "end": ArrowDate(date(2021, 1, 1))},
            "start\n  Cannot parse single argument of type <class 'bool'>.",
        ),
        (
            {"start": ArrowDate(date(2021, 1, 1)), "end": ArrowDate(True)},
            "end\n  Cannot parse single argument of type <class 'bool'>.",
        ),
        (
            {"end": ArrowDate("2021/12/31")},
            "start\n  field required",
        ),
        (
            {"start": ArrowDate("2021/01/01")},
            "end\n  field required",
        ),
    ],
)
def test_datespan_model_with_invalid_content(kwargs, error):
    """Tests a invalid DateSpan model raises a ValidationError."""

    with pytest.raises(ValidationError, match=error):
        DateSpan(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"first_name": "John", "last_name": "Doe", "position": "CEO"},
        {"first_name": "Jane", "last_name": "Doe", "position": "CTO"},
    ],
)
def test_manager_model_with_valid_content(kwargs):
    """Tests a valid Manager model does not raise ValidationError."""

    try:
        Manager(**kwargs)
    except ValidationError:
        pytest.fail(f"Valid Manager model with {kwargs} should not raise exceptions.")


@pytest.mark.parametrize(
    "kwargs, error",
    [
        (
            {"first_name": None, "last_name": "Doe", "position": "CEO"},
            "first_name\n  none is not an allowed value",
        ),
        (
            {"first_name": "Jane", "last_name": None, "position": "CEO"},
            "last_name\n  none is not an allowed value",
        ),
        (
            {"first_name": "Jane", "last_name": "Doe", "position": None},
            "position\n  none is not an allowed value",
        ),
        (
            {"last_name": "Doe", "position": "CEO"},
            "first_name\n  field required",
        ),
        (
            {"first_name": "Jane", "position": "CEO"},
            "last_name\n  field required",
        ),
        (
            {"first_name": "Jane", "last_name": "Doe"},
            "position\n  field required",
        ),
    ],
)
def test_manager_model_with_invalid_content(kwargs, error):
    """Tests a invalid Manager model raises a ValidationError."""

    with pytest.raises(ValidationError, match=error):
        Manager(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "name": "edx",
            "manager": {
                "position": "CEO",
                "last_name": "Agarwal",
                "first_name": "Anant",
            },
            "location": "Boston, MA",
        },
        {
            "name": "edx",
            "location": "Boston, MA",
        },
        {
            "name": "edx",
            "manager": {
                "position": "CEO",
                "last_name": "Agarwal",
                "first_name": "Anant",
            },
        },
    ],
)
def test_organization_model_with_valid_content(kwargs):
    """Tests a valid Organization model does not raise ValidationError."""

    try:
        Organization(**kwargs)
    except ValidationError:
        pytest.fail(
            f"Valid Organization model with {kwargs} should not raise exceptions."
        )


@pytest.mark.parametrize(
    "kwargs, error",
    [
        (
            {
                "name": None,
                "manager": {
                    "position": "CEO",
                    "last_name": "Agarwal",
                    "first_name": "Anant",
                },
                "location": "Boston, MA",
            },
            "name\n  none is not an allowed value",
        ),
        (
            {
                "name": "edx",
                "manager": "CEO, Agarwal Anant",
                "location": "Boston, MA",
            },
            "manager\n  value is not a valid dict",
        ),
        (
            {
                "manager": {
                    "position": "CEO",
                    "last_name": "Agarwal",
                    "first_name": "Anant",
                },
                "location": "Boston, MA",
            },
            "name\n  field required",
        ),
    ],
)
def test_organization_model_with_invalid_content(kwargs, error):
    """Tests a invalid Organization model raises a ValidationError."""

    with pytest.raises(ValidationError, match=error):
        Organization(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "first_name": "John",
            "last_name": "Doe",
            "gender": Gender.MALE,
            "organization": {
                "name": "ACME Inc.",
            },
        },
    ],
)
def test_student_model_with_valid_content(kwargs):
    """Tests a valid Student model does not raise ValidationError."""

    try:
        Student(**kwargs)
    except ValidationError:
        pytest.fail(f"Valid Student model with {kwargs} should not raise exceptions.")


@pytest.mark.parametrize(
    "kwargs, error",
    [
        (
            {"first_name": None, "last_name": "Doe", "gender": Gender.MALE},
            "first_name\n  none is not an allowed value",
        ),
        (
            {"first_name": "Jane", "last_name": None, "gender": Gender.FEMALE},
            "last_name\n  none is not an allowed value",
        ),
        (
            {"first_name": "Jane", "last_name": "Doe", "gender": None},
            "gender\n  none is not an allowed value",
        ),
        (
            {"first_name": "John", "last_name": "Doe", "gender": "monsieur"},
            "gender\n  value is not a valid enumeration member",
        ),
        (
            {"last_name": "Doe", "gender": Gender.MALE},
            "first_name\n  field required",
        ),
        (
            {"first_name": "Jane", "gender": Gender.FEMALE},
            "last_name\n  field required",
        ),
        (
            {"first_name": "Jane", "last_name": "Doe"},
            "gender\n  field required",
        ),
    ],
)
def test_student_model_with_invalid_content(kwargs, error):
    """Tests a invalid Student model raises a ValidationError."""

    with pytest.raises(ValidationError, match=error):
        Student(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "datespan": {
                "start": ArrowDate("2021/01/01"),
                "end": ArrowDate("2021/12/31"),
            },
            "duration": 23,
            "scope": CertificateScope.FORMATION,
            "manager": {
                "position": "CEO",
                "last_name": "Agarwal",
                "first_name": "Anant",
            },
        },
    ],
)
def test_session_model_with_valid_content(kwargs):
    """Tests a valid Session model does not raise ValidationError."""

    try:
        Session(**kwargs)
    except ValidationError:
        pytest.fail(f"Valid Session model with {kwargs} should not raise exceptions.")


@pytest.mark.parametrize(
    "kwargs, error",
    [
        (
            {
                "datespan": ArrowDate(date(2021, 1, 1)),
                "duration": 23,
                "scope": CertificateScope.FORMATION,
                "manager": {
                    "position": "CEO",
                    "last_name": "Agarwal",
                    "first_name": "Anant",
                },
            },
            "datespan\n  value is not a valid dict",
        ),
        (
            {
                "datespan": {
                    "start": ArrowDate("2021/01/01"),
                    "end": ArrowDate("2021/12/31"),
                },
                "duration": "23 days",
                "scope": CertificateScope.FORMATION,
                "manager": {
                    "position": "CEO",
                    "last_name": "Agarwal",
                    "first_name": "Anant",
                },
            },
            "duration\n  value is not a valid integer",
        ),
        (
            {
                "datespan": {
                    "start": ArrowDate("2021/01/01"),
                    "end": ArrowDate("2021/12/31"),
                },
                "duration": 23,
                "scope": "formation",
                "manager": {
                    "position": "CEO",
                    "last_name": "Agarwal",
                    "first_name": "Anant",
                },
            },
            "scope\n  value is not a valid enumeration member",
        ),
        (
            {
                "datespan": {
                    "start": ArrowDate("2021/01/01"),
                    "end": ArrowDate("2021/12/31"),
                },
                "duration": 23,
                "scope": CertificateScope.FORMATION,
                "manager": "CEO Agarwal Anant",
            },
            "manager\n  value is not a valid dict",
        ),
        (
            {
                "duration": 23,
                "scope": CertificateScope.FORMATION,
                "manager": {
                    "position": "CEO",
                    "last_name": "Agarwal",
                    "first_name": "Anant",
                },
            },
            "datespan\n  field required",
        ),
        (
            {
                "datespan": {
                    "start": ArrowDate("2021/01/01"),
                    "end": ArrowDate("2021/12/31"),
                },
                "scope": CertificateScope.FORMATION,
                "manager": {
                    "position": "CEO",
                    "last_name": "Agarwal",
                    "first_name": "Anant",
                },
            },
            "duration\n  field required",
        ),
        (
            {
                "datespan": {
                    "start": ArrowDate("2021/01/01"),
                    "end": ArrowDate("2021/12/31"),
                },
                "duration": 23,
                "manager": {
                    "position": "CEO",
                    "last_name": "Agarwal",
                    "first_name": "Anant",
                },
            },
            "scope\n  field required",
        ),
        (
            {
                "datespan": {
                    "start": ArrowDate("2021/01/01"),
                    "end": ArrowDate("2021/12/31"),
                },
                "duration": 23,
                "scope": CertificateScope.FORMATION,
            },
            "manager\n  field required",
        ),
    ],
)
def test_session_model_with_invalid_content(kwargs, error):
    """Tests a invalid Session model raises a ValidationError."""

    with pytest.raises(ValidationError, match=error):
        Session(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "name": "edX Demonstration Course",
            "session": {
                "datespan": {
                    "start": ArrowDate("2021/01/01"),
                    "end": ArrowDate("2021/12/31"),
                },
                "duration": 23,
                "scope": CertificateScope.FORMATION,
                "manager": {
                    "position": "CEO",
                    "last_name": "Agarwal",
                    "first_name": "Anant",
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
    ],
)
def test_course_model_with_valid_content(kwargs):
    """Tests a valid Course model does not raise ValidationError."""

    try:
        Course(**kwargs)
    except ValidationError:
        pytest.fail(f"Valid Course model with {kwargs} should not raise exceptions.")


@pytest.mark.parametrize(
    "kwargs, error",
    [
        (
            {
                "name": None,
                "session": {
                    "datespan": {
                        "start": ArrowDate("2021/01/01"),
                        "end": ArrowDate("2021/12/31"),
                    },
                    "duration": 23,
                    "scope": CertificateScope.FORMATION,
                    "manager": {
                        "position": "CEO",
                        "last_name": "Agarwal",
                        "first_name": "Anant",
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
            "name\n  none is not an allowed value",
        ),
        (
            {
                "name": "edX Demonstration Course",
                "session": None,
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
            "session\n  none is not an allowed value",
        ),
        (
            {
                "name": "edX Demonstration Course",
                "session": {
                    "datespan": {
                        "start": ArrowDate("2021/01/01"),
                        "end": ArrowDate("2021/12/31"),
                    },
                    "duration": 23,
                    "scope": CertificateScope.FORMATION,
                    "manager": {
                        "position": "CEO",
                        "last_name": "Agarwal",
                        "first_name": "Anant",
                    },
                },
                "organization": None,
            },
            "organization\n  none is not an allowed value",
        ),
        (
            {
                "name": "edX Demonstration Course",
                "session": "session 234",
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
            "session\n  value is not a valid dict",
        ),
        (
            {
                "name": "edX Demonstration Course",
                "session": {
                    "datespan": {
                        "start": ArrowDate("2021/01/01"),
                        "end": ArrowDate("2021/12/31"),
                    },
                    "duration": 23,
                    "scope": CertificateScope.FORMATION,
                    "manager": {
                        "position": "CEO",
                        "last_name": "Agarwal",
                        "first_name": "Anant",
                    },
                },
                "organization": "edx",
            },
            "organization\n  value is not a valid dict",
        ),
        (
            {
                "session": {
                    "datespan": {
                        "start": ArrowDate("2021/01/01"),
                        "end": ArrowDate("2021/12/31"),
                    },
                    "duration": 23,
                    "scope": CertificateScope.FORMATION,
                    "manager": {
                        "position": "CEO",
                        "last_name": "Agarwal",
                        "first_name": "Anant",
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
            "name\n  field required",
        ),
        (
            {
                "name": "edX Demonstration Course",
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
            "session\n  field required",
        ),
        (
            {
                "name": "edX Demonstration Course",
                "session": {
                    "datespan": {
                        "start": ArrowDate("2021/01/01"),
                        "end": ArrowDate("2021/12/31"),
                    },
                    "duration": 23,
                    "scope": CertificateScope.FORMATION,
                    "manager": {
                        "position": "CEO",
                        "last_name": "Agarwal",
                        "first_name": "Anant",
                    },
                },
            },
            "organization\n  field required",
        ),
    ],
)
def test_course_model_with_invalid_content(kwargs, error):
    """Tests a invalid Course model raises a ValidationError."""

    with pytest.raises(ValidationError, match=error):
        Course(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "identifier": "ab9fe733-5b4b-485c-b0c2-f28d920c8588",
            "course": {
                "name": "edX Demonstration Course",
                "session": {
                    "datespan": {
                        "start": ArrowDate("2021/01/01"),
                        "end": ArrowDate("2021/12/31"),
                    },
                    "duration": 23,
                    "scope": CertificateScope.FORMATION,
                    "manager": {
                        "position": "CEO",
                        "last_name": "Agarwal",
                        "first_name": "Anant",
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
                "first_name": "John",
                "last_name": "Doe",
                "gender": Gender.MALE,
                "organization": {
                    "name": "ACME Inc.",
                },
            },
            "creation_date": datetime(2021, 1, 1),
            "delivery_stamp": datetime(2021, 1, 1),
        },
    ],
)
def test_context_model_with_valid_content(kwargs):
    """Tests a valid Context model does not raise ValidationError."""

    try:
        ContextModel(**kwargs)
    except ValidationError:
        pytest.fail(f"Valid Context model with {kwargs} should not raise exceptions.")


@pytest.mark.parametrize(
    "kwargs, error",
    [
        (
            {
                "identifier": None,
                "course": {
                    "name": "edX Demonstration Course",
                    "session": {
                        "datespan": {
                            "start": ArrowDate("2021/01/01"),
                            "end": ArrowDate("2021/12/31"),
                        },
                        "duration": 23,
                        "scope": CertificateScope.FORMATION,
                        "manager": {
                            "position": "CEO",
                            "last_name": "Agarwal",
                            "first_name": "Anant",
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
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": Gender.MALE,
                    "organization": {
                        "name": "ACME Inc.",
                    },
                },
                "creation_date": datetime(2021, 1, 1),
                "delivery_stamp": datetime(2021, 1, 1),
            },
            "identifier\n  none is not an allowed value",
        ),
        (
            {
                "identifier": "ab9fe733-5b4b-485c-b0c2-f28d920c8588",
                "course": None,
                "student": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": Gender.MALE,
                    "organization": {
                        "name": "ACME Inc.",
                    },
                },
                "creation_date": datetime(2021, 1, 1),
                "delivery_stamp": datetime(2021, 1, 1),
            },
            "course\n  none is not an allowed value",
        ),
        (
            {
                "identifier": "ab9fe733-5b4b-485c-b0c2-f28d920c8588",
                "course": {
                    "name": "edX Demonstration Course",
                    "session": {
                        "datespan": {
                            "start": ArrowDate("2021/01/01"),
                            "end": ArrowDate("2021/12/31"),
                        },
                        "duration": 23,
                        "scope": CertificateScope.FORMATION,
                        "manager": {
                            "position": "CEO",
                            "last_name": "Agarwal",
                            "first_name": "Anant",
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
                "student": None,
                "creation_date": datetime(2021, 1, 1),
                "delivery_stamp": datetime(2021, 1, 1),
            },
            "student\n  none is not an allowed value",
        ),
        (
            {
                "identifier": "ab9fe733-5b4b-485c-b0c2-f28d920c8588",
                "course": {
                    "name": "edX Demonstration Course",
                    "session": {
                        "datespan": {
                            "start": ArrowDate("2021/01/01"),
                            "end": ArrowDate("2021/12/31"),
                        },
                        "duration": 23,
                        "scope": CertificateScope.FORMATION,
                        "manager": {
                            "position": "CEO",
                            "last_name": "Agarwal",
                            "first_name": "Anant",
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
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": Gender.MALE,
                    "organization": {
                        "name": "ACME Inc.",
                    },
                },
                "creation_date": None,
                "delivery_stamp": datetime(2021, 1, 1),
            },
            "creation_date\n  none is not an allowed value",
        ),
        (
            {
                "identifier": "ab9fe733-5b4b-485c-b0c2-f28d920c8588",
                "course": {
                    "name": "edX Demonstration Course",
                    "session": {
                        "datespan": {
                            "start": ArrowDate(date(2021, 1, 1)),
                            "end": ArrowDate(date(2021, 12, 31)),
                        },
                        "duration": 23,
                        "scope": CertificateScope.FORMATION,
                        "manager": {
                            "position": "CEO",
                            "last_name": "Agarwal",
                            "first_name": "Anant",
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
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": Gender.MALE,
                },
                "creation_date": datetime(2021, 1, 1),
                "delivery_stamp": None,
            },
            "delivery_stamp\n  none is not an allowed value",
        ),
        (
            {
                "identifier": "abcd1234",
                "course": {
                    "name": "edX Demonstration Course",
                    "session": {
                        "datespan": {
                            "start": ArrowDate("2021/01/01"),
                            "end": ArrowDate("2021/12/31"),
                        },
                        "duration": 23,
                        "scope": CertificateScope.FORMATION,
                        "manager": {
                            "position": "CEO",
                            "last_name": "Agarwal",
                            "first_name": "Anant",
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
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": Gender.MALE,
                    "organization": {
                        "name": "ACME Inc.",
                    },
                },
                "creation_date": datetime(2021, 1, 1),
                "delivery_stamp": datetime(2021, 1, 1),
            },
            "identifier\n  value is not a valid uuid",
        ),
        (
            {
                "identifier": "ab9fe733-5b4b-485c-b0c2-f28d920c8588",
                "course": "edX Demonstration Course",
                "student": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": Gender.MALE,
                    "organization": {
                        "name": "ACME Inc.",
                    },
                },
                "creation_date": datetime(2021, 1, 1),
                "delivery_stamp": datetime(2021, 1, 1),
            },
            "course\n  value is not a valid dict",
        ),
        (
            {
                "identifier": "ab9fe733-5b4b-485c-b0c2-f28d920c8588",
                "course": {
                    "name": "edX Demonstration Course",
                    "session": {
                        "datespan": {
                            "start": ArrowDate("2021/01/01"),
                            "end": ArrowDate("2021/12/31"),
                        },
                        "duration": 23,
                        "scope": CertificateScope.FORMATION,
                        "manager": {
                            "position": "CEO",
                            "last_name": "Agarwal",
                            "first_name": "Anant",
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
                "student": "John Doe",
                "creation_date": datetime(2021, 1, 1),
                "delivery_stamp": datetime(2021, 1, 1),
            },
            "student\n  value is not a valid dict",
        ),
        (
            {
                "identifier": "ab9fe733-5b4b-485c-b0c2-f28d920c8588",
                "course": {
                    "name": "edX Demonstration Course",
                    "session": {
                        "datespan": {
                            "start": ArrowDate("2021/01/01"),
                            "end": ArrowDate("2021/12/31"),
                        },
                        "duration": 23,
                        "scope": CertificateScope.FORMATION,
                        "manager": {
                            "position": "CEO",
                            "last_name": "Agarwal",
                            "first_name": "Anant",
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
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": Gender.MALE,
                    "organization": {
                        "name": "ACME Inc.",
                    },
                },
                "creation_date": "2021-01-01",
                "delivery_stamp": datetime(2021, 1, 1),
            },
            "creation_date\n  invalid datetime format",
        ),
        (
            {
                "identifier": "ab9fe733-5b4b-485c-b0c2-f28d920c8588",
                "course": {
                    "name": "edX Demonstration Course",
                    "session": {
                        "datespan": {
                            "start": ArrowDate(date(2021, 1, 1)),
                            "end": ArrowDate(date(2021, 12, 31)),
                        },
                        "duration": 23,
                        "scope": CertificateScope.FORMATION,
                        "manager": {
                            "position": "CEO",
                            "last_name": "Agarwal",
                            "first_name": "Anant",
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
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": Gender.MALE,
                },
                "creation_date": datetime(2021, 1, 1),
                "delivery_stamp": "2021-01-01",
            },
            "delivery_stamp\n  invalid datetime format",
        ),
        (
            {
                "course": {
                    "name": "edX Demonstration Course",
                    "session": {
                        "datespan": {
                            "start": ArrowDate("2021/01/01"),
                            "end": ArrowDate("2021/12/31"),
                        },
                        "duration": 23,
                        "scope": CertificateScope.FORMATION,
                        "manager": {
                            "position": "CEO",
                            "last_name": "Agarwal",
                            "first_name": "Anant",
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
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": Gender.MALE,
                    "organization": {
                        "name": "ACME Inc.",
                    },
                },
                "creation_date": datetime(2021, 1, 1),
                "delivery_stamp": datetime(2021, 1, 1),
            },
            "identifier\n  field required",
        ),
        (
            {
                "identifier": "ab9fe733-5b4b-485c-b0c2-f28d920c8588",
                "student": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": Gender.MALE,
                    "organization": {
                        "name": "ACME Inc.",
                    },
                },
                "creation_date": datetime(2021, 1, 1),
                "delivery_stamp": datetime(2021, 1, 1),
            },
            "course\n  field required",
        ),
        (
            {
                "identifier": "ab9fe733-5b4b-485c-b0c2-f28d920c8588",
                "course": {
                    "name": "edX Demonstration Course",
                    "session": {
                        "datespan": {
                            "start": ArrowDate("2021/01/01"),
                            "end": ArrowDate("2021/12/31"),
                        },
                        "duration": 23,
                        "scope": CertificateScope.FORMATION,
                        "manager": {
                            "position": "CEO",
                            "last_name": "Agarwal",
                            "first_name": "Anant",
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
                "creation_date": datetime(2021, 1, 1),
                "delivery_stamp": datetime(2021, 1, 1),
            },
            "student\n  field required",
        ),
        (
            {
                "identifier": "ab9fe733-5b4b-485c-b0c2-f28d920c8588",
                "course": {
                    "name": "edX Demonstration Course",
                    "session": {
                        "datespan": {
                            "start": ArrowDate("2021/01/01"),
                            "end": ArrowDate("2021/12/31"),
                        },
                        "duration": 23,
                        "scope": CertificateScope.FORMATION,
                        "manager": {
                            "position": "CEO",
                            "last_name": "Agarwal",
                            "first_name": "Anant",
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
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": Gender.MALE,
                    "organization": {
                        "name": "ACME Inc.",
                    },
                },
                "delivery_stamp": datetime(2021, 1, 1),
            },
            "creation_date\n  field required",
        ),
        (
            {
                "identifier": "ab9fe733-5b4b-485c-b0c2-f28d920c8588",
                "course": {
                    "name": "edX Demonstration Course",
                    "session": {
                        "datespan": {
                            "start": ArrowDate(date(2021, 1, 1)),
                            "end": ArrowDate(date(2021, 12, 31)),
                        },
                        "duration": 23,
                        "scope": CertificateScope.FORMATION,
                        "manager": {
                            "position": "CEO",
                            "last_name": "Agarwal",
                            "first_name": "Anant",
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
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": Gender.MALE,
                },
                "creation_date": datetime(2021, 1, 1),
            },
            "delivery_stamp\n  field required",
        ),
    ],
)
def test_context_model_with_invalid_content(kwargs, error):
    """Tests a invalid Context model raises a ValidationError."""

    with pytest.raises(ValidationError, match=error):
        ContextModel(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "student": {
                "first_name": "John",
                "last_name": "Doe",
                "gender": Gender.MALE,
                "organization": {
                    "name": "ACME Inc.",
                },
            },
            "course": {
                "name": "edX Demonstration Course",
                "session": {
                    "datespan": {
                        "start": ArrowDate(date(2021, 1, 1)),
                        "end": ArrowDate(date(2021, 12, 31)),
                    },
                    "duration": 23,
                    "scope": CertificateScope.FORMATION,
                    "manager": {
                        "position": "CEO",
                        "last_name": "Agarwal",
                        "first_name": "Anant",
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
        },
    ],
)
def test_context_query_model_with_valid_content(kwargs):
    """Tests a valid ContextQuery model does not raise ValidationError."""

    try:
        ContextQueryModel(**kwargs)
    except ValidationError:
        pytest.fail(
            f"Valid ContextQuery model with {kwargs} should not raise exceptions."
        )


@pytest.mark.parametrize(
    "kwargs, error",
    [
        (
            {
                "student": None,
                "course": {
                    "name": "edX Demonstration Course",
                    "session": {
                        "datespan": {
                            "start": ArrowDate(date(2021, 1, 1)),
                            "end": ArrowDate(date(2021, 12, 31)),
                        },
                        "duration": 23,
                        "scope": CertificateScope.FORMATION,
                        "manager": {
                            "position": "CEO",
                            "last_name": "Agarwal",
                            "first_name": "Anant",
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
            },
            "student\n  none is not an allowed value",
        ),
        (
            {
                "student": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": Gender.MALE,
                },
                "course": None,
            },
            "course\n  none is not an allowed value",
        ),
        (
            {
                "student": "John Doe",
                "course": {
                    "name": "edX Demonstration Course",
                    "session": {
                        "datespan": {
                            "start": ArrowDate(date(2021, 1, 1)),
                            "end": ArrowDate(date(2021, 12, 31)),
                        },
                        "duration": 23,
                        "scope": CertificateScope.FORMATION,
                        "manager": {
                            "position": "CEO",
                            "last_name": "Agarwal",
                            "first_name": "Anant",
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
            },
            "student\n  value is not a valid dict",
        ),
        (
            {
                "student": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": Gender.MALE,
                },
                "course": "edX Demonstration Course",
            },
            "course\n  value is not a valid dict",
        ),
        (
            {
                "course": {
                    "name": "edX Demonstration Course",
                    "session": {
                        "datespan": {
                            "start": ArrowDate(date(2021, 1, 1)),
                            "end": ArrowDate(date(2021, 12, 31)),
                        },
                        "duration": 23,
                        "scope": CertificateScope.FORMATION,
                        "manager": {
                            "position": "CEO",
                            "last_name": "Agarwal",
                            "first_name": "Anant",
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
            },
            "student\n  field required",
        ),
        (
            {
                "student": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "gender": Gender.MALE,
                },
            },
            "course\n  field required",
        ),
    ],
)
def test_context_query_model_with_invalid_content(kwargs, error):
    """Tests a invalid ContextQuery model raises a ValidationError."""

    with pytest.raises(ValidationError, match=error):
        ContextQueryModel(**kwargs)


def test_realisation_certificate_fetch_context(monkeypatch):
    """Test Realisation Certificate fetch_context"""

    class TestCertificate(RealisationCertificate):
        pass

    identifier = uuid.uuid4()
    test_certificate = TestCertificate(identifier=identifier)

    freezed_now = datetime(2021, 1, 1)
    monkeypatch.setattr("django.utils.timezone.now", lambda: freezed_now)

    datespan = DateSpan(
        start=ArrowDate(date(2015, 2, 3)),
        end=ArrowDate(date(2015, 5, 6)),
    )

    course_manager = Manager(
        position="CHRO",
        last_name="Riggs",
        first_name="Martin",
    )

    session = Session(
        datespan=datespan,
        scope=CertificateScope.APPRENTISSAGE,
        duration=23,
        manager=course_manager,
    )

    course_organization_manager = Manager(
        position="CEO",
        last_name="Agarwal",
        first_name="Anant",
    )

    course_organization = Organization(
        name="edx",
        manager=course_organization_manager,
        location="Boston, MA",
    )

    course = Course(
        name="edX Demonstration Course",
        session=session,
        organization=course_organization,
    )

    student_organization = Organization(name="ACME inc.")

    student = Student(
        gender=Gender.FEMALE,
        first_name="Jane",
        last_name="Doe",
        organization=student_organization,
    )

    expected = Context(
        {
            "identifier": str(identifier),
            "course": course,
            "student": student,
            "creation_date": freezed_now,
            "delivery_stamp": freezed_now.isoformat(),
        }
    )

    context = test_certificate.fetch_context(
        course={
            "name": "edX Demonstration Course",
            "session": {
                "datespan": {
                    "start": ArrowDate(date(2015, 2, 3)),
                    "end": ArrowDate(date(2015, 5, 6)),
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
        student={
            "gender": "Mme",
            "first_name": "Jane",
            "last_name": "Doe",
            "organization": {"name": "ACME inc."},
        },
    )

    assert context == expected
