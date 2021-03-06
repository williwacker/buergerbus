#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Lese die Datei mit den Orts und Strassennamen und schreibe sie in die entsprechenden SQL Tabellen (Orte, Strassen)

@Werner Kuehn - Use at your own risk
19.06.2019 WK Initial version

"""

import configparser
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','buergerbus.settings')
django.setup()

from Einsatzmittel.models import Bus
from Klienten.models import Orte, Strassen

class ReadNames():
	def __init__(self,filename):
		self.read_names(filename)

	def read_names(self,filename): #read configuration from the configuration file and prepare a preferences dict
		cfg = configparser.ConfigParser()
		cfg.optionxform=str
		cfg.read(filename, encoding='utf-8')
	#	Orte.objects.all().delete()
		for ortsname in cfg:
			if (ortsname != 'DEFAULT'):
				strassenname = {}
				[ort,plz_bus] = ortsname.split("=")
				[plz,bus] = plz_bus.split(",")
				print(ort, plz, bus)

				# if ort already exists then update, else create
				try:
					o = Orte.objects.get(ort=ort.strip())
				except:
					o = Orte(ort=ort.strip())
				if (plz.strip() != ""):
					o.plz = plz.strip()
				else:
					o.plz = None				
				if (bus.strip() != ""):
					o.bus = Bus.objects.get(bus=bus.strip())
				else:
					o.bus = None
				o.save()
				for name, value in cfg.items(ortsname):
					strassenname[name] = value
					print('    ',name)
					try:
						s = Strassen.objects.get(ort=o, strasse=name.strip())
					except:
						s = Strassen(ort=o, strasse=name.strip(), )
					s.save()
		return

ReadNames('Strassennamen.txt')
