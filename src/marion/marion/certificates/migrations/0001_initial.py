# Generated by Django 3.1 on 2020-09-04 09:29

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CertificateRequest",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Primary key for the certificate request as UUID",
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_on",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Date and time at which a certificate request was created",
                        verbose_name="Created on",
                    ),
                ),
                (
                    "updated_on",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Date and time at which a certificate request was last updated",
                        verbose_name="Updated on",
                    ),
                ),
                (
                    "certificate_id",
                    models.UUIDField(
                        help_text="Generated certificate identifier",
                        null=True,
                        unique=True,
                        verbose_name="Certificate ID",
                    ),
                ),
                (
                    "issuer",
                    models.CharField(
                        choices=[
                            ("marion.certificates.issuers.DummyCertificate", "Dummy")
                        ],
                        help_text="The issuer of the certificate among allowed ones",
                        max_length=200,
                        verbose_name="Issuer",
                    ),
                ),
                (
                    "context",
                    models.JSONField(
                        blank=True,
                        editable=False,
                        help_text="Context used to render the certificate's template",
                        null=True,
                        verbose_name="Collected context",
                    ),
                ),
                (
                    "context_query",
                    models.JSONField(
                        help_text="Context will be fetched from those parameters",
                        verbose_name="Context query parameters",
                    ),
                ),
            ],
            options={"ordering": ["-created_on"],},
        ),
    ]
