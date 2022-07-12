"""Pylint init hook for Django-configurations.

Taken from:
https://github.com/PyCQA/pylint-django/issues/306#issuecomment-859515591
"""
import os


def _configure_pylint_django():
    os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
    os.environ["DJANGO_CONFIGURATION"] = "Development"

    from configurations import importer  # noqa

    importer.install()


if __name__ == "<run_path>":
    _configure_pylint_django()
