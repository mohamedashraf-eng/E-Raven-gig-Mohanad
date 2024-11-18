# ums/templatetags/form_filters.py
from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter(name='dict_key')
def dict_key(value, key):
    """
    Custom filter to get value from dictionary by key
    """
    return value.get(key)