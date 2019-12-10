from django.contrib.auth.models import Permission
from Einsatzmittel.models import Bus, Buero
from django.template import loader, Context
from django.http import HttpResponse
from django.utils.http import is_safe_url
from django.contrib import messages
from django.contrib.auth.models import User
from xhtml2pdf import pisa
from io import BytesIO
from django.db.models.deletion import Collector
from collections import OrderedDict
from django.contrib.messages.api import get_messages
from django.contrib.messages.constants import DEFAULT_LEVELS

def render_to_pdf(template_src, context_dict={}):
	template = loader.get_template(template_src)
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

def get_sidebar(user):
	sidebar = []

	value = []
	if user.has_perm('auth.view_user'):
		value.append({'name':'Benutzer','value':'/Basis/benutzer/'})
	if user.has_perm('auth.view_group'):
		value.append({'name':'Gruppen','value':'/Basis/gruppen/'})
	if value:
		sidebar.append({'name':'Autorisierung', 'value':value})	
	
	value = []
	if user.has_perm('Klienten.view_klienten'):
		value.append({'name':'Fahrgäste','value':'/Klienten/fahrgaeste/'})
		value.append({'name':'Dienstleister','value':'/Klienten/dienstleister/'})
	if user.has_perm('Klienten.view_orte'):
		value.append({'name':'Orte','value':'/Klienten/orte/'})
	if user.has_perm('Klienten.view_strassen'):
		value.append({'name':'Strassen','value':'/Klienten/strassen/'})
	if value:
		sidebar.append({'name':'Klienten', 'value':value})	
	
	if user.has_perm('Tour.view_tour'):
		sidebar.append({'name':'Touren', 'value':({'name':'Touren','value':'/Tour/tour/'},)})

	value = []
	if user.has_perm('Einsatztage.view_fahrtag'):
		value.append({'name':'Fahrtage','value':'/Einsatztage/fahrer/'})
	if user.has_perm('Einsatztage.view_buerotag'):
		value.append({'name':'Bürotage','value':'/Einsatztage/buero/'})
	if value:
		sidebar.append({'name':'Einsatztage', 'value':value})	

	value = []
	if user.has_perm('Team.view_fahrer'):
		value.append({'name':'Fahrer','value':'/Team/fahrer/'})
	if user.has_perm('Team.view_koordinator'):
		value.append({'name':'Koordinatoren','value':'/Team/koordinator/'})
	if value:
		sidebar.append({'name':'Team', 'value':value})
		
	value = []
	if user.has_perm('Einsatzmittel.view_bus'):
		value.append({'name':'Busse','value':'/Einsatzmittel/busse/'})
	if user.has_perm('Einsatzmittel.view_buero'):
		value.append({'name':'Büros','value':'/Einsatzmittel/bueros/'})
	if value:
		sidebar.append({'name':'Einsatzmittel', 'value':value})

	value = []
	if user.has_perm('Basis.view_document'):
		value.append({'name':'Dokumente','value':'/Basis/documents/'})
	if list(User.objects.filter(is_superuser=True).values_list('email', flat=True)):
		value.append({'name':'Feedback','value':'/Basis/feedback/'})
	if value:
		sidebar.append({'name':'Hilfe', 'value':value})		
	return sidebar

def url_args(request):
	args = request.build_absolute_uri().lstrip(request.build_absolute_uri('?'))
	if is_safe_url(args,request.get_host()):
		return args
	return ""

def get_relation_dict(modelclass, kwargs):
		objects = OrderedDict()
		obj = modelclass.objects.get(pk=kwargs['object'].pk)
		collector = Collector(using='default')
		collector.collect([obj])
		for item in collector.data.items():
			objects[item[0].__name__] = item[1]
		return objects

def messages(request):
    # Remove duplicate messages
    messages = []
    unique_messages = []
    for m in get_messages(request):
        if m.message not in messages:
            messages.append(m.message)
            unique_messages.append(m)

    return {
		'messages': unique_messages,
        'DEFAULT_MESSAGE_LEVELS': DEFAULT_LEVELS,
	}		