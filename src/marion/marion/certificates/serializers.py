"""Serializers for the marion.certificates application"""

from django.utils.translation import gettext_lazy as _

from jsonschema import ValidationError as JSONSchemaValidationError
from jsonschema import validate
from rest_framework import serializers

from .exceptions import InvalidCertificateIssuer
from .models import CertificateRequest


class JSONSchemaField(serializers.JSONField):
    """JSONSchema Field."""

    def __init__(self, *args, **kwargs):
        self.schema = kwargs.pop("schema", None)
        super().__init__(*args, **kwargs)

    def _get_schema(self):
        """Get field schema from the serializer instance"""

        if self.schema is None:
            try:
                self.schema = getattr(self.parent, f"get_{self.field_name}_schema")()
            except AttributeError as error:
                raise serializers.ValidationError(
                    _(
                        f"A schema is missing for the '{self.field_name}' field. "
                        "It should be provided thanks to the 'schema' field argument "
                        "or by adding a get_<FIELD_NAME>_schema method to the "
                        "serializer."
                    )
                ) from error

        return self.schema

    def _validate_schema(self, value):
        """Perform schema validation"""

        schema = self._get_schema()

        try:
            validate(value, schema)
        except JSONSchemaValidationError as error:
            raise serializers.ValidationError(error.message) from error

    def to_internal_value(self, data):
        """Validate data thanks to the field schema"""

        internal = super().to_internal_value(data)

        self._validate_schema(internal)

        return internal


class CertificateRequestSerializer(serializers.HyperlinkedModelSerializer):
    """CertificateRequest model serializer"""

    class Meta:
        model = CertificateRequest
        fields = "__all__"

    # Force binary representation
    context = JSONSchemaField(schema=None, binary=True, required=False)
    context_query = JSONSchemaField(schema=None, binary=True)
    certificate_url = serializers.SerializerMethodField()

    def get_certificate_url(self, instance):
        """Add the certificate URL to the object"""

        return self._context.get("request").build_absolute_uri(
            instance.get_certificate_url()
        )

    def _get_issuer_class(self):
        """Get CertificateRequest issuer class from submitted data"""

        # At this stage, data has not been validated yet, hence we use
        # initial_data to prevent bad issuer submission.
        try:
            return self.Meta.model.get_issuer_class(self.initial_data.get("issuer"))
        except InvalidCertificateIssuer as error:
            raise serializers.ValidationError(_("")) from error

    def get_context_schema(self):
        """Get context schema from the issuer class"""
        return self._get_issuer_class().context_schema

    def get_context_query_schema(self):
        """Get context_query schema from the issuer class"""
        return self._get_issuer_class().context_query_schema
