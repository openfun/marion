"""Base document issuer for the marion.documents application"""

import uuid
from abc import ABC, abstractmethod

from django.conf import settings
from django.template.engine import Engine
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import re_camel_case
from django.utils.translation import gettext_lazy as _

from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError
from weasyprint import CSS, HTML
from weasyprint.document import DocumentMetadata
from weasyprint.fonts import FontConfiguration

from marion import __version__ as marion_version

from .. import defaults
from ..exceptions import (
    DocumentIssuerContextQueryValidationError,
    DocumentIssuerContextValidationError,
    DocumentIssuerMissingContext,
)
from ..utils import static_file_fetcher


class PDFFileMetadataMixin:
    """PDF file metadata"""

    attachments = None
    authors = None
    description = None
    generator = f"Marion, version {marion_version}"
    keywords = None
    title = None

    def __init__(self):

        self._created = None
        self._metadata = None
        self._modified = None

    @property
    def metadata(self):
        """Get document PDF file metadata.

        Return default (or set) document file metadata as a
        weasyprint.document.DocumentMetadata instance.

        """
        if self._metadata is None:
            self._metadata = DocumentMetadata(
                attachments=self.get_attachments(),
                authors=self.get_authors(),
                created=self.created,
                description=self.get_description(),
                generator=self.get_generator(),
                keywords=self.get_keywords(),
                modified=self.modified,
                title=self.get_title(),
            )
        return self._metadata

    def get_attachments(self):
        """Get document PDF file attachments metadata"""
        return self.attachments

    def get_authors(self):
        """Get document PDF file 'authors' metadata"""
        return self.authors

    @property
    def created(self):
        """Get document PDF file 'created' metadata"""
        if self._created is None:
            self._created = timezone.now().isoformat()
        return self._created

    def get_description(self):
        """Get document PDF file 'description' metadata"""
        return self.description

    def get_generator(self):
        """Get document PDF file 'generator' metadata"""
        return self.generator

    def get_keywords(self):
        """Get document PDF file 'keywords' metadata"""
        return self.keywords

    @property
    def modified(self):
        """Get document PDF file 'modified' metadata"""
        if self._modified is None:
            self._modified = timezone.now().isoformat()
        return self._modified

    def get_title(self):
        """Get document PDF file 'title' metadata"""
        return self.title


# pylint: disable=not-callable
class AbstractDocument(PDFFileMetadataMixin, ABC):
    """Base document interface.

    To define a new document, one should inherit from this interface and
    implement the `fetch_context` abstract method.

    """

    # Templates
    css_template_path = None
    html_template_path = None
    template_engine = None

    # Models
    context_model: BaseModel = None
    context_query_model: BaseModel = None

    def __init__(self, identifier=None):

        # Document
        self.identifier = self.generate_identifier(identifier)
        self.document_path = self.get_document_path()

        # Templates
        self.context = None
        self.css = None
        self.html = None

        super().__init__()

    @classmethod
    def validate_context(cls, context):
        """Use required context pydantic model to validate input context."""

        if cls.context_model is None:
            raise DocumentIssuerContextValidationError(
                str(_("Context model is missing"))
            )
        try:
            return cls.context_model(**context)
        except ValidationError as error:
            raise DocumentIssuerContextValidationError(
                _(f"Document issuer context is not valid: {error}")
            ) from error

    @classmethod
    def validate_context_query(cls, context_query):
        """Use required context query pydantic model to validate input context query."""

        if cls.context_query_model is None:
            raise DocumentIssuerContextQueryValidationError(
                str(_("Context query model is missing"))
            )
        try:
            return cls.context_query_model(**context_query)
        except ValidationError as error:
            raise DocumentIssuerContextQueryValidationError(
                _(f"Document issuer context query is not valid: {error}")
            ) from error

    @cached_property
    def __default_template_basename(self):
        """Get default template base name given its class name.

        Example subsequent class name transformations:
          DummyDocument
            -> _Dummy_Document
            -> Dummy_Document
            -> dummy_document
            -> dummy
        """

        return (
            re_camel_case.sub(r"_\1", self.__class__.__name__)
            .strip("_")
            .lower()
            .replace("_document", "")
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
        """Generate the document identifier.

        If the identifier has been set or is provided as an argument, it will
        be returned, or else a new UUID is generated.

        """

        if hasattr(self, "identifier") and self.identifier is not None:
            return self.identifier
        if identifier is not None:
            return str(identifier)
        return str(uuid.uuid4())

    def get_document_path(self):
        """Get (generated) document path.

        Return default (or set) document path as a pathlib.Path object.

        """

        if hasattr(self, "document_path") and self.document_path is not None:
            return self.document_path
        return defaults.DOCUMENTS_ROOT.joinpath(f"{self.identifier}.pdf")

    def get_document_url(self, host=None, schema="https"):
        """Get (generated) document URL.

        If the host argument is provided a fully qualified URL will be
        returned, or else, an absolute URL will be generated.

        """
        relative_path = self.get_document_path().relative_to(defaults.DOCUMENTS_ROOT)
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
        return defaults.DOCUMENTS_TEMPLATE_ROOT.joinpath(
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
        return defaults.DOCUMENTS_TEMPLATE_ROOT.joinpath(
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
        """Fetch document context given context query parameters.

        This method should be implemented while using this interface for a
        custom document class.

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
            raise DocumentIssuerContextValidationError(
                _(f"Fetched context is not valid, error was: {error}")
            ) from error
        else:
            self.context = context

    @classmethod
    def get_context_dict(cls, context):
        """Get the context dict from a Django Context instance"""
        return context.dicts[1]

    def create(self):
        """Create document.

        Given an HTML template, a CSS template and the required context to
        compile them, we render the document HTML that will be used by
        Weasyprint's headless web browser to generate the document as a PDF
        file.

        The path of the document is returned as a pathlib.Path instance.

        """

        if self.context is None:
            raise DocumentIssuerMissingContext("Context needs to be loaded first")

        document_path = self.get_document_path()
        html_str = self.get_html().render(self.context)
        css_str = self.get_css().render(self.context)

        font_config = FontConfiguration()
        html = HTML(string=html_str, url_fetcher=static_file_fetcher)
        css = CSS(string=css_str, font_config=font_config)

        document = html.render(stylesheets=[css], font_config=font_config)
        document.metadata = self.metadata
        document.write_pdf(target=document_path, zoom=1)

        return document_path
