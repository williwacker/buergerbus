from django.conf import settings
from django.core.mail import EmailMessage, get_connection

from Faq.models import Question, Topic
import logging

logger = logging.getLogger(__name__)

class FaqNotification():
	
	def __init__(self):
		self.send_notification()

	def send_notification(self):
		mail_backend = get_connection()
		faq_list = list(Question.objects.filter(status=Question.INACTIVE))
		mail_text = ''
		for faq in faq_list:
			mail_text += 'Q:{}\nA:{}\n\n'.format(faq.text, faq.answer)
		if mail_text:
			message = EmailMessage(
						from_email=settings.EMAIL_HOST_USER,
						to=[settings.EMAIL_HOST_USER,],
						connection=mail_backend,
						subject="[Bürgerbus] Neue FAQ Fragen", 
						body=mail_text,
					)
			message.send()

def get_topic_list(request):
	filterlist = []
	qs = Topic.objects.values_list('id', flat=True)
	for i in qs:
		codename = "Faq.Topic_{}_editieren".format(i)
		if request.user.has_perm(codename): filterlist.append(i)
	return filterlist			