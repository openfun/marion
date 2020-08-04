"""Admin for the marion.certificates application"""

from django.contrib import admin

from .models import CertificateRequest


class CertificateRequestAdmin(admin.ModelAdmin):
    """CertificateModel admin"""


admin.site.register(CertificateRequest, CertificateRequestAdmin)
