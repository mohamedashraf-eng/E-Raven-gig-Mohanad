from django import template
from cms.models import Enrollment

register = template.Library()

@register.filter
def is_enrolled(user, course):
    return Enrollment.objects.filter(user=user, course=course).exists()
