"""Models for the marion application"""

import json
import uuid

from django.core.exceptions import FieldError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from pydantic.error_wrappers import ValidationError as PydanticValidationError

from .defaults import DOCUMENT_ISSUER_CHOICES_CLASS
from .exceptions import DocumentIssuerContextQueryValidationError, InvalidDocumentIssuer

DocumentIssuerChoices = import_string(DOCUMENT_ISSUER_CHOICES_CLASS)


class PydanticModelField(models.JSONField):
    """Pydantic Model Field.

    This field is a pydantic model field but with model validation when the model
    is provided.

    """

    def __init__(self, *args, **kwargs):
        self.pydantic_model = kwargs.pop("pydantic_model", None)
        super().__init__(*args, **kwargs)

    def _validate_pydantic_model(self, value, model_instance):
        """Perform pydantic model validation"""

        pydantic_model = self._get_pydantic_model(model_instance)

        # Disable validation when migrations are faked
        if self.model.__module__ == "__fake__":
            return

        # Validate either raw (JSON string) data or a serialized dict (before
        # saving the Django model).
        try:
            if isinstance(value, str):
                pydantic_model.parse_raw(value)
            elif isinstance(value, dict):
                pydantic_model(**value)
        except PydanticValidationError as error:
            raise DjangoValidationError(error, code="invalid") from error

    def _get_pydantic_model(self, model_instance):
        """Get field pydantic model from the expected model instance method"""

        if self.pydantic_model is None:
            try:
                return getattr(model_instance, f"get_{self.name}_pydantic_model")()
            except AttributeError as error:
                raise FieldError(
                    _(
                        f"A pydantic model is missing for the '{self.name}' field. "
                        "It should be provided thanks to the 'pydantic_model' "
                        "field argument or by adding a get_<FIELD_NAME>_pydantic_model "
                        "method to your model."
                    )
                ) from error
        return self.pydantic_model

    def validate(self, value, model_instance):
        """Add pydantic model validation to field validation"""

        # Validate JSON value
        super().validate(value, model_instance)

        self._validate_pydantic_model(value, model_instance)

    def pre_save(self, model_instance, add):
        """Ensure pydantic model validation occurs before saving"""

        value = super().pre_save(model_instance, add)
        if value and not self.null:
            self._validate_pydantic_model(value, model_instance)
        return value


class DocumentRequest(models.Model):
    """Document Requests are stored in models and linked to documents.

    Each document request has a particular issuer, context, and
    context_query. An issuer is responsible for the generation of a particular
    type of document in PDF format; it has its own logic that implements how
    to fetch required context to compile a document template given a
    context_query.

    Note that a document request has its own unique identifier that is
    distinct from the document unique identifier as we consider them as
    dictinct objects; but we make sure that one cannot generate two
    documents with the same identifier from two document requests.
    Another advantage of having a distinct identifier for a document request
    and a request is that one cannot guess a document request identifier
    from a document identifier, and thus one cannot access to the
    document request object via the document requests API.

    Given an issuer and a context, we should be able to re-generate a
    particular document if the PDF file has been lost or deleted. In last
    resort, we also should be able to re-generate the context from the
    context_query, but the latest is mostly stored for tracking purpose.

    """

    id = models.UUIDField(
        verbose_name=_("ID"),
        help_text=_("Primary key for the document request as UUID"),
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    created_on = models.DateTimeField(
        verbose_name=_("Created on"),
        help_text=_("Date and time at which a document request was created"),
        auto_now_add=True,
        editable=False,
    )

    updated_on = models.DateTimeField(
        verbose_name=_("Updated on"),
        help_text=_("Date and time at which a document request was last updated"),
        auto_now=True,
        editable=False,
    )

    document_id = models.UUIDField(
        verbose_name=_("Document ID"),
        help_text=_("Generated document identifier"),
        null=True,
        unique=True,
    )

    issuer = models.CharField(
        verbose_name=_("Issuer"),
        help_text=_("The issuer of the document among allowed ones"),
        max_length=200,
        choices=DocumentIssuerChoices.choices,
    )

    context = PydanticModelField(
        pydantic_model=None,
        verbose_name=_("Collected context"),
        help_text=_("Context used to render the document's template"),
        editable=False,
        null=True,
        blank=True,
    )

    context_query = PydanticModelField(
        pydantic_model=None,
        verbose_name=_("Context query parameters"),
        help_text=_("Context will be fetched from those parameters"),
    )

    class Meta:
        """Options for the DocumentRequest model"""

        ordering = ["-created_on"]

    def get_context_pydantic_model(self):
        """Get context pydantic model from the issuer class"""
        return self.get_issuer_class(self.issuer).context_model

    def get_context_query_pydantic_model(self):
        """Get context_query pydantic model from the issuer class"""
        return self.get_issuer_class(self.issuer).context_query_model

    # pylint: disable=signature-differs
    def save(self, *args, **kwargs):
        """Generate the document along with the document request"""

        document = self.get_issuer()
        document.create()

        self.document_id = document.identifier

        # Prevent JSON encoding issues
        #
        # Pydantic knows how to JSON-serialize all fields, the standard JSON
        # encoder does not. So we convert pydantic model data to a
        # dumb-dict with simple types using this trick.
        self.context = json.loads(document.context.json())
        self.context_query = json.loads(document.context_query.json())

        super().save(*args, **kwargs)

    @classmethod
    def get_issuer_class(cls, issuer_class_name):
        """Get issuer class given its class name (or its path)"""

        # pylint: disable=no-member
        issuer_class_paths = list(
            filter(
                lambda issuer_module_path: issuer_module_path.endswith(
                    issuer_class_name
                ),
                # pylint: disable=no-member
                (issuer for issuer, _ in cls.issuer.field.choices),
            )
        )
        matches = len(issuer_class_paths)
        if matches == 0:
            raise InvalidDocumentIssuer(
                _(f"{issuer_class_name} is not an allowed issuer")
            )
        if matches > 1:
            raise InvalidDocumentIssuer(
                _(
                    f"Issuer class name should be unique, found {matches} for "
                    f"{issuer_class_name}"
                )
            )
        return import_string(issuer_class_paths[0])

    def get_issuer(self):
        """Get instanciated issuer class"""

        try:
            return self.get_issuer_class(self.issuer)(
                identifier=self.document_id, context_query=self.context_query
            )
        except DocumentIssuerContextQueryValidationError as error:
            raise DjangoValidationError(error, code="invalid") from error

    def get_document_url(self, host=None, schema="https"):
        """Shortcut to get the document URL.

        This method is mostly a wrapper for the issuer's `get_document_url`
        method. If no host or schema is provided, an absolute URL is returned
        (and not a fully qualified URL).

        """
        return self.get_issuer().get_document_url(host=host, schema=schema)

    def get_document_path(self):
        """Shortcut to get the document PATH.

        This method is mostly a wrapper for the issuer's `get_document_path`
        method.

        """
        return self.get_issuer().get_document_path()
