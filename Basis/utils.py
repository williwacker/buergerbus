import os
import subprocess
from collections import OrderedDict
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.utils import NestedObjects
from django.contrib.auth.models import Permission, User
from django.contrib.messages.api import get_messages
from django.contrib.messages.constants import DEFAULT_LEVELS
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.template import Context, loader
from django.utils.http import is_safe_url
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from fuzzywuzzy import fuzz, process
from xhtml2pdf import pisa

from Einsatzmittel.models import Buero, Bus
from Einsatzmittel.utils import get_buero_list, get_bus_list
from Faq.utils import get_topic_list


def get_user_permissions(user):
    if user.is_superuser:
        return Permission.objects.all()
    return user.user_permissions.all().values_list(
        'codename', flat=True) | Permission.objects.filter(
        group__user=user).values_list(
        'codename', flat=True)


def get_index_bar(user):
    index_bar = []

    value = []
    if user.has_perm('Klienten.view_klienten'):
        value.append({
            'name':
            'Fahrgast auswählen <img src="/static/project/img/fahrplan.png" style="height: 24px; vertical-align: bottom; padding-left: 10px;">',
            'value': '/Klienten/fahrgaeste/'})
    if user.has_perm('Tour.view_tour'):
        value.append({'name': 'Touren ansehen', 'value': '/Tour/tour/'})
    if value:
        index_bar.append({'name': 'Touren bearbeiten', 'value': value})

    value = []
    if user.has_perm('Klienten.view_klienten'):
        value.append({'name': 'Fahrgäste ansehen', 'value': '/Klienten/fahrgaeste/'})
    if user.has_perm('Klienten.add_klienten'):
        value.append({'name': 'Fahrgast anlegen', 'value': '/Klienten/fahrgaeste/add/'})
    if value:
        index_bar.append({'name': 'Fahrgäste bearbeiten', 'value': value})

    value = []
    if user.has_perm('Klienten.view_klienten'):
        value.append({'name': 'Dienstleister ansehen', 'value': '/Klienten/dienstleister/'})
    if user.has_perm('Klienten.add_klienten'):
        value.append({'name': 'Dienstleister anlegen', 'value': '/Klienten/dienstleister/add/'})
    if value:
        index_bar.append({'name': 'Dienstleister bearbeiten', 'value': value})

    value = []
    if user.has_perm('Einsatztage.view_fahrtag'):
        value.append({'name': 'Fahrplan ansehen und als Email verschicken', 'value': '/Einsatztage/fahrer/'})
    if value:
        index_bar.append({'name': 'Fahrpläne anzeigen', 'value': value})

    value = []
    if user.has_perm('Einsatztage.change_fahrtag'):
        value.append({
            'name':
            'Fahrdienst eintragen <img src="/static/project/img/kalender-plus-32-trans.png" style="height: 24px; vertical-align: bottom; padding-left: 10px;">',
            'value': '/Einsatztage/fahrer/'})
    if user.has_perm('Einsatztage.change_buerotag'):
        value.append({
            'name':
            'Bürodienst eintragen <img src="/static/project/img/kalender-plus-32-trans.png" style="height: 24px; vertical-align: bottom; padding-left: 10px;">',
            'value': '/Einsatztage/buero/'})
    if value:
        index_bar.append({'name': 'Dienstpläne', 'value': value})

    return index_bar


def get_sidebar(user):
    sidebar = []

    value = []
    if user.has_perm('auth.view_user'):
        value.append({'name': 'Benutzer', 'value': '/Basis/benutzer/'})
    if user.has_perm('auth.view_group'):
        value.append({'name': 'Gruppen', 'value': '/Basis/gruppen/'})
    if value:
        sidebar.append({'name': 'Autorisierung', 'value': value})

    value = []
    if user.has_perm('Klienten.view_klienten'):
        value.append({'name': 'Fahrgäste', 'value': '/Klienten/fahrgaeste/'})
        value.append({'name': 'Dienstleister', 'value': '/Klienten/dienstleister/'})
    if user.has_perm('Klienten.view_orte'):
        value.append({'name': 'Orte', 'value': '/Klienten/orte/'})
    if user.has_perm('Klienten.view_strassen'):
        value.append({'name': 'Strassen', 'value': '/Klienten/strassen/'})
    if value:
        sidebar.append({'name': 'Klienten', 'value': value})

    if user.has_perm('Tour.view_tour'):
        sidebar.append({'name': 'Touren', 'value': ({'name': 'Touren', 'value': '/Tour/tour/'},)})

    value = []
    if user.has_perm('Einsatztage.view_fahrtag'):
        value.append({'name': 'Fahrdienste', 'value': '/Einsatztage/fahrer/'})
    if user.has_perm('Einsatztage.view_buerotag'):
        value.append({'name': 'Bürodienste', 'value': '/Einsatztage/buero/'})
    if value:
        sidebar.append({'name': 'Dienstpläne', 'value': value})

    value = []
    if user.has_perm('Team.view_fahrer'):
        value.append({'name': 'Fahrer', 'value': '/Team/fahrer/'})
    if user.has_perm('Team.view_koordinator'):
        value.append({'name': 'Koordinatoren', 'value': '/Team/koordinator/'})
    if value:
        sidebar.append({'name': 'Team', 'value': value})

    value = []
    if user.has_perm('Einsatzmittel.view_bus'):
        value.append({'name': 'Busse', 'value': '/Einsatzmittel/busse/'})
    if user.has_perm('Einsatzmittel.view_buero'):
        value.append({'name': 'Büros', 'value': '/Einsatzmittel/bueros/'})
    if user.has_perm('Einsatzmittel.change_bus'):
        value.append({'name': 'Bus Standorte', 'value': '/Klienten/standorte/'})
    if value:
        sidebar.append({'name': 'Einsatzmittel', 'value': value})

    value = []
    if user.is_superuser:
        value.append({'name': 'Themen', 'value': '/Faq/topics/admin/'})
    if user.has_perm('Faq.change_question'):
        value.append({'name': 'Fragen', 'value': '/Faq/questions/admin/'})
    if value:
        sidebar.append({'name': 'FAQ', 'value': value})

    value = []
    if user.has_perm('Basis.view_document'):
        value.append({'name': 'Einen Kaffee bitte', 'value': '/Basis/coffee/'})
    if user.has_perm('Basis.view_document'):
        value.append({'name': 'Dokumente', 'value': '/Basis/documents/'})
    if list(User.objects.filter(is_superuser=True).values_list('email', flat=True)):
        value.append({'name': 'Lob und Tadel', 'value': '/Basis/feedback/'})
    if user.has_perm('Faq.view_question') and user.has_perm('Faq.view_topic'):
        value.append({'name': 'Fragen und Antworten', 'value': '/Faq/questions/'})
    if value:
        sidebar.append({'name': 'Hilfe', 'value': value})

    value = []
    if user.is_superuser:
        value.append({'name': 'Log Viewer', 'value': '/admin/logtailer/'})
        value.append({'name': 'Web Service neu starten', 'value': '/Basis/restart_apache/'})
    if value:
        sidebar.append({'name': 'Admin', 'value': value})

    return sidebar


def url_args(request):
    args = request.build_absolute_uri().lstrip(request.build_absolute_uri('?'))
    if is_safe_url(args, request.get_host()):
        return args
    return ""


def get_relation_dict(modelclass, kwargs):
    objects = OrderedDict()
    obj = modelclass.objects.get(pk=kwargs['object'].pk)
    collector = NestedObjects(using='default')
    collector.collect([obj])
    for item in collector.data.items():
        objects[item[0].__name__] = item[1]
    return objects


def get_object_filter(viewclass, request):
    filter = {}
    if hasattr(viewclass, 'object_filter'):
        for field, value in viewclass.object_filter:
            filter[field] = eval(value)
    return filter


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


def append_br(message, new_message):
    return message+'<br>'+new_message if len(message) > 0 else new_message


class MyPasswordValidator:
    """
    Validate whether the password is a common password.

    The password is rejected if it occurs in a provided list of passwords,
    which may be gzipped. 
    The password list must be lowercased to match the comparison in validate().
    """
    DEFAULT_PASSWORD_LIST_PATH = Path(__file__).resolve().parent / 'my-passwords.ini'

    def __init__(self, password_list_path=DEFAULT_PASSWORD_LIST_PATH):
        try:
            with open(str(password_list_path)) as f:
                common_passwords_lines = f.read().splitlines()
        except IOError:
            with open(str(password_list_path)) as f:
                common_passwords_lines = f.readlines()

        self.passwords = [p.strip() for p in common_passwords_lines]

    def validate(self, password, user=None):
        if [sub[0] for sub in process.extract(password.lower().strip(), self.passwords, scorer=fuzz.token_set_ratio) if sub[1] >= 85]:
            raise ValidationError(
                _("This password is too common."),
                code='password_too_common',
            )

    def get_help_text(self):
        return _("Your password can't be a commonly used password.")


class TriggerRestartApache():
    def __init__(self):
        self.touch(settings.MEDIA_ROOT, 'trigger_apache_restart')

    def touch(self, fpath, fname):
        fpathname = '/'.join([fpath, fname])
        if os.path.exists(fpathname):
            os.utime(fpathname, None)
        else:
            open(fpathname, 'a').close()


def run_command(command):
    return subprocess.getoutput(command)
