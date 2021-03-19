"""Debug Urls for the marion application"""

from django.urls import path

from .. import views

urlpatterns = [
    path(
        "templates/",
        views.document_template_debug,
        name="documents-template-debug",
    )
]
