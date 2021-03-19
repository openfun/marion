"""Admin for the marion application"""

from django.contrib import admin

from .models import DocumentRequest


class DocumentRequestAdmin(admin.ModelAdmin):
    """DocumentModel admin"""


admin.site.register(DocumentRequest, DocumentRequestAdmin)
