"""Debug Urls for the marion project."""

from django.urls import include, path

from . import urlpatterns

urlpatterns += [path("__debug__/", include("marion.urls.debug"))]
