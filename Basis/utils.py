from django.contrib.auth.models import Permission
from Einsatzmittel.models import Bus, Buero
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO

def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None

def get_user_permissions(user):
	if user.is_superuser:
		return Permission.objects.all()
	return user.user_permissions.all().values_list('codename', flat=True) | Permission.objects.filter(group__user=user).values_list('codename', flat=True)

def has_perm(user, codename):
	if user.is_superuser:
		return True
	if user.has_perm(codename):
		return True
	if Permission.objects.filter(group__user=user, codename=codename):
		return True
	return False

def get_sidebar(user):
	sidebar = []
	if user.has_perm('auth.view_user') or user.has_perm('auth.view_group'):
		value = []
		if user.has_perm('auth.view_user'):
			value.append({'name':'Benutzer','value':'/admin/auth/user/'})
		if user.has_perm('auth.view_group'):
			value.append({'name':'Gruppen','value':'/admin/auth/group/'})
		sidebar.append({'name':'Autorisierung', 'value':value})	
	
	if user.has_perm('Klienten.view_klient') or user.has_perm('Klienten.view_orte') or user.has_perm('Klienten.view_strassen'):
		value = []
		if user.has_perm('Klienten.view_klient'):
			value.append({'name':'Fahrgäste','value':'/Klienten/fahrgaeste/'})
			value.append({'name':'Dienstleister','value':'/Klienten/dienstleister/'})
		if user.has_perm('Klienten.view_orte'):
			value.append({'name':'Orte','value':'/Klienten/orte/'})
		if user.has_perm('Klienten.view_strassen'):
			value.append({'name':'Strassen','value':'/Klienten/strassen/'})
		sidebar.append({'name':'Klienten', 'value':value})
	
	if user.has_perm('Einsatztage.view_bus') or user.has_perm('Einsatztage.view_buero'):
		value = []
		if user.has_perm('Einsatztage.view_bus'):
			value.append({'name':'Fahrer','value':'/Einsatztage/fahrer/'})
		if user.has_perm('Einsatztage.view_buero'):
			value.append({'name':'Büro','value':'/Einsatztage/buero/'})
		sidebar.append({'name':'Einsatztage', 'value':value})
	
	if user.has_perm('Tour.view_tour'):
		sidebar.append({'name':'Touren', 'value':({'name':'Touren','value':'/Tour/touren/'},)})
	
	if user.has_perm('Team.view_fahrer') or user.has_perm('Team.view_buero'):
		value = []
		if user.has_perm('Team.view_fahrer'):
			value.append({'name':'Fahrer','value':'/Team/fahrer/'})
		if user.has_perm('Team.view_buero'):
			value.append({'name':'Büro','value':'/Team/buero/'})
		sidebar.append({'name':'Team', 'value':value})
	return sidebar
