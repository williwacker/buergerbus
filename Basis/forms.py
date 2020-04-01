from django import forms
from django.forms import ModelForm
from django.shortcuts import render

from Basis.models import Document


class FeedbackForm(forms.Form):
    an = forms.CharField(required=False, label='An', widget=forms.HiddenInput(
        attrs={'readonly': 'readonly', 'style': 'width:800px;'}))
    betreff = forms.CharField(max_length=50, required=True, label='Betreff',
                              widget=forms.TextInput(attrs={'style': 'width:800px;'}))
    text = forms.CharField(max_length=400, required=False, label='Text', widget=forms.Textarea(
        attrs={'style': 'width:800px;', 'autofocus': True}))


class DocumentAddForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ('description', 'document')
        widgets = {'description': forms.TextInput(attrs={'autofocus': True})}

    def __init__(self, *args, **kwargs):
        super(DocumentAddForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = self.cleaned_data['document']
        if data.name[-4:].upper() != '.PDF':
            raise forms.ValidationError("Nur PDF Dokumente erlaubt")


class DocumentChangeForm(forms.ModelForm):
    document_ro = forms.CharField(required=False, label='Dokument', widget=forms.TextInput(
        attrs={'readonly': 'readonly', 'style': 'width:800px;'}))

    class Meta:
        model = Document
        fields = ('description', 'document_ro', )

    def __init__(self, *args, **kwargs):
        super(DocumentChangeForm, self).__init__(*args, **kwargs)
