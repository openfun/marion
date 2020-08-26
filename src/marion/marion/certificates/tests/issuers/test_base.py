"""Tests for the marion.certificates.issuers.base certificate"""

import uuid
from pathlib import Path
from unittest.mock import patch

from django.template import Context, Template, engines
from django.template.engine import Engine

import pytest
from pdfminer.high_level import extract_text as pdf_extract_text

from marion.certificates.exceptions import (
    CertificateIssuerContextQueryValidationError,
    CertificateIssuerContextValidationError,
    CertificateIssuerMissingContext,
)
from marion.certificates.issuers.base import AbstractCertificate


def test_abstract_certificate_interface_with_missing_abstract_methods():
    """Test interface mechanism with missing abstract methods"""

    class BadTestCertificate(AbstractCertificate):
        """Bad implementation with missing abstract methods"""

    # pylint: disable=abstract-class-instantiated
    with pytest.raises(
        TypeError,
        match=(
            "Can't instantiate abstract class BadTestCertificate with "
            "abstract methods fetch_context"
        ),
    ):
        BadTestCertificate()


def test_abstract_certificate_interface_with_implemented_abstract_method():
    """Test interface mechanism with properly implemented abstract methods"""

    class GoodTestCertificate(AbstractCertificate):
        """Correct implementation with required abstract methods"""

        def fetch_context(self, **context_query):
            """Fake context fetching"""

    GoodTestCertificate()


def test_abstract_certificate_init():
    """Test AbstractCertificate init method"""

    # pylint: disable=missing-class-docstring
    class TestCertificate(AbstractCertificate):
        def fetch_context(self, **context_query):
            pass

    test_certificate = TestCertificate()

    # Instance attributes
    assert test_certificate.identifier is not None
    assert isinstance(test_certificate.identifier, str)
    assert test_certificate.certificate_path is not None
    assert isinstance(test_certificate.certificate_path, Path)
    assert test_certificate.context is None
    assert test_certificate.css is None
    assert test_certificate.html is None

    # PDFFileMetadataMixin attributes
    assert test_certificate.created is None
    assert test_certificate.metadata is None
    assert test_certificate.modified is None


def test_abstract_certificate_generate_identifier():
    """Test AbstractCertificate generate_identifier method"""

    # pylint: disable=missing-class-docstring
    class TestCertificate(AbstractCertificate):
        def fetch_context(self, **context_query):
            pass

    test_certificate = TestCertificate()
    assert test_certificate.generate_identifier() == test_certificate.identifier

    identifier = uuid.uuid4()
    test_certificate = TestCertificate(identifier=str(identifier))
    assert test_certificate.generate_identifier() == str(identifier)

    other_identifier = uuid.uuid4()
    assert test_certificate.generate_identifier(str(other_identifier)) == str(
        identifier
    )

    test_certificate.identifier = None
    assert test_certificate.generate_identifier(str(other_identifier)) == str(
        other_identifier
    )


def test_abstract_certificate_get_certificate_path():
    """Test AbstractCertificate get_certificate_path method"""

    # pylint: disable=missing-class-docstring
    class TestCertificate(AbstractCertificate):
        def fetch_context(self, **context_query):
            pass

    test_certificate = TestCertificate()
    assert test_certificate.get_certificate_path() == Path(
        f"/tmp/{test_certificate.identifier}.pdf"
    )

    test_certificate.certificate_path = Path("/tmp/richie.pdf")
    assert test_certificate.get_certificate_path() == Path("/tmp/richie.pdf")


def test_abstract_certificate_get_certificate_url():
    """Test AbstractCertificate get_certificate_url method"""

    # pylint: disable=missing-class-docstring
    class TestCertificate(AbstractCertificate):
        def fetch_context(self, **context_query):
            pass

    test_certificate = TestCertificate()
    assert (
        test_certificate.get_certificate_url()
        == f"/media/{test_certificate.identifier}.pdf"
    )
    assert (
        test_certificate.get_certificate_url(host="example.org")
        == f"https://example.org/media/{test_certificate.identifier}.pdf"
    )
    assert (
        test_certificate.get_certificate_url(host="example.org", schema="http")
        == f"http://example.org/media/{test_certificate.identifier}.pdf"
    )


def test_abstract_certificate_get_css(monkeypatch):
    """Test AbstractCertificate get_css method"""

    monkeypatch.setattr(
        Engine, "get_template", lambda _, template_name: "body { color: red }"
    )

    # pylint: disable=missing-class-docstring
    class TestCertificate(AbstractCertificate):
        def fetch_context(self, **context_query):
            pass

    test_certificate = TestCertificate()
    assert test_certificate.get_css() is not None

    # Ensure we always return css attribute when set
    test_certificate.css = "body { color: red }"
    assert test_certificate.get_css() == "body { color: red }"
    monkeypatch.setattr(
        Engine, "get_template", lambda _, template_name: "body { color: blue }"
    )
    assert test_certificate.get_css() == "body { color: red }"


def test_abstract_certificate_get_css_template_path():
    """Test AbstractCertificate get_css_template_path method"""

    # pylint: disable=missing-class-docstring
    class TestCertificate(AbstractCertificate):
        def fetch_context(self, **context_query):
            pass

    test_certificate = TestCertificate()
    assert test_certificate.get_css_template_path() == Path(
        "marion/certificates/test.css"
    )

    test_certificate.css_template_path = Path("foo/bar.css")
    assert test_certificate.get_css_template_path() == Path("foo/bar.css")

    class TestCertificateWithSpecificHTMLTemplatePath(AbstractCertificate):
        css_template_path = Path("foo/specific.css")

        def fetch_context(self, **context_query):
            pass

    test_certificate = TestCertificateWithSpecificHTMLTemplatePath()
    assert test_certificate.get_css_template_path() == Path("foo/specific.css")


def test_abstract_certificate_get_html(monkeypatch):
    """Test AbstractCertificate get_html method"""

    monkeypatch.setattr(
        Engine, "get_template", lambda _, template_name: "body { color: red }"
    )

    # pylint: disable=missing-class-docstring
    class TestCertificate(AbstractCertificate):
        def fetch_context(self, **context_query):
            pass

    test_certificate = TestCertificate()
    assert test_certificate.get_html() is not None

    # Ensure we always return html attribute when set
    test_certificate.html = "body { color: red }"
    assert test_certificate.get_html() == "body { color: red }"
    monkeypatch.setattr(
        Engine, "get_template", lambda _, template_name: "body { color: blue }"
    )
    assert test_certificate.get_html() == "body { color: red }"


def test_abstract_certificate_get_html_template_path():
    """Test AbstractCertificate get_html_template_path method"""

    # pylint: disable=missing-class-docstring
    class TestCertificate(AbstractCertificate):
        def fetch_context(self, **context_query):
            pass

    test_certificate = TestCertificate()
    assert test_certificate.get_html_template_path() == Path(
        "marion/certificates/test.html"
    )

    test_certificate.html_template_path = Path("foo/bar.html")
    assert test_certificate.get_html_template_path() == Path("foo/bar.html")

    # pylint: disable=missing-class-docstring
    class TestCertificateWithSpecificHTMLTemplatePath(AbstractCertificate):
        html_template_path = Path("foo/specific.html")

        def fetch_context(self, **context_query):
            pass

    test_certificate = TestCertificateWithSpecificHTMLTemplatePath()
    assert test_certificate.get_html_template_path() == Path("foo/specific.html")


def test_abstract_certificate_get_template_engine():
    """Test AbstractCertificate get_template_engine method"""

    # pylint: disable=missing-class-docstring
    class TestCertificate(AbstractCertificate):
        def fetch_context(self, **context_query):
            pass

    test_certificate = TestCertificate()
    with patch.object(Engine, "get_default") as mocked_get_default:
        test_certificate.get_template_engine()
        mocked_get_default.assert_called()

    test_certificate.template_engine = "fake"
    with patch.object(Engine, "get_default") as mocked_get_default:
        test_certificate.get_template_engine()
        mocked_get_default.assert_not_called()


def test_abstract_certificate_validate_context():
    """Test AbstractCertificate validate_context method"""

    # pylint: disable=missing-class-docstring
    class TestCertificateWithMissingContextSchema(AbstractCertificate):
        def fetch_context(self, **context_query):
            pass

    with pytest.raises(
        CertificateIssuerContextValidationError, match="Context schema is missing"
    ):
        TestCertificateWithMissingContextSchema.validate_context({"foo": 1})

    # pylint: disable=missing-class-docstring
    class TestCertificate(AbstractCertificate):

        context_schema = {
            "type": "object",
            "properties": {
                "fullname": {"type": "string", "minLength": 2, "maxLength": 255},
                "friends": {"type": "integer"},
            },
            "required": ["fullname", "friends"],
            "additionalProperties": False,
        }

        def fetch_context(self, **context_query):
            pass

    with pytest.raises(
        CertificateIssuerContextValidationError, match="'None' is not of type 'integer'"
    ):
        TestCertificate.validate_context(
            {"fullname": "Richie Cunningham", "friends": "None"}
        )

    assert (
        TestCertificate.validate_context(
            {"fullname": "Richie Cunningham", "friends": 2}
        )
        is None
    )


def test_abstract_certificate_validate_context_query():
    """Test AbstractCertificate validate_context_query method"""

    # pylint: disable=missing-class-docstring
    class TestCertificateWithMissingContextSchema(AbstractCertificate):
        def fetch_context(self, **context_query):
            pass

    with pytest.raises(
        CertificateIssuerContextQueryValidationError,
        match="Context query schema is missing",
    ):
        TestCertificateWithMissingContextSchema.validate_context_query({"foo": 1})

    # pylint: disable=missing-class-docstring
    class TestCertificate(AbstractCertificate):

        context_query_schema = {
            "type": "object",
            "properties": {
                "fullname": {"type": "string", "minLength": 2, "maxLength": 255},
                "friends": {"type": "integer"},
            },
            "required": ["fullname", "friends"],
            "additionalProperties": False,
        }

        def fetch_context(self, **context_query):
            pass

    with pytest.raises(
        CertificateIssuerContextQueryValidationError,
        match="'None' is not of type 'integer'",
    ):
        TestCertificate.validate_context_query(
            {"fullname": "Richie Cunningham", "friends": "None"}
        )

    assert (
        TestCertificate.validate_context_query(
            {"fullname": "Richie Cunningham", "friends": 2}
        )
        is None
    )


def test_abstract_certificate_load_context():
    """Test AbstractCertificate load_context method"""

    # pylint: disable=missing-class-docstring
    class TestCertificate(AbstractCertificate):

        context_schema = {
            "type": "object",
            "properties": {
                "fullname": {"type": "string", "minLength": 2, "maxLength": 255},
                "friends": {"type": "integer"},
            },
            "required": ["fullname", "friends"],
            "additionalProperties": False,
        }

        def fetch_context(self, **context_query):
            pass

    test_certificate = TestCertificate()

    # Load valid context
    context = Context({"fullname": "Richie Cunningham", "friends": 2})
    test_certificate.load_context(context)
    assert test_certificate.context == context

    # Load invalid context
    context = Context({"fullname": "Richie Cunningham", "friends": "None"})
    with pytest.raises(
        CertificateIssuerContextValidationError,
        match=(
            "Certificate issuer context is not valid: "
            "'None' is not of type 'integer'"
        ),
    ):
        test_certificate.load_context(context)


def test_abstract_certificate_get_context_dict():
    """Test AbstractCertificate get_context_dict method"""

    # pylint: disable=missing-class-docstring
    class TestCertificate(AbstractCertificate):
        def fetch_context(self, **context_query):
            pass

    assert TestCertificate.get_context_dict(Context({"foo": 1})) == {"foo": 1}


def test_abstract_certificate_create():
    """Test AbstractCertificate create method"""

    # pylint: disable=missing-class-docstring
    class TestCertificate(AbstractCertificate):
        context_schema = {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "fullname": {"type": "string"},
            },
        }
        context_query_schema = {
            "type": "object",
            "properties": {"user_id": {"type": "string"}},
        }

        def get_html(self):
            return Template(
                "<body>My name is {{ fullname }} (user id: {{ user_id }})</body>"
            )

        def get_css(self):
            return Template("body {color: red}")

        def fetch_context(self, **context_query):
            return Context({"fullname": "Richie Cunningham", **context_query})

    test_certificate = TestCertificate()

    with pytest.raises(
        CertificateIssuerMissingContext, match="Context needs to be loaded first"
    ):
        test_certificate.create()

    context = test_certificate.fetch_context(user_id="rcunningham")
    test_certificate.load_context(context)
    test_certificate_path = test_certificate.create()

    assert Path(test_certificate_path).exists()
    with test_certificate_path.open("rb") as test_certificate_file:
        assert (
            pdf_extract_text(test_certificate_file).strip()
            == "My name is Richie Cunningham (user id: rcunningham)"
        )


def test_abstract_certificate_jinja_template_engine(settings):
    """Test certificate rendering with jinja templates"""

    settings.TEMPLATES = [
        {"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": []},
        {"BACKEND": "django.template.backends.jinja2.Jinja2", "DIRS": []},
    ]

    # pylint: disable=missing-class-docstring
    class TestCertificate(AbstractCertificate):
        template_engine = engines["jinja2"]

        def get_html(self):
            return self.template_engine.from_string(
                "{% set status='ninja' %}"
                "<body>My name is {{ fullname }} (status: {{ status }})</body>"
            )

        def fetch_context(self, **context_query):
            pass

    test_certificate = TestCertificate()
    assert (
        test_certificate.get_html().render({"fullname": "Richie Cunningham"})
        == "<body>My name is Richie Cunningham (status: ninja)</body>"
    )
