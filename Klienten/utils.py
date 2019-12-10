from django.contrib import messages
from django.conf import settings
import googlemaps
import logging

logger = logging.getLogger(__name__)

'''
def del_message(request):
	storage = messages.get_messages(request)
	for _ in storage:
		pass
	if len(storage._loaded_messages)  == 1:
		del storage._loaded_messages[0]
'''

class GeoLocation():

	def __init__(self):
		self.setUp()

	def setUp(self):
		self.key = settings.GOOGLEMAPS_KEY
		self.client = googlemaps.Client(self.key)

	def getLocation(self, instance):
		if settings.USE_GOOGLE:
			address = ' '.join([instance.strasse.strasse, instance.hausnr, instance.ort.plz, instance.ort.ort])
			logger.info("{}: {} {}".format(__name__, instance.name, address))
			location = self.client.geocode(address)
			instance.longitude=location[0]['geometry']['location']['lng']
			instance.latitude =location[0]['geometry']['location']['lat']