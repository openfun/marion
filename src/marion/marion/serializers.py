"""Serializers for the marion application"""

from rest_framework import serializers

from .exceptions import DocumentIssuerMissingContext, InvalidDocumentIssuer
from .models import DocumentRequest, IssuerChoice


class IssuerChoiceSerializer(serializers.ModelSerializer):
    """IssuerChoice model serializer"""

    class Meta:
        model = IssuerChoice
        fields = "__all__"


class DocumentRequestSerializer(serializers.HyperlinkedModelSerializer):
    """DocumentRequest model serializer"""

    class Meta:
        model = DocumentRequest
        fields = "__all__"

    document_url = serializers.SerializerMethodField()

    def get_document_url(self, instance):
        """Add the document URL to the object"""

        return self._context.get("request").build_absolute_uri(
            instance.get_document_url()
        )

    issuer = serializers.CharField(max_length=100)

    def create(self, validated_data):
        if "issuer" in validated_data:
            issuer_path = validated_data.pop("issuer")
            obj = DocumentRequest(**validated_data)
            try:
                issuer = IssuerChoice.objects.get(issuer_path=issuer_path)
                obj.issuer = issuer
                obj.save()
                return obj
            except IssuerChoice.DoesNotExist as error:
                raise InvalidDocumentIssuer(
                    f"Could not find a matching IssuerChoice: {error}"
                ) from error

        raise DocumentIssuerMissingContext("`issuer` was not provided in POST")
