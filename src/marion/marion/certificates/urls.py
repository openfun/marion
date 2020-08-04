"""Urls for the marion.certificates application"""

from django.urls import include, path

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"requests", views.CertificateRequestViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
