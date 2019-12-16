from django import forms

from .models import Question, Topic


class TopicAddForm(forms.ModelForm):
	class Meta:
		model = Topic
		fields = ['name', 'sort_order']

class SubmitFAQForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['topic', 'text', 'answer']

class QuestionChangeForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'answer', 'topic', 'status']
