from django import template
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()

@register.filter
def tour_navbar(nav_bar, datum):
	html = ''
	if nav_bar:
#        if len(nav_bar) < 9:
		for i in range(min(8, len(nav_bar))):
			selected = ''
			tag = 'a'
			if datum:
				if int(datum) == nav_bar[i].id:
					selected = ' selected'
					tag = 'span'
			html += '<{4} href="?datum={0}" class="changeform-navigation-button segmented-button {3}"><span class="changeform-navigation-button-label">{1} {2}</span></{4}>'.format(nav_bar[i].id,nav_bar[i].datum,nav_bar[i].team,selected,tag)
	'''
		else:
			for i in range(len(nav_bar)):
				nav1 = None
				nav2 = None
				nav3 = None
				if datum == None:
					nav1 = nav_bar[0]
					if i+2 <= len(nav_bar):
						nav3 = nav_bar[i+1]
					break
				if nav_bar[i].id == int(datum):
					if i > 0:
						nav1 = nav_bar[i-1]
					nav2 = nav_bar[i]
					if i+2 <= len(nav_bar):
						nav3 = nav_bar[i+1]
					break
	
			if nav1:
				html += '<a href="?datum={0}" class="changeform-navigation-button left segmented-button"><span class="changeform-navigation-button-icon left icon-arrow-left"></span><span class="changeform-navigation-button-label">{1} {2}</span></a>'.format(nav1.id,nav1.datum,nav1.team)
			else:
				html += '<a class="changeform-navigation-button segmented-button left disabled"><span class="changeform-navigation-button-icon left icon-arrow-left"></span><span class="changeform-navigation-button-label">-</span></a>'
			if nav2:
				html += '<span class="changeform-navigation-button segmented-button selected"><span class="changeform-navigation-button-icon"></span><span class="changeform-navigation-button-label">{1} {2}</span></span>'.format(nav2.id,nav2.datum,nav2.team)
			if nav3:
				html += '<a href="?datum={0}" class="changeform-navigation-button right segmented-button"><span class="changeform-navigation-button-icon right icon-arrow-right"></span><span class="changeform-navigation-button-label">{1} {2}</span></a>'.format(nav3.id,nav3.datum,nav3.team)
			else:
				html += '<a class="changeform-navigation-button segmented-button right disabled"><span class="changeform-navigation-button-icon right icon-arrow-right"></span><span class="changeform-navigation-button-label">-</span></a>'
	'''         
	return mark_safe(html)