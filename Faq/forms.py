from django import forms

from .models import Question, Topic


class TopicAddForm(forms.ModelForm):
	class Meta:
		model = Topic
		fields = ['name', 'sort_order']
		widgets = {'name': forms.TextInput(attrs={'autofocus': True})}

class SubmitFAQForm(forms.ModelForm):
	class Meta:
		model = Question
		fields = ['topic', 'text', 'answer']
		widgets = {'text': forms.TextInput(attrs={'autofocus': True})}

class QuestionChangeForm(forms.ModelForm):
	class Meta:
		model = Question
		fields = ['text', 'answer', 'topic', 'status']

	def __init__(self, *args, **kwargs):
		super(QuestionChangeForm, self).__init__(*args, **kwargs)
