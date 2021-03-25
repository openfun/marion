"""Tests for the marion.issuers.base document"""

import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from django.template import Context, Template, engines
from django.template.engine import Engine

import pytest
from pdfminer.high_level import extract_text as pdf_extract_text
from pydantic import BaseModel
from weasyprint.document import DocumentMetadata

from marion.defaults import DOCUMENTS_ROOT
from marion.exceptions import (
    DocumentIssuerContextQueryValidationError,
    DocumentIssuerContextValidationError,
    DocumentIssuerMissingContext,
    DocumentIssuerMissingContextQuery,
)
from marion.issuers.base import AbstractDocument


def test_abstract_document_interface_with_missing_abstract_methods():
    """Test interface mechanism with missing abstract methods"""

    class BadTestDocument(AbstractDocument):
        """Bad implementation with missing abstract methods"""

    # pylint: disable=abstract-class-instantiated
    with pytest.raises(
        TypeError,
        match=(
            "Can't instantiate abstract class BadTestDocument with "
            "abstract methods fetch_context"
        ),
    ):
        BadTestDocument()


def test_abstract_document_interface_with_implemented_abstract_method():
    """Test interface mechanism with properly implemented abstract methods"""

    class GoodTestDocument(AbstractDocument):
        """Correct implementation with required abstract methods"""

        def fetch_context(self, **context_query):
            """Fake context fetching"""

    GoodTestDocument()


def test_abstract_document_init(monkeypatch):
    """Test AbstractDocument init method"""

    # pylint: disable=missing-class-docstring
    class TestDocument(AbstractDocument):
        def fetch_context(self, **context_query):
            pass

    test_document = TestDocument()

    freezed_now = datetime(2021, 1, 1, 0, 0, 0)
    monkeypatch.setattr("django.utils.timezone.now", lambda: freezed_now)

    # Instance attributes
    assert test_document.identifier is not None
    assert isinstance(test_document.identifier, str)
    assert test_document.document_path is not None
    assert isinstance(test_document.document_path, Path)
    assert test_document.context is None
    assert test_document.css is None
    assert test_document.html is None

    # PDFFileMetadataMixin attributes
    assert test_document.created == freezed_now.isoformat()
    assert test_document.metadata is not None
    assert isinstance(test_document.metadata, DocumentMetadata)
    assert test_document.modified == freezed_now.isoformat()


def test_abstract_document_generate_identifier():
    """Test AbstractDocument generate_identifier method"""

    # pylint: disable=missing-class-docstring
    class TestDocument(AbstractDocument):
        def fetch_context(self, **context_query):
            pass

    test_document = TestDocument()
    assert test_document.generate_identifier() == test_document.identifier

    identifier = uuid.uuid4()
    test_document = TestDocument(identifier=str(identifier))
    assert test_document.generate_identifier() == str(identifier)

    other_identifier = uuid.uuid4()
    assert test_document.generate_identifier(str(other_identifier)) == str(identifier)

    test_document.identifier = None
    assert test_document.generate_identifier(str(other_identifier)) == str(
        other_identifier
    )


def test_abstract_document_get_document_path():
    """Test AbstractDocument get_document_path method"""

    # pylint: disable=missing-class-docstring
    class TestDocument(AbstractDocument):
        def fetch_context(self, **context_query):
            pass

    test_document = TestDocument()
    assert test_document.get_document_path() == Path(
        f"{DOCUMENTS_ROOT}/{test_document.identifier}.pdf"
    )

    test_document.document_path = Path(f"{DOCUMENTS_ROOT}/richie.pdf")
    assert test_document.get_document_path() == Path(f"{DOCUMENTS_ROOT}/richie.pdf")


def test_abstract_document_get_document_url():
    """Test AbstractDocument get_document_url method"""

    # pylint: disable=missing-class-docstring
    class TestDocument(AbstractDocument):
        def fetch_context(self, **context_query):
            pass

    test_document = TestDocument()
    assert test_document.get_document_url() == f"/media/{test_document.identifier}.pdf"
    assert (
        test_document.get_document_url(host="example.org")
        == f"https://example.org/media/{test_document.identifier}.pdf"
    )
    assert (
        test_document.get_document_url(host="example.org", schema="http")
        == f"http://example.org/media/{test_document.identifier}.pdf"
    )


def test_abstract_document_get_css(monkeypatch):
    """Test AbstractDocument get_css method"""

    monkeypatch.setattr(
        Engine, "get_template", lambda _, template_name: "body { color: red }"
    )

    # pylint: disable=missing-class-docstring
    class TestDocument(AbstractDocument):
        def fetch_context(self, **context_query):
            pass

    test_document = TestDocument()
    assert test_document.get_css() is not None

    # Ensure we always return css attribute when set
    test_document.css = "body { color: red }"
    assert test_document.get_css() == "body { color: red }"
    monkeypatch.setattr(
        Engine, "get_template", lambda _, template_name: "body { color: blue }"
    )
    assert test_document.get_css() == "body { color: red }"


def test_abstract_document_get_css_template_path():
    """Test AbstractDocument get_css_template_path method"""

    # pylint: disable=missing-class-docstring
    class TestDocument(AbstractDocument):
        def fetch_context(self, **context_query):
            pass

    test_document = TestDocument()
    assert test_document.get_css_template_path() == Path("marion/test.css")

    test_document.css_template_path = Path("foo/bar.css")
    assert test_document.get_css_template_path() == Path("foo/bar.css")

    class TestDocumentWithSpecificHTMLTemplatePath(AbstractDocument):
        css_template_path = Path("foo/specific.css")

        def fetch_context(self, **context_query):
            pass

    test_document = TestDocumentWithSpecificHTMLTemplatePath()
    assert test_document.get_css_template_path() == Path("foo/specific.css")


def test_abstract_document_get_html(monkeypatch):
    """Test AbstractDocument get_html method"""

    monkeypatch.setattr(
        Engine, "get_template", lambda _, template_name: "body { color: red }"
    )

    # pylint: disable=missing-class-docstring
    class TestDocument(AbstractDocument):
        def fetch_context(self, **context_query):
            pass

    test_document = TestDocument()
    assert test_document.get_html() is not None

    # Ensure we always return html attribute when set
    test_document.html = "body { color: red }"
    assert test_document.get_html() == "body { color: red }"
    monkeypatch.setattr(
        Engine, "get_template", lambda _, template_name: "body { color: blue }"
    )
    assert test_document.get_html() == "body { color: red }"


def test_abstract_document_get_html_template_path():
    """Test AbstractDocument get_html_template_path method"""

    # pylint: disable=missing-class-docstring
    class TestDocument(AbstractDocument):
        def fetch_context(self, **context_query):
            pass

    test_document = TestDocument()
    assert test_document.get_html_template_path() == Path("marion/test.html")

    test_document.html_template_path = Path("foo/bar.html")
    assert test_document.get_html_template_path() == Path("foo/bar.html")

    # pylint: disable=missing-class-docstring
    class TestDocumentWithSpecificHTMLTemplatePath(AbstractDocument):
        html_template_path = Path("foo/specific.html")

        def fetch_context(self, **context_query):
            pass

    test_document = TestDocumentWithSpecificHTMLTemplatePath()
    assert test_document.get_html_template_path() == Path("foo/specific.html")


def test_abstract_document_get_template_engine():
    """Test AbstractDocument get_template_engine method"""

    # pylint: disable=missing-class-docstring
    class TestDocument(AbstractDocument):
        def fetch_context(self, **context_query):
            pass

    test_document = TestDocument()
    with patch.object(Engine, "get_default") as mocked_get_default:
        test_document.get_template_engine()
        mocked_get_default.assert_called()

    test_document.template_engine = "fake"
    with patch.object(Engine, "get_default") as mocked_get_default:
        test_document.get_template_engine()
        mocked_get_default.assert_not_called()


def test_abstract_document_validate_context():
    """Test AbstractDocument validate_context method"""

    # pylint: disable=missing-class-docstring
    class TestDocumentWithMissingContextModel(AbstractDocument):
        def fetch_context(self, **context_query):
            pass

    with pytest.raises(DocumentIssuerMissingContext, match="Context model is missing"):
        TestDocumentWithMissingContextModel.validate_context({"foo": 1})

    class ContextModel(BaseModel):
        fullname: str
        friends: int

    # pylint: disable=missing-class-docstring
    class TestDocument(AbstractDocument):

        context_model = ContextModel

        def fetch_context(self, **context_query):
            pass

    with pytest.raises(
        DocumentIssuerContextValidationError, match="value is not a valid integer"
    ):
        TestDocument.validate_context(
            {"fullname": "Richie Cunningham", "friends": "None"}
        )

    assert TestDocument.validate_context(
        {"fullname": "Richie Cunningham", "friends": 2}
    ) == ContextModel(
        fullname="Richie Cunningham",
        friends=2,
    )


def test_abstract_document_validate_context_query():
    """Test AbstractDocument validate_context_query method"""

    # pylint: disable=missing-class-docstring
    class TestDocumentWithMissingContextModel(AbstractDocument):
        def fetch_context(self, **context_query):
            pass

    with pytest.raises(
        DocumentIssuerMissingContextQuery,
        match="Context query model is missing",
    ):
        TestDocumentWithMissingContextModel.validate_context_query({"foo": 1})

    # pylint: disable=missing-class-docstring
    class ContextQueryModel(BaseModel):
        fullname: str
        friends: int

    # pylint: disable=missing-class-docstring
    class TestDocument(AbstractDocument):

        context_query_model = ContextQueryModel

        def fetch_context(self, **context_query):
            pass

    with pytest.raises(
        DocumentIssuerContextQueryValidationError,
        match="value is not a valid integer",
    ):
        TestDocument.validate_context_query(
            {"fullname": "Richie Cunningham", "friends": "None"}
        )

    assert TestDocument.validate_context_query(
        {"fullname": "Richie Cunningham", "friends": 2}
    ) == ContextQueryModel(
        fullname="Richie Cunningham",
        friends=2,
    )


def test_abstract_document_set_context():
    """Test AbstractDocument set_context method"""

    # pylint: disable=missing-class-docstring
    class ContextModel(BaseModel):
        fullname: str
        friends: int

    # pylint: disable=missing-class-docstring
    class TestDocument(AbstractDocument):

        context_model = ContextModel

        def fetch_context(self, **context_query):
            pass

    test_document = TestDocument()

    # Load valid context
    context = Context({"fullname": "Richie Cunningham", "friends": 2})
    test_document.set_context(context)
    assert test_document.context == context

    # Load invalid context
    context = {"fullname": "Richie Cunningham", "friends": "None"}
    with pytest.raises(
        DocumentIssuerContextValidationError,
        match="value is not a valid integer",
    ):
        test_document.set_context(context)


# pylint: disable=missing-class-docstring
def test_abstract_document_get_django_context():
    """Test AbstractDocument get_django_context method"""

    class ContextModel(BaseModel):
        life: int

    class ContextQueryModel(BaseModel):
        intergalactic: str

    class TestDocument(AbstractDocument):
        context_model = ContextModel
        context_query_model = ContextQueryModel

        def fetch_context(self):
            return {"life": 42}

    document = TestDocument(context_query={"intergalactic": "voyager"})
    document.set_context(document.fetch_context())
    assert document.get_django_context() == Context({"life": 42})


def test_abstract_document_create():
    """Test AbstractDocument create method"""

    # pylint: disable=missing-class-docstring
    class ContextModel(BaseModel):
        user_id: str
        fullname: str

    # pylint: disable=missing-class-docstring
    class ContextQueryModel(BaseModel):
        user_id: str

    # pylint: disable=missing-class-docstring
    class TestDocument(AbstractDocument):
        context_model = ContextModel
        context_query_model = ContextQueryModel

        def get_html(self):
            return Template(
                "<body>My name is {{ fullname }} (user id: {{ user_id }})</body>"
            )

        def get_css(self):
            return Template("body {color: red}")

        def fetch_context(self):
            return {"fullname": "Richie Cunningham", **self.context_query.dict()}

    test_document = TestDocument(context_query={"user_id": "rcunningham"})
    test_document_path = test_document.create()

    assert Path(test_document_path).exists()
    with test_document_path.open("rb") as test_document_file:
        assert (
            pdf_extract_text(test_document_file).strip()
            == "My name is Richie Cunningham (user id: rcunningham)"
        )


def test_abstract_document_jinja_template_engine(settings):
    """Test document rendering with jinja templates"""

    settings.TEMPLATES = [
        {"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": []},
        {"BACKEND": "django.template.backends.jinja2.Jinja2", "DIRS": []},
    ]

    # pylint: disable=missing-class-docstring
    class TestDocument(AbstractDocument):
        template_engine = engines["jinja2"]

        def get_html(self):
            return self.template_engine.from_string(
                "{% set status='ninja' %}"
                "<body>My name is {{ fullname }} (status: {{ status }})</body>"
            )

        def fetch_context(self):
            pass

    test_document = TestDocument()
    assert (
        test_document.get_html().render({"fullname": "Richie Cunningham"})
        == "<body>My name is Richie Cunningham (status: ninja)</body>"
    )
