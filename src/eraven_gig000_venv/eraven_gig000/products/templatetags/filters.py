from django import template

register = template.Library()

@register.filter
def split_filter(value, delimiter=","):
    """
    Splits the input string by the given delimiter.
    """
    if not isinstance(value, str):
        return []
    return value.split(delimiter)
