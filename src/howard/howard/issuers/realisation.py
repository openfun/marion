"""Realisation Certificate"""

import datetime
from pathlib import Path
from typing import Any, Generic, Optional, TypeVar
from uuid import UUID

import arrow
from dateutil import parser
from pydantic import BaseModel, GetCoreSchemaHandler, ValidationError
from pydantic_core import CoreSchema, core_schema

from marion.issuers.base import AbstractDocument

from ..utils import StrEnum

# pylint: disable=invalid-name
ArrowSupportedDateType = TypeVar(
    "ArrowSupportedDateType", int, str, datetime.date, datetime.datetime
)


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
    # pylint: disable=unused-argument,no-member
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate, handler(ArrowSupportedDateType)
        )

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
    manager: Optional[Manager] = None
    location: Optional[str] = None


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
            **self.context_query.model_dump(),
        }
