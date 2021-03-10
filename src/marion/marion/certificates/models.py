"""Models for the marion.certificates application"""

import uuid

from django.core.exceptions import FieldError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from pydantic.error_wrappers import ValidationError as PydanticValidationError

from .defaults import CERTIFICATE_ISSUER_CHOICES_CLASS
from .exceptions import InvalidCertificateIssuer

CertificateIssuerChoices = import_string(CERTIFICATE_ISSUER_CHOICES_CLASS)


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
        try:
            pydantic_model(**value)
        except PydanticValidationError as error:
            raise DjangoValidationError(error, code="invalid") from error

    def _get_pydantic_model(self, model_instance):
        """Get field pydantic model from the expected model instance method"""

        if self.pydantic_model is None:
            try:
                self.pydantic_model = getattr(
                    model_instance, f"get_{self.name}_pydantic_model"
                )()
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

        super().validate(value, model_instance)

        self._validate_pydantic_model(value, model_instance)

    def pre_save(self, model_instance, add):
        """Ensure pydantic model validation occurs before saving"""

        value = super().pre_save(model_instance, add)
        if value and not self.null:
            self._validate_pydantic_model(value, model_instance)
        return value


class CertificateRequest(models.Model):
    """Certificate Requests are stored in models and linked to certificates.

    Each certificate request has a particular issuer, context, and
    context_query. An issuer is responsible for the generation of a particular
    type of certificate in PDF format; it has its own logic that implements how
    to fetch required context to compile a certificate template given a
    context_query.

    Note that a certificate request has its own unique identifier that is
    distinct from the certificate unique identifier as we consider them as
    dictinct objects; but we make sure that one cannot generate two
    certificates with the same identifier from two certificate requests.
    Another advantage of having a distinct identifier for a certificate request
    and a request is that one cannot guess a certificate request identifier
    from a certificate identifier, and thus one cannot access to the
    certificate request object via the certificate requests API.

    Given an issuer and a context, we should be able to re-generate a
    particular certificate if the PDF file has been lost or deleted. In last
    resort, we also should be able to re-generate the context from the
    context_query, but the latest is mostly stored for tracking purpose.

    """

    id = models.UUIDField(
        verbose_name=_("ID"),
        help_text=_("Primary key for the certificate request as UUID"),
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    created_on = models.DateTimeField(
        verbose_name=_("Created on"),
        help_text=_("Date and time at which a certificate request was created"),
        auto_now_add=True,
        editable=False,
    )

    updated_on = models.DateTimeField(
        verbose_name=_("Updated on"),
        help_text=_("Date and time at which a certificate request was last updated"),
        auto_now=True,
        editable=False,
    )

    certificate_id = models.UUIDField(
        verbose_name=_("Certificate ID"),
        help_text=_("Generated certificate identifier"),
        null=True,
        unique=True,
    )

    issuer = models.CharField(
        verbose_name=_("Issuer"),
        help_text=_("The issuer of the certificate among allowed ones"),
        max_length=200,
        choices=CertificateIssuerChoices.choices,
    )

    context = PydanticModelField(
        pydantic_model=None,
        verbose_name=_("Collected context"),
        help_text=_("Context used to render the certificate's template"),
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
        """Options for the CertificateRequest model"""

        ordering = ["-created_on"]

    def get_context_pydantic_model(self):
        """Get context pydantic model from the issuer class"""
        return self.get_issuer_class(self.issuer).context_model

    def get_context_query_pydantic_model(self):
        """Get context_query pydantic model from the issuer class"""
        return self.get_issuer_class(self.issuer).context_query_model

    # pylint: disable=signature-differs
    def save(self, *args, **kwargs):
        """Generate the certificate along with the certificate request"""

        # Perform early clean up
        self.full_clean(exclude=["certificate_id", "context"])

        certificate = self.get_issuer()
        certificate.load_context(certificate.fetch_context(**self.context_query))
        certificate.create()

        self.certificate_id = certificate.identifier
        self.context = certificate.get_context_dict(certificate.context)

        # Validate new fields before saving
        self.full_clean(exclude=["context_query", "issuer"])

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
            raise InvalidCertificateIssuer(
                _(f"{issuer_class_name} is not an allowed issuer")
            )
        if matches > 1:
            raise InvalidCertificateIssuer(
                _(
                    f"Issuer class name should be unique, found {matches} for "
                    f"{issuer_class_name}"
                )
            )
        return import_string(issuer_class_paths[0])

    def get_issuer(self):
        """Get instanciated issuer class"""
        return self.get_issuer_class(self.issuer)(identifier=self.certificate_id)

    def get_certificate_url(self, host=None, schema="https"):
        """Shortcut to get the certificate URL.

        This method is mostly a wrapper for the issuer's `get_certificate_url`
        method. If no host or schema is provided, an absolute URL is returned
        (and not a fully qualified URL).

        """
        return self.get_issuer().get_certificate_url(host=host, schema=schema)
