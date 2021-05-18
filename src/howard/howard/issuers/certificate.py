""""Certificate issuer"""

import datetime
from pathlib import Path
from uuid import UUID

from dateutil import parser
from pydantic import BaseModel

from marion.issuers.base import AbstractDocument


class Organization(BaseModel):
    """Organization pydantic model"""

    name: str
    representative: str
    signature: Path
    logo: Path


class Student(BaseModel):
    """Student pydantic model"""

    name: str


class Course(BaseModel):
    """Course pydantic model"""

    name: str
    description: str
    organization: Organization


class ContextModel(BaseModel):
    """Context pydantic model"""

    identifier: UUID
    student: Student
    course: Course
    creation_date: datetime.datetime
    delivery_stamp: datetime.datetime


class ContextQueryModel(BaseModel):
    """Context query pydantic model"""

    student: Student
    course: Course


class CertificateDocument(AbstractDocument):
    """Certificate issuer"""

    keywords = ["certificate"]

    context_model = ContextModel
    context_query_model = ContextQueryModel

    css_template_path = Path("howard/certificate.css")
    html_template_path = Path("howard/certificate.html")

    def fetch_context(self) -> dict:
        """Certificate context"""
        return {
            "identifier": self.identifier,
            "creation_date": parser.isoparse(self.created),
            "delivery_stamp": self.created,
            **self.context_query.dict(),
        }
