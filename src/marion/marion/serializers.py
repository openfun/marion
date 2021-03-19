"""Serializers for the marion application"""

from django.utils.translation import gettext_lazy as _

from pydantic.error_wrappers import ValidationError as PydanticValidationError
from rest_framework import serializers

from .exceptions import InvalidDocumentIssuer
from .models import DocumentRequest


class PydanticModelField(serializers.JSONField):
    """PydanticModel Field."""

    def __init__(self, *args, **kwargs):
        self.pydantic_model = kwargs.pop("pydantic_model", None)
        super().__init__(*args, **kwargs)

    def _get_pydantic_model(self):
        """Get field pydantic model from the serializer instance"""

        if self.pydantic_model is None:
            try:
                self.pydantic_model = getattr(
                    self.parent, f"get_{self.field_name}_pydantic_model"
                )()
            except AttributeError as error:
                raise serializers.ValidationError(
                    _(
                        f"A pydantic model is missing for the '{self.field_name}' "
                        "field. It should be provided thanks to the 'pydantic_model' "
                        "field argument or by adding a get_<FIELD_NAME>_pydantic_model "
                        "method to the serializer."
                    )
                ) from error

        return self.pydantic_model

    def _validate_pydantic_model(self, value):
        """Perform pydantic model validation"""

        pydantic_model = self._get_pydantic_model()

        try:
            pydantic_model(**value)
        except PydanticValidationError as error:
            raise serializers.ValidationError(error) from error

    def to_internal_value(self, data):
        """Validate data thanks to the field pydantic model"""

        internal = super().to_internal_value(data)

        self._validate_pydantic_model(internal)

        return internal


class DocumentRequestSerializer(serializers.HyperlinkedModelSerializer):
    """DocumentRequest model serializer"""

    class Meta:
        model = DocumentRequest
        fields = "__all__"

    # Force binary representation
    context = PydanticModelField(pydantic_model=None, binary=True, required=False)
    context_query = PydanticModelField(pydantic_model=None, binary=True)
    document_url = serializers.SerializerMethodField()

    def get_document_url(self, instance):
        """Add the document URL to the object"""

        return self._context.get("request").build_absolute_uri(
            instance.get_document_url()
        )

    def _get_issuer_class(self):
        """Get DocumentRequest issuer class from submitted data"""

        # At this stage, data has not been validated yet, hence we have no
        # choice but to use initial_data with caution to prevent bad issuer
        # submission.
        try:
            return self.Meta.model.get_issuer_class(self.initial_data.get("issuer"))
        except InvalidDocumentIssuer as error:
            raise serializers.ValidationError(_("")) from error

    def get_context_pydantic_model(self):
        """Get context pydantic model from the issuer class"""
        return self._get_issuer_class().context_model

    def get_context_query_pydantic_model(self):
        """Get context_query pydantic model from the issuer class"""
        return self._get_issuer_class().context_query_model
