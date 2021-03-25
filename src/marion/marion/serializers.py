"""Serializers for the marion application"""

from rest_framework import serializers

from .models import DocumentRequest


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
