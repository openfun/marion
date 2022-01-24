"""Howard template tags"""
from pathlib import Path

from django import template

register = template.Library()


@register.filter()
def is_path(obj):
    """Check if the provided object is a Path instance."""
    return isinstance(obj, Path)
