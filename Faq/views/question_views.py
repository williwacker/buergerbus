from django.contrib import messages
from django.db.models import Max
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from Basis.utils import get_sidebar, url_args
from Basis.views import (MyCreateView, MyDeleteView, MyDetailView, MyListView,
                         MyUpdateView, MyView)

from ..filters import TopicFilter
from ..forms import QuestionChangeForm, SubmitFAQForm, TopicAddForm
from ..models import Question, Topic
from ..tables import QuestionAdminTable, QuestionTable, QuestionTopicTable
from ..utils import get_topic_list


class QuestionTopicView(MyListView):
	model = Topic
	permission_required = 'Faq.view_topic'
	allow_empty = True

	def get_queryset(self):
		qs = Topic.objects.all()
		table = QuestionTopicTable(qs)
		table.paginate(page=self.request.GET.get("page", 1), per_page=18)
		return table

	def get_context_data(self, **kwargs):
		context = super(QuestionTopicView, self).get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = self.model._meta.verbose_name_raw+' - Themen'
		context['url_args'] = url_args(self.request)
		return context

class QuestionListView(MyListView):
	model = Question
	permission_required = 'Faq.view_question'

	def get_queryset(self):
		topic = self.request.GET.get('topic')
		if topic:
			qs = Question.objects.active().filter(topic_id=topic).order_by('-created_on')
		else:
			qs = Question.objects.active().order_by('-created_on')
		table = QuestionTable(qs)
		table.paginate(page=self.request.GET.get("page", 1), per_page=17)
		return table

	def get_context_data(self, **kwargs):
		context = super(QuestionListView, self).get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = "Fragen und Antworten"
		if self.request.user.has_perm('Faq.add_question'): context['add'] = "Frage"
		context['filter'] = TopicFilter()
		topic = self.request.GET.get('topic')
		if topic:
			top = Topic.objects.get(id=topic)
			context['table_header'] = '<p>'+top.name+'</p>'
		context['url_args'] = url_args(self.request)
		return context

class QuestionAddView(MyCreateView):
	form_class = SubmitFAQForm
	permission_required = 'Faq.add_question'
	success_url = '/Faq/questions/list/'
	model = Question

	def get_context_data(self, **kwargs):
		context = {}
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = self.model._meta.verbose_name_raw+" - Frage hinzufügen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		return context

	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		topic = self.request.GET.get('topic')
		self.initial['topic'] = Topic.objects.filter(pk=topic).first() if topic else None
		form = self.form_class(initial=self.initial)
		context['form'] = form
		return render(request, self.template_name, context)

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.created_by = self.request.user
		instance.save()
		self.success_message = 'Vielen Dank. Ihre Frage wurde erfolgreich hinzugefügt und wird nach der Überprüfung durch den Administrator veröffentlicht.'
		self.success_url += url_args(self.request)
		return super(QuestionAddView, self).form_valid(form)

###
### Admin Views
###

class QuestionAdminListView(MyListView):
	model = Question
	permission_required = 'Faq.view_question'

	def get_queryset(self):
		qs = Question.objects.all().order_by('status','-created_on').filter(topic__in=get_topic_list(self.request))
		return QuestionAdminTable(qs)

	def get_context_data(self, **kwargs):
		context = super(QuestionAdminListView, self).get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = self.model._meta.verbose_name_raw
		if self.request.user.has_perm('Faq.add_question'): context['add'] = "Frage"
		context['url_args'] = url_args(self.request)
		return context

class QuestionAdminChangeView(MyUpdateView):
	permission_required = 'Faq.change_question'
	form_class = QuestionChangeForm
	success_url = '/Faq/questions/admin/'
	model = Question

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['sidebar_liste'] = get_sidebar(self.request.user)
		context['title'] = self.model._meta.verbose_name_raw+" - Frage ändern"
		if self.request.user.has_perm('Faq.delete_question'): context['delete_button'] = "Löschen"
		context['submit_button'] = "Sichern"
		context['back_button'] = ["Abbrechen",self.success_url+url_args(self.request)]
		context['url_args'] = url_args(self.request)
		return context

	def form_valid(self, form):
		instance = form.save(commit=False)
		instance.updated_by = self.request.user
		instance.save(force_update=True)
		self.success_url += url_args(self.request)
		messages.success(self.request, self.model._meta.verbose_name_raw+' "<a href="'+self.success_url+str(instance.id)+'">'+str(instance)+'</a>" wurde erfolgreich geändert.')
		return super(QuestionAdminChangeView, self).form_valid(form)

class QuestionAdminDeleteView(MyDeleteView):
	permission_required = 'Faq.delete_topic'
	success_url = '/Faq/questions/admin/'
	model = Question
	pass
