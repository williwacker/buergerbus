import django_filters

from .models import Question, Topic


class TopicFilter(django_filters.FilterSet):
    class Meta:
        model = Question
        fields = ['topic',]
