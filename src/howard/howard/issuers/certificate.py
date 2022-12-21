""""Certificate issuer"""

import datetime
from pathlib import Path
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, constr

from marion.issuers.base import AbstractDocument

BASE_64_IMAGE_REGEXP = r"^data:image/[-+\w.]+;base64,.*$"


class Organization(BaseModel):
    """Organization pydantic model"""

    name: str
    representative: str
    signature: Union[constr(regex=BASE_64_IMAGE_REGEXP), Path]
    logo: Union[constr(regex=BASE_64_IMAGE_REGEXP), Path]


class Student(BaseModel):
    """Student pydantic model"""

    name: str


class Course(BaseModel):
    """Course pydantic model"""

    name: str


class ContextModel(BaseModel):
    """Context pydantic model"""

    identifier: UUID
    student: Student
    organization: Organization
    course: Course
    creation_date: datetime.datetime
    delivery_stamp: datetime.datetime


class ContextQueryModel(BaseModel):
    """Context query pydantic model"""

    creation_date: Optional[datetime.datetime] = None
    student: Student
    course: Course
    organization: Organization


class CertificateDocument(AbstractDocument):
    """Certificate issuer"""

    keywords = ["certificate"]

    context_model = ContextModel
    context_query_model = ContextQueryModel

    css_template_path = Path("howard/certificate.css")
    html_template_path = Path("howard/certificate.html")

    def fetch_context(self) -> dict:
        """Certificate context"""

        context = self.context_query.dict()

        if context.get("creation_date") is None:
            context["creation_date"] = self.created

        return {
            "identifier": self.identifier,
            "delivery_stamp": self.created,
            **context,
        }
