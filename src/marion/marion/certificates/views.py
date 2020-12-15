"""Views for the marion.certificates application"""
import datetime

from django.http import HttpResponse, HttpResponseBadRequest
from django.template import Context
from django.utils.module_loading import import_string

from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from .exceptions import CertificateIssuerContextValidationError
from .models import CertificateRequest
from .serializers import CertificateRequestSerializer


class CertificateRequestViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """API endpoint that allows certificate requests to be viewed, listed or created"""

    # pylint: disable=too-many-ancestors
    queryset = CertificateRequest.objects.all()
    serializer_class = CertificateRequestSerializer

    def create(self, request, *args, **kwargs):
        """Create a certificate request (and the corresponding certificate)"""

        try:
            return super().create(request, *args, **kwargs)
        except (CertificateIssuerContextValidationError,) as error:
            return Response(
                data={"error": str(error)}, status=status.HTTP_400_BAD_REQUEST
            )


def certificate_template_debug_view(request):
    """Certificate template debug view.

    Disclainer: this view should be used for development/testing purpose only.
    """
    issuer_path = request.GET.get("issuer", None)
    context = request.GET.get(
        "context",
        {
            "course": {
                "name": "edX Demonstration Course",
                "session": {
                    "date": {
                        "to": datetime.datetime(2020, 3, 1, 10, 0),
                        "from": datetime.datetime(2020, 2, 1, 23, 0),
                    },
                    "scope": "action de formation par apprentissage",
                    "duration": 23,
                    "manager": {
                        "position": "CHRO",
                        "last_name": "Riggs",
                        "first_name": "Martin",
                    },
                },
                "organization": {
                    "name": "edx",
                    "manager": {
                        "position": "CEO",
                        "last_name": "Agarwal",
                        "first_name": "Anant",
                    },
                    "location": "Boston, MA",
                },
            },
            "student": {
                "gender": "Mme",
                "last_name": "Doe",
                "first_name": "Jane",
                "organization": {"name": "ACME inc."},
            },
            "identifier": "53ced5ac-d3af-4b08-8ead-096a8cd007a4",
            "creation_date": datetime.datetime.now(),
        },
    )

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
