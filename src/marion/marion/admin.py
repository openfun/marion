"""Admin for the marion application"""

from django.contrib import admin

from .models import DocumentRequest, IssuerChoice


class DocumentRequestAdmin(admin.ModelAdmin):
    """DocumentRequest admin"""


class IssuerChoiceAdmin(admin.ModelAdmin):
    """IssuerChoice admin"""


admin.site.register(DocumentRequest, DocumentRequestAdmin)
admin.site.register(IssuerChoice, IssuerChoiceAdmin)
