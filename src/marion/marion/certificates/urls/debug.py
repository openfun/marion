"""Debug Urls for the marion.certificates application"""

from django.urls import path

from .. import views

urlpatterns = [
    path(
        "templates/",
        views.certificate_template_debug,
        name="certificates-template-debug",
    )
]
