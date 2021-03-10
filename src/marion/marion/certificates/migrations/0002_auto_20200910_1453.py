# Generated by Django 3.1 on 2020-09-10 14:53

from django.db import migrations, models

import marion.certificates.models


class Migration(migrations.Migration):

    dependencies = [
        ("certificates", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="certificaterequest",
            name="context",
            field=marion.certificates.models.PydanticModelField(
                blank=True,
                editable=False,
                help_text="Context used to render the certificate's template",
                null=True,
                verbose_name="Collected context",
            ),
        ),
        migrations.AlterField(
            model_name="certificaterequest",
            name="context_query",
            field=marion.certificates.models.PydanticModelField(
                help_text="Context will be fetched from those parameters",
                verbose_name="Context query parameters",
            ),
        ),
        migrations.AlterField(
            model_name="certificaterequest",
            name="issuer",
            field=models.CharField(
                choices=[("howard.issuers.RealisationCertificate", "Realisation")],
                help_text="The issuer of the certificate among allowed ones",
                max_length=200,
                verbose_name="Issuer",
            ),
        ),
    ]
