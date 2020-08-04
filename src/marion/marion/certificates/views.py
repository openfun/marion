"""Views for the marion.certificates application"""

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
