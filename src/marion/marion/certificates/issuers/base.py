"""Base certificate issuer for the marion.certificates application"""

import uuid
from abc import ABC, abstractmethod

from django.conf import settings
from django.template.engine import Engine
from django.utils.functional import cached_property
from django.utils.text import re_camel_case
from django.utils.translation import gettext_lazy as _

from jsonschema import ValidationError, validate
from weasyprint import CSS, HTML
from weasyprint.document import DocumentMetadata
from weasyprint.fonts import FontConfiguration

from marion import __version__ as marion_version

from .. import defaults
from ..exceptions import (
    CertificateIssuerContextQueryValidationError,
    CertificateIssuerContextValidationError,
    CertificateIssuerMissingContext,
)


class PDFFileMetadataMixin:
    """PDF file metadata"""

    attachments = None
    authors = None
    description = None
    generator = f"Marion, version {marion_version}"
    keywords = None
    title = None

    def __init__(self):

        self.created = None
        self.metadata = None
        self.modified = None

    def get_metadata(self):
        """Get certificate PDF file metadata.

        Return default (or set) certificate file metadata as a
        weasyprint.document.DocumentMetadata instance.

        """
        if self.metadata is None:
            self.metadata = DocumentMetadata(
                attachments=self.get_attachments(),
                authors=self.get_authors(),
                created=self.get_created(),
                description=self.get_description(),
                generator=self.get_generator(),
                keywords=self.get_keywords(),
                modified=self.get_modified(),
                title=self.get_title(),
            )
        return self.metadata

    def get_attachments(self):
        """Get certificate PDF file attachments metadata"""
        return self.attachments

    def get_authors(self):
        """Get certificate PDF file 'authors' metadata"""
        return self.authors

    def get_created(self):
        """Get certificate PDF file 'created' metadata"""
        return self.created

    def get_description(self):
        """Get certificate PDF file 'description' metadata"""
        return self.description

    def get_generator(self):
        """Get certificate PDF file 'generator' metadata"""
        return self.generator

    def get_keywords(self):
        """Get certificate PDF file 'keywords' metadata"""
        return self.keywords

    def get_modified(self):
        """Get certificate PDF file 'modified' metadata"""
        return self.modified

    def get_title(self):
        """Get certificate PDF file 'title' metadata"""
        return self.title


class AbstractCertificate(PDFFileMetadataMixin, ABC):
    """Base certificate interface.

    To define a new certificate, one should inherit from this interface and
    implement the `fetch_context` abstract method.

    """

    # Templates
    css_template_path = None
    html_template_path = None
    template_engine = None

    # Schemas
    context_schema = None
    context_query_schema = None

    def __init__(self, identifier=None):

        # Certificate
        self.identifier = self.generate_identifier(identifier)
        self.certificate_path = self.get_certificate_path()

        # Templates
        self.context = None
        self.css = None
        self.html = None

        super().__init__()

    @classmethod
    def validate_context(cls, context):
        """Use required context JSON schema to validate input context"""

        if cls.context_schema is None:
            raise CertificateIssuerContextValidationError(
                str(_("Context schema is missing"))
            )
        try:
            validate(context, cls.context_schema)
        except ValidationError as error:
            raise CertificateIssuerContextValidationError(
                _(f"Certificate issuer context is not valid: {error}")
            ) from error

    @classmethod
    def validate_context_query(cls, context_query):
        """Use required context query JSON schema to validate input context query"""

        if cls.context_query_schema is None:
            raise CertificateIssuerContextQueryValidationError(
                str(_("Context query schema is missing"))
            )
        try:
            validate(context_query, cls.context_query_schema)
        except ValidationError as error:
            raise CertificateIssuerContextQueryValidationError(
                _(f"Certificate issuer context query is not valid: {error}")
            ) from error

    @cached_property
    def __default_template_basename(self):
        """Get default template base name given its class name.

        Example subsequent class name transformations:
          DummyCertificate
            -> _Dummy_Certificate
            -> Dummy_Certificate
            -> dummy_certificate
            -> dummy
        """

        return (
            re_camel_case.sub(r"_\1", self.__class__.__name__)
            .strip("_")
            .lower()
            .replace("_certificate", "")
        )

    def __get_template(self, template_path):
        """Get a template from its relative path.

        This method always tries to return a template using the default
        template engine if it is not set.

        """
        if self.template_engine is None:
            template_engine = self.get_template_engine()
        return template_engine.get_template(template_path)

    def generate_identifier(self, identifier=None):
        """Generate the certificate identifier.

        If the identifier has been set or is provided as an argument, it will
        be returned, or else a new UUID is generated.

        """

        if hasattr(self, "identifier") and self.identifier is not None:
            return self.identifier
        if identifier is not None:
            return str(identifier)
        return str(uuid.uuid4())

    def get_certificate_path(self):
        """Get (generated) certificate path.

        Return default (or set) certificate path as a pathlib.Path object.

        """

        if hasattr(self, "certificate_path") and self.certificate_path is not None:
            return self.certificate_path
        return defaults.CERTIFICATES_ROOT.joinpath(f"{self.identifier}.pdf")

    def get_certificate_url(self, host=None, schema="https"):
        """Get (generated) certificate URL.

        If the host argument is provided a fully qualified URL will be
        returned, or else, an absolute URL will be generated.

        """
        relative_path = self.get_certificate_path().relative_to(settings.MEDIA_ROOT)
        relative_url = f"{settings.MEDIA_URL}{relative_path}"
        if host is None:
            return relative_url
        return f"{schema}://{host}{relative_url}"

    def get_css(self):
        """Get CSS template instance"""

        if self.css is not None:
            return self.css
        return self.__get_template(self.get_css_template_path())

    def get_css_template_path(self):
        """Get CSS template path.

        Return default (or set) CSS template path as a pathlib.Path object.

        """

        if self.css_template_path is not None:
            return self.css_template_path
        return defaults.CERTIFICATES_TEMPLATE_ROOT.joinpath(
            f"{self.__default_template_basename}.css"
        )

    def get_html(self):
        """Get HTML template instance"""

        if self.html is not None:
            return self.html
        return self.__get_template(self.get_html_template_path())

    def get_html_template_path(self):
        """Get HTML template path.

        Return default (or set) HTML template path as a pathlib.Path object.

        """

        if self.html_template_path is not None:
            return self.html_template_path
        return defaults.CERTIFICATES_TEMPLATE_ROOT.joinpath(
            f"{self.__default_template_basename}.html"
        )

    def get_template_engine(self):
        """Get template engine.

        Return default (or set) template engine.

        """
        if self.template_engine is not None:
            return self.template_engine
        return Engine.get_default()

    @abstractmethod
    def fetch_context(self, **context_query):
        """Fetch certificate context given context query parameters.

        This method should be implemented while using this interface for a
        custom certificate class.

        Note that it is highly recommended to validate the context_query using
        the validate_context_query method in your implementation to ensure data
        consistency.

        Returns fetched context as a Django Context instance.

        """

    def load_context(self, context):
        """Validate and set context passed as a Django Context instance"""

        try:
            self.validate_context(self.get_context_dict(context))
        except ValidationError as error:
            raise CertificateIssuerContextValidationError(
                _(f"Fetched context is not valid, error was: {error}")
            ) from error
        else:
            self.context = context

    @classmethod
    def get_context_dict(cls, context):
        """Get the context dict from a Django Context instance"""
        return context.dicts[1]

    def create(self):
        """Create certificate.

        Given an HTML template, a CSS template and the required context to
        compile them, we render the certificate HTML that will be used by
        Weasyprint's headless web browser to generate the certificate as a PDF
        file.

        The path of the certificate is returned as a pathlib.Path instance.

        """

        if self.context is None:
            raise CertificateIssuerMissingContext("Context needs to be loaded first")

        certificate_path = self.get_certificate_path()

        font_config = FontConfiguration()
        html = HTML(string=self.get_html().render(self.context))
        css = CSS(string=self.get_css().render(self.context), font_config=font_config)

        certificate = html.render(stylesheets=[css], font_config=font_config)
        certificate.metadata = self.get_metadata()
        certificate.write_pdf(target=certificate_path, zoom=1)

        return certificate_path
