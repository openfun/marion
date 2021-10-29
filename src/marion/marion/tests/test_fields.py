"""Tests for the marion application fields"""

from marion.defaults import DocumentIssuerChoices

from ..fields import IssuerLazyChoiceField, LazyChoiceField


def test_fields_lazy_choice_field():
    """
    LazyChoiceField class.
    Choices instance attribute should not be customizable.
    """
    field = LazyChoiceField(
        name="lazy_choice_field",
        choices=[("option1", "Option 1"), ("option2", "Option 2")],
        max_length=200,
    )

    errors = field.check()
    assert len(errors) == 0

    assert field.choices == []


def test_fields_issuer_lazy_choice_field(settings):
    """
    IssuerLazyChoiceField class.
    Choices attribute relies on DOCUMENT_ISSUER_CHOICES_CLASS setting.
    """
    settings.MARION_DOCUMENT_ISSUER_CHOICES_CLASS = (
        "marion.defaults.DocumentIssuerChoices"
    )
    field = IssuerLazyChoiceField(name="issuer_lazy_choice_field")

    assert field.choices == DocumentIssuerChoices.choices
