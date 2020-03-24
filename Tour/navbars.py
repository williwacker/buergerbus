from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def tour_navbar(nav_bar, datum):
    html = ''
    if nav_bar:
        for i in range(min(8, len(nav_bar))):
            selected = ''
            tag = 'a'
            if datum:
                if int(datum) == nav_bar[i].id:
                    selected = ' selected'
                    tag = 'span'
            html += '<{4} href="?datum={0}" class="changeform-navigation-button segmented-button {3}"><span class="changeform-navigation-button-label">{5} {1} {2}</span></{4}>'.format(
                nav_bar[i].id, nav_bar[i].datum, nav_bar[i].team, selected, tag, nav_bar[i].wochentag)
    return mark_safe(html)
