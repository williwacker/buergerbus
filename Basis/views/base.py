import os

from django.conf import settings
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User

from Basis.forms import DocumentAddForm, DocumentChangeForm, FeedbackForm
from Basis.models import Document
from Basis.tables import DocumentTable
from Basis.utils import get_sidebar, url_args
from Basis.views import (MyBaseDetailView, MyDeleteView, MyDetailView,
                         MyListView, MyUpdateView, MyView)

# Documents View

class DocumentListView(MyListView):
	permission_required = 'Basis.view_document'
	model = Document

	def get_queryset(self):
		return(DocumentTable(Document.objects.order_by('document')))

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Dokumente"
		if self.request.user.has_perm('Basis.add_document'):
			context['add'] = "Dokument"
		context['url_args'] = url_args(self.request)
		return context

class DocumentAddView(MyDetailView):
	form_class = DocumentAddForm
	permission_required = 'Basis.add_document'
	template_name = 'Basis/simple_upload.html'
	success_url = '/Basis/documents/'

	def get_context_data(self):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = 'Dokument hinzufügen'
		context['submit_button'] = "Hochladen"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(self.request)
		return context

	def get(self, request, *args, **kwargs):
		context = self.get_context_data()
		form = self.form_class()
		context['form'] = form
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		context = self.get_context_data()
		form = self.form_class(request.POST, request.FILES)
		context['form'] = form
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)			
		return render(request, self.template_name, context)

class DocumentChangeView(MyUpdateView):
	permission_required = 'Basis.change_document'
	form_class = DocumentChangeForm
	model=Document
	success_url = '/Basis/documents/'
	
	def get_context_data(self):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Dokument ändern"
		if self.request.user.has_perm('Basis.delete_document'):
			context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(self.request)
		return context

	def get(self, request, *args, **kwargs):
		context = self.get_context_data()
		instance=Document.objects.get(pk=kwargs['pk'])
		form = self.form_class(instance=instance)
		form.fields["dokument"].initial = instance.document.name
		context['form'] = form
		return render(request, self.template_name, context)

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.save(force_update=True)
		storage = messages.get_messages(self.request)
		storage.used = True
		self.success_url += url_args(self.request)		
		messages.success(self.request, self.model._meta.verbose_name_raw+' "<a href="'+self.success_url+str(instance.id)+'">'+str(instance)+'</a>" wurde erfolgreich geändert.')
		return super(DocumentChangeView, self).form_valid(form) 

class DocumentDeleteView(MyDeleteView):
	permission_required = 'Basis.delete_document'
	model = Document
	success_url = '/Basis/documents/'

	def post(self, request, *args, **kwargs):
		instance = self.model.objects.get(pk=kwargs['pk'])
		messages.success(request, self.model._meta.verbose_name.title()+' "'+str(instance)+'" wurde gelöscht.')
		return self.delete(request, *args, **kwargs)

class DocumentPDFView(MyBaseDetailView):
	permission_required = 'Basis.view_document'
	model = Document

	def get(self, request, *args, **kwargs):
		objkey = self.kwargs.get('pk', None)
		pdf = get_object_or_404(Document, pk=objkey)
		path = pdf.document.file.name
		response = FileResponse(open(path, 'rb'), content_type="application/pdf")
		response["Content-Disposition"] = "filename={}".format(pdf.relative_path)
		return response

# Feedback View

class FeedbackView(MyDetailView):
	form_class = FeedbackForm
	permission_required = 'Tour.view_tour'
	success_url = '/'
	context = {}

	def get_context_data(self):
		self.context['sidebar_liste'] = get_sidebar(self.request.user)
		self.context['title'] = 'Feedback senden'
		self.context['submit_button'] = "Senden"
		self.context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		self.context['url_args'] = url_args(self.request)

	def get(self, request, *args, **kwargs):
		admin_email = list(User.objects.filter(is_superuser=True).values_list('email', flat=True))
		self.get_context_data()
		self.initial['von'] = settings.EMAIL_HOST_USER
		self.initial['an'] = ';'.join(admin_email)
		self.initial['betreff'] = '[Bürgerbus] Feedback '
		form = self.form_class(initial=self.initial)
		self.context['form'] = form
		return render(request, self.template_name, self.context)

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		self.context['form'] = form
		if form.is_valid():
			post = form.cleaned_data
			email = EmailMessage(
				post['betreff'],
				post['text'],
				post['von'],
				post['an'].split(";"),
				reply_to=post['von'].split(";"),
			)
			email.send(fail_silently=False)	
			messages.success(request, post['betreff']+' wurde erfolgreich versandt.')
			return HttpResponseRedirect(self.success_url+url_args(request))
		else:
			messages.error(request, form.errors)			
		return render(request, self.template_name, self.context)	    
