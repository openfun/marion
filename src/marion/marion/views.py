"""Views for the marion application"""

import json

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse, HttpResponseBadRequest
from django.template import Context
from django.utils.module_loading import import_string

from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from .exceptions import (
    DocumentIssuerContextQueryValidationError,
    DocumentIssuerContextValidationError,
)
from .models import DocumentRequest
from .serializers import DocumentRequestSerializer


class DocumentRequestViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """API endpoint that allows document requests to be viewed, listed or created"""

    # pylint: disable=too-many-ancestors
    queryset = DocumentRequest.objects.all()
    serializer_class = DocumentRequestSerializer

    def create(self, request, *args, **kwargs):
        """Create a document request (and the corresponding document)"""

        try:
            return super().create(request, *args, **kwargs)
        except (
            DocumentIssuerContextQueryValidationError,
            DocumentIssuerContextValidationError,
            ValidationError,
        ) as error:
            return Response(
                data={"error": str(error)}, status=status.HTTP_400_BAD_REQUEST
            )


def document_template_debug(request):
    """Document template debug view.

    Disclaimer: this view should be used for development/testing purpose only.
    """

    if not settings.DEBUG:
        raise PermissionDenied

    issuer_path = request.GET.get("issuer", None)
    context = json.loads(request.GET.get("context", "{}"))

    if issuer_path is None:
        return HttpResponseBadRequest("You should provide an issuer.")

    try:
        issuer = import_string(issuer_path)()
    except ImportError:
        return HttpResponseBadRequest(f"Unknown issuer {issuer_path}.")

    css = issuer.get_css().render(Context(context))
    context.update({"css": css, "debug": True})
    html = issuer.get_html().render(Context(context))

    return HttpResponse(html)
