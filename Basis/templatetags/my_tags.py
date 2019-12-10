from django import template
from django.conf import settings

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