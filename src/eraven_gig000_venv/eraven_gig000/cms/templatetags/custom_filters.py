# cms/templatetags/custom_filters.py

from django import template
from django.contrib.contenttypes.models import ContentType
from cms.models import Submission, Workshop, Enrollment

register = template.Library()

@register.filter
@register.filter
def has_attended_workshop(user, workshop):
    if not user.is_authenticated:
        return False
    try:
        ct = ContentType.objects.get_for_model(Workshop)
        return Submission.objects.filter(user=user, content_type=ct, object_id=workshop.id).exists()
    except ContentType.DoesNotExist:
        return False

@register.filter
def is_enrolled(user, course):
    return Enrollment.objects.filter(user=user, course=course).exists()
