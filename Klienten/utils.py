import logging

import googlemaps
from django.conf import settings
from django.contrib import messages

logger = logging.getLogger(__name__)


class GeoLocation():

    def __init__(self):
        self.setUp()

    def setUp(self):
        self.key = settings.GOOGLEMAPS_KEY
        self.client = googlemaps.Client(self.key)

    def getLocation(self, instance):
        if settings.USE_GOOGLE:
            address = ' '.join([instance.strasse.strasse, str(instance.hausnr),
                                str(instance.ort.plz), instance.ort.ort])
            logger.info("{} {}".format(instance.name, address))
            location = self.client.geocode(address)
            instance.longitude = location[0]['geometry']['location']['lng']
            instance.latitude = location[0]['geometry']['location']['lat']
