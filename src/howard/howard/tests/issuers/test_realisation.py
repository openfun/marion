"""Tests for the howard.issuers.realisation application views"""

import datetime
import uuid

import pytest
from howard.issuers.realisation import (
    ArrowDate,
    ContextQueryModel,
    CourseRun,
    RealisationCertificate,
)
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pydantic import BaseModel, ValidationError


@pytest.mark.parametrize(
    "input_date",
    [
        "2021/03/24",
        "2021-03-24",
        "20210324",
        1616598447,
        datetime.date(2021, 3, 24),
        datetime.datetime(2021, 3, 24, 12, 12),
    ],
)
def test_arrowdate_field_with_valid_dates(input_date):
    """Test ArrowDate field supported types thanks to the arrow library"""

    class Foo(BaseModel):
        """Test pydantic model"""

        date: ArrowDate

    assert Foo(date=input_date).date == datetime.date(2021, 3, 24)


@pytest.mark.parametrize(
    "input_date",
    [None, "24/03/2021", "24-03-2021", "random string", {}, []],
)
def test_arrowdate_field_with_invalid_dates(input_date):
    """Test ArrowDate field supported types thanks to the arrow library"""

    class Foo(BaseModel):
        """Test pydantic model"""

        date: ArrowDate

    with pytest.raises(ValidationError):
        Foo(date=input_date)


@given(
    st.builds(
        ContextQueryModel,
        course_run=st.builds(CourseRun, start=st.dates(), end=st.dates()),
    )
)
@settings(suppress_health_check=(HealthCheck.function_scoped_fixture,))
def test_realisation_certificate_fetch_context(monkeypatch, context_query):
    """Test Realisation Certificate fetch_context"""

    freezed_now = datetime.datetime(2021, 1, 1)
    monkeypatch.setattr("django.utils.timezone.now", lambda: freezed_now)

    identifier = uuid.uuid4()
    test_certificate = RealisationCertificate(
        identifier=identifier, context_query=context_query
    )

    expected = {
        "identifier": str(identifier),
        "creation_date": freezed_now,
        "delivery_stamp": freezed_now.isoformat(),
        **context_query.model_dump(),
    }
    context = test_certificate.fetch_context()

    assert context == expected
