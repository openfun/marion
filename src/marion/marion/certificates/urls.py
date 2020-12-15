"""Urls for the marion.certificates application"""

from django.conf import settings
from django.urls import include, path

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"requests", views.CertificateRequestViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += [path("templates/debug/", views.certificate_template_debug_view)]
