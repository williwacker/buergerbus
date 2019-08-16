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

def get_sidebar():
	return [
		{'name':'Klienten',    'value':({'name':'Fahrgäste','value':'/Klienten/fahrgaeste/'},{'name':'Dienstleister','value':'/Klienten/dienstleister/'})},
		{'name':'Einsatztage', 'value':({'name':'Fahrer','value':'/Einsatztage/fahrer/'},{'name':'Büro','value':'/Einsatztage/buero/'})},
		{'name':'Touren',      'value':({'name':'Touren','value':'/Tour/touren/'},)},
		{'name':'Team',        'value':({'name':'Fahrer','value':'/Team/fahrer/'},{'name':'Büro','value':'/Team/buero/'})},
	]
