"""Realisation Certificate"""

import datetime
from enum import Enum
from pathlib import Path
from typing import Generic, TypeVar
from uuid import UUID

import arrow
from dateutil import parser
from pydantic import BaseModel, ValidationError

from marion.issuers.base import AbstractDocument

ArrowSupportedDateType = TypeVar(
    "ArrowSupportedDateType", int, str, datetime.date, datetime.datetime
)


class StrEnum(str, Enum):
    """String Enum."""

    def __str__(self):
        return f"{self.value}"


class Gender(StrEnum):
    """Gender definitions."""

    MALE = "Mr"
    FEMALE = "Mme"


class CertificateScope(StrEnum):
    """Allowed scopes for the RealisationCertificate."""

    FORMATION = "action de formation"
    BILAN = "bilan de compétences"
    VAE = "action de VAE"
    APPRENTISSAGE = "action de formation par apprentissage"


class ArrowDate(Generic[ArrowSupportedDateType]):
    """ArrowDate field definition.

    To accept several input date types as string, integer, datetime.datetime or
    datetime.date, it is necessary to parse them to get a datetime.date object.

    The 'arrow' package is used to convert inputs in datetime.date with a
    wide range of possible writing formats.

    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        """Validates input date format with arrow library object."""

        if isinstance(value, (int, str)):
            return arrow.get(value).date()

        if isinstance(value, datetime.datetime):
            return value.date()

        if isinstance(value, datetime.date):
            return value

        raise ValidationError(
            "Date value must be of type int, str, datetime.date or datetime.datetime."
        )


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


class Course(BaseModel):
    """Course model definition."""

    name: str
    duration: int
    scope: CertificateScope
    organization: Organization


class CourseRun(BaseModel):
    """Course run model definition."""

    course: Course
    start: ArrowDate
    end: ArrowDate
    manager: Manager


class ContextModel(BaseModel):
    """Context model definition."""

    identifier: UUID
    course_run: CourseRun
    student: Student
    creation_date: datetime.datetime
    delivery_stamp: datetime.datetime


class ContextQueryModel(BaseModel):
    """Context query model definition."""

    student: Student
    course_run: CourseRun


class RealisationCertificate(AbstractDocument):
    """Official 'Certificat de réalisation des actions de formation'."""

    keywords = ["certificat", "réalisation", "formation"]
    title = "Certificat de réalisation des actions de formation"

    context_model = ContextModel
    context_query_model = ContextQueryModel

    css_template_path = Path("howard/realisation.css")
    html_template_path = Path("howard/realisation.html")

    def fetch_context(self) -> dict:
        """Fetch the context that will be used to compile the certificate template."""

        return {
            "identifier": self.identifier,
            "creation_date": parser.isoparse(self.created),
            "delivery_stamp": self.created,
            **self.context_query.dict(),
        }
