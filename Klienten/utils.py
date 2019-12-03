from django.contrib import messages
from django.conf import settings
import googlemaps

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
			location = self.client.geocode(address)
			return location[0]['geometry']['location']