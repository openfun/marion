"""Realisation Certificate"""

import datetime
from enum import Enum
from typing import Generic, TypeVar
from uuid import UUID

from django.template import Context

import arrow
from dateutil import parser
from pydantic import BaseModel, ValidationError

from marion.issuers.base import AbstractDocument

ArrowSupportedDateType = TypeVar("ArrowSupportedDateType", int, str, datetime.date)


class StrEnum(str, Enum):
    """String Enum."""

    def __str__(self):
        return f"{self.value}"


class Gender(StrEnum):
    """Gender definitions."""

    MALE = "Mr"
    FEMALE = "Mme"

    def __str__(self):
        return f"{self.value}"


class CertificateScope(StrEnum):
    """Allowed scopes for the RealisationCertificate."""

    FORMATION = "action de formation"
    BILAN = "bilan de compétences"
    VAE = "action de VAE"
    APPRENTISSAGE = "action de formation par apprentissage"

    def __str__(self):
        return f"{self.value}"


class ArrowDate(Generic[ArrowSupportedDateType]):
    """ArrowDate generic class definition.

    To accept several input date types as string, integer or datetime.date,
    it is necessary to parse them to get a datetime.date object.

    The 'arrow' package is used to convert inputs in datetime.date with a
    wide range of possible writing formats.

    """

    def __init__(self, date: ArrowSupportedDateType) -> None:
        self.date = date

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        """Validates input date format with arrow library object."""

        if not isinstance(value, cls):
            raise TypeError("Invalid value")

        if isinstance(value.date, (int, str)):
            return arrow.get(value.date).date()

        if isinstance(value.date, datetime.date):
            return value.date

        raise ValidationError("Date value must be of type int, str or datetime.date.")


class DateSpan(BaseModel):
    """DateSpan model definition."""

    start: ArrowDate
    end: ArrowDate


class Manager(BaseModel):
    """Manager model definition."""

    first_name: str
    last_name: str
    position: str


class Organization(BaseModel):
    """Organization model definition."""

    name: str
    manager: Manager = None
    location: str = None


class Student(BaseModel):
    """Student model definition."""

    first_name: str
    last_name: str
    gender: Gender
    organization: Organization


class Session(BaseModel):
    """Course session model definition."""

    datespan: DateSpan
    duration: int
    scope: CertificateScope
    manager: Manager


class Course(BaseModel):
    """Course model definition."""

    name: str
    session: Session
    organization: Organization


class ContextModel(BaseModel):
    """Context model definition."""

    identifier: UUID
    course: Course
    student: Student
    creation_date: datetime.datetime
    delivery_stamp: datetime.datetime


class ContextQueryModel(BaseModel):
    """Context query model definition."""

    student: Student
    course: Course


class RealisationCertificate(AbstractDocument):
    """Official 'Certificat de réalisation des actions de formation'."""

    keywords = ["certificat", "réalisation", "formation"]
    title = "Certificat de réalisation des actions de formation"

    context_model = ContextModel
    context_query_model = ContextQueryModel

    def fetch_context(self, **context_query):
        """Fetch the context that will be used to compile the certificate template."""

        validated = self.validate_context_query(context_query)

        return Context(
            {
                "identifier": self.identifier,
                "course": validated.course,
                "student": validated.student,
                "creation_date": parser.isoparse(self.created),
                "delivery_stamp": self.created,
            }
        )
