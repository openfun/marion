"""Urls for the marion application"""

from django.urls import include, path

from rest_framework import routers

from .. import views

router = routers.DefaultRouter()
router.register(r"requests", views.DocumentRequestViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
