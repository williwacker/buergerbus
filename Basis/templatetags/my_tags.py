from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.text import normalize_newlines


register = template.Library()

@register.filter
def verbose_name(obj):
    return obj._meta.verbose_name


@register.filter
def verbose_name_plural(obj):
    return obj._meta.verbose_name_plural

ALLOWABLE_VALUES = ("PORTAL", "WELCOME", "MEDIA_ROOT", "MEDIA_URL")

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