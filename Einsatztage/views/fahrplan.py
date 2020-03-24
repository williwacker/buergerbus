from django import forms, template
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.http import (FileResponse, Http404, HttpResponse,
                         HttpResponseForbidden, HttpResponseRedirect)
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from trml2pdf import trml2pdf

from Basis.utils import get_sidebar, url_args
from Basis.views import MyDetailView, MyListView, MyUpdateView, MyView
from Einsatzmittel.models import Bus
from Einsatzmittel.utils import get_bus_list
from Klienten.models import Klienten
from Team.models import Fahrer, Koordinator
from Tour.models import Tour

from ..filters import FahrtagFilter
from ..forms import FahrplanEmailForm, FahrtagChgForm
from ..models import Fahrtag
from ..tables import FahrerTable, TourTable
from ..utils import FahrplanBackup

register = template.Library()


class FahrplanView(MyListView):
    permission_required = 'Tour.view_tour'
    success_url = '/Einsatztage/fahrer/'
    model = Tour

    def get_queryset(self):
        return TourTable(Tour.objects.order_by('uhrzeit').filter(datum=self.kwargs['id']))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ft = Fahrtag.objects.filter(pk=self.kwargs['id'])
        context['pre_table'] = FahrerTable(ft)
        context['title'] = 'Fahrplan {} am {}'.format(ft.first().team, ft.first())
        context['back_button'] = ["Zurück", self.success_url+url_args(self.request)]
        return context


class FahrplanAsPDF(MyView):
    permission_required = 'Tour.view_tour'
    success_url = '/Einsatztage/fahrer/'
    model = Tour

    def pdf_render_to_response(self, template_src, context_dict={}, filename=None, prompt=False):
        context_dict['filename'] = filename
        template = get_template(template_src)
        rml = template.render(context_dict)
        return trml2pdf.parseString(rml)

    def get(self, request, id):
        fahrtag_liste = get_object_or_404(Fahrtag, pk=id)
        tour_liste = Tour.objects.order_by('uhrzeit').filter(datum=id)
        context = {'fahrtag_liste': fahrtag_liste, 'tour_liste': tour_liste}
        filename = 'Buergerbus_Fahrplan_{}_{}.pdf'.format(
            str(fahrtag_liste.team).replace(' ', '_'), fahrtag_liste.datum)
        pdf = self.pdf_render_to_response('Einsatztage/tour_as_pdf.rml', context, filename)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            content = "inline; filename='%s'" % (filename)
            filepath = settings.TOUR_PATH + filename
            try:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                f.close()
                response = FileResponse(open(filepath, 'rb'), content_type="application/pdf")
                response["Content-Disposition"] = "filename={}".format(filename)
                return response
            except:
                messages.error(request, 'Dokument <b>'+filename+'</b> ist noch geöffnet.')
            return HttpResponseRedirect(self.success_url+url_args(request))
        return HttpResponse("Kein Dokument vorhanden")


class FahrplanAsCSV(MyView):
    permission_required = 'Tour.view_tour'
    success_url = '/Einsatztage/fahrer/'
    model = Tour

    def get(self, request, id):
        FahrplanBackup().export_as_csv(id)
        return HttpResponseRedirect(self.success_url+url_args(request))


class FahrplanBackupView(MyView):
    permission_required = 'Tour.view_tour'
    success_url = '/Einsatztage/fahrer/'
    model = Tour

    def get(self, request):
        FahrplanBackup().send_backup()
        return HttpResponseRedirect(self.success_url+url_args(request))


class FahrplanEmailView(MyDetailView):
    form_class = FahrplanEmailForm
    permission_required = 'Tour.view_tour'
    success_url = '/Einsatztage/fahrer/'
    model = Tour

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ft = get_object_or_404(Fahrtag, pk=self.kwargs['id'])
        context['fahrtag_liste'] = ft
        context['tour_liste'] = Tour.objects.order_by('uhrzeit').filter(datum=self.kwargs['id'])
        context['title'] = 'Fahrplan {} am {} versenden'.format(ft.team, ft.datum)
        context['submit_button'] = "Senden"
        context['filepath'] = []
        return context

    def get_dsgvo_klienten(self):
        klienten_liste = {}
        for tour in self.context['tour_liste']:
            if tour.klient.dsgvo == '01':
                klienten_liste[tour.klient.name] = tour.klient
        return klienten_liste

    def writeDSGVO(self):
        context = self.get_context_data()
        filepath_liste = []
        if settings.SEND_DSGVO:
            klienten_liste = self.get_dsgvo_klienten()
            klienten_keys = []
            for key in klienten_liste:
                klienten_keys.append(klienten_liste[key].id)
                self.context['klient'] = klienten_liste[key]
                filename = "DSGVO_{}_{}.pdf".format(klienten_liste[key].nachname, klienten_liste[key].vorname)
                pdf = FahrplanAsPDF().pdf_render_to_response('Klienten/dsgvo.rml', context, filename)
                if pdf:
                    response = HttpResponse(pdf, content_type='application/pdf')
                    content = "inline; filename='%s'" % (filename)
                    filepath = settings.DSGVO_PATH + filename
                    filepath_liste.append(filepath)
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    f.close()
            self.request.session['klienten_keys'] = klienten_keys
        return filepath_liste

    def writeFahrplan(self):
        context = self.get_context_data()
        filename = 'Buergerbus_Fahrplan_{}_{}.pdf'.format(
            str(context['fahrtag_liste'].team).replace(' ', '_'),
            context['fahrtag_liste'].datum)
        pdf = FahrplanAsPDF().pdf_render_to_response('Einsatztage/tour_as_pdf.rml', context, filename)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            content = "inline; filename='%s'" % (filename)
            filepath = settings.TOUR_PATH + filename
            try:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                f.close()
            except:
                messages.error(self.request, 'Dokument <b>' + filepath +
                               '</b> ist noch geöffnet und kann nicht geschrieben werden.')
        return [filepath]

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context['filepath'] += self.writeDSGVO()
        context['filepath'] += self.writeFahrplan()
        form = self.form_class()
        form.fields['von'].initial = settings.EMAIL_HOST_USER
        ft = context['fahrtag_liste']
        email_to = []
        if ft.fahrer_vormittag:
            email_to.append(ft.fahrer_vormittag.benutzer.email)
        if ft.fahrer_nachmittag:
            email_to.append(ft.fahrer_nachmittag.benutzer.email)
        if ft.team.email:
            email_to.append(ft.team.email)
        form.fields['an'].initial = "; ".join(email_to)
        form.fields['betreff'].initial = '[Bürgerbus] Fahrplan {} am {}'.format(ft.team, ft.datum)
        form.fields['datei'].initial = '\n'.join(context['filepath'])
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = self.form_class(request.POST)
        context['form'] = form
        if form.is_valid():
            post = form.cleaned_data
            email = EmailMessage(
                post['betreff'],
                post['text'],
                post['von'],
                post['an'].split(";"),
                reply_to=[User.objects.get(username=request.user).email],
            )
            if post['cc']:
                email.cc = list(post['cc'].values_list('email', flat=True))
            for filepath in post['datei'].split('\n'):
                email.attach_file(filepath.strip('\r'))
            email.send(fail_silently=False)
            if settings.SEND_DSGVO:
                # klienten dsgvo auf 'versandt' stellen
                klienten_keys = self.request.session.pop('klienten_keys', [])
                for id in klienten_keys:
                    klient = Klienten.objects.get(id=id)
                    klient.dsgvo = '02'
                    klient.save(force_update=True)
            storage = messages.get_messages(request)
            storage.used = True
            messages.success(request, post['betreff']+' wurde erfolgreich versandt.')
            return HttpResponseRedirect(self.success_url+url_args(request))
        else:
            messages.error(request, form.errors)
        return render(request, self.template_name, context)
