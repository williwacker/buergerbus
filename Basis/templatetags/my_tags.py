from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.text import normalize_newlines

register = template.Library()

ALLOWABLE_VALUES = ("PORTAL", "MEDIA_ROOT", "MEDIA_URL", "COMMUNITY_SUBDIR")


@register.filter
def verbose_name(obj):
    return obj._meta.verbose_name


@register.filter
def verbose_name_plural(obj):
    return obj._meta.verbose_name_plural


@register.filter
def in_list(value, the_list):
    value = str(value)
    return value in the_list.split(',')


@register.filter
def to_str(value):
    """converts int to string"""
    return str(value)

# settings value
@register.simple_tag
def settings_value(name):
    if name in ALLOWABLE_VALUES:
        return getattr(settings, name, '')
    return ''


@register.filter()
@stringfilter
def linebreaksrml(value, autoescape=None):
    """
    Converts all newlines in a piece of plain text to XML line breaks
    (``<text:line-break />``).
    """
    autoescape = autoescape and not isinstance(value, SafeData)
    value = normalize_newlines(value)
    if autoescape:
        value = escape(value)
    return mark_safe(value.replace('\n', '<br/>'))
