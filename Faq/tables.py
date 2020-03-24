import django_tables2 as tables

from .models import Question, Topic


class TopicTable(tables.Table):
    name = tables.TemplateColumn(
        template_code='''
            {% if perms.Faq.change_topic %}
                <a href="{{ record.id }}/{{ url_args }}">{{ record.name |safe }}</a>
            {% else %}
                {{ record.name |safe }}
            {% endif %}            
        '''
    )

    class Meta:
        model = Topic
        fields = ('name', 'sort_order')


class QuestionTopicTable(tables.Table):
    name = tables.TemplateColumn(
        template_code='''
            {% if perms.Faq.view_question %}
                <a href="list/?topic={{ record.id }}">{{ record.name |safe }}</a>
            {% else %}
                {{ record.name |safe }}
            {% endif %}            
        '''
    )

    class Meta:
        model = Topic
        fields = ('name',)


class QuestionTable(tables.Table):
    class Meta:
        model = Question
        fields = ('text', 'answer')


class QuestionAdminTable(tables.Table):
    text = tables.TemplateColumn(
        template_code='''
            {% if perms.Faq.change_question %}
                <a href="{{ record.id }}/{{ url_args }}">{{ record.text |safe }}</a>
            {% else %}
                {{ record.text |safe }}
            {% endif %}            
        '''
    )

    class Meta:
        model = Question
        fields = ('text', 'answer', 'topic', 'status', 'created_on', 'created_by', 'updated_on')
