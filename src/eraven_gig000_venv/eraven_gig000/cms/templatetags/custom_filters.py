# cms/templatetags/custom_filters.py

from django import template
from django.contrib.contenttypes.models import ContentType
from cms.models import Submission, Workshop, Enrollment, Assignment, Challenge, Article, Video, Session, Documentation

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

@register.filter
def is_instance(obj, class_name):
    return obj.__class__.__name__ == class_name

@register.simple_tag
def get_detail_url(item):
    if isinstance(item, Assignment):
        return 'cms:assignment_detail'
    elif isinstance(item, Challenge):
        return 'cms:challenge_detail'
    elif isinstance(item, Article):
        return 'cms:article_detail'
    elif isinstance(item, Video):
        return 'cms:video_detail'
    elif isinstance(item, Session): 
        return 'cms:session_detail'
    elif isinstance(item, Documentation):
        return 'cms:documentation_detail'
    return '#'

@register.filter
def icon_for(item):
    icon_map = {
        "Assignment": "fas fa-file-alt",
        "Challenge": "fas fa-trophy",
        "Article": "fas fa-newspaper",
        "Video": "fas fa-video",
        "Workshop": "fas fa-chalkboard-teacher",
        "Session": "fas fa-calendar-alt",
        "Documentation": "fas fa-book",
    }
    return icon_map.get(item.__class__.__name__, "fas fa-info-circle")