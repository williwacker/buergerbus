#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Lese die Datei mit den Orts und Strassennamen und schreibe sie in die entsprechenden SQL Tabellen (Orte, Strassen)

@Werner Kuehn - Use at your own risk
19.06.2019 WK Initial version

"""

import configparser
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','buergerbus.settings')

import django
django.setup()

from Klienten.models import Orte, Strassen


def read_names(filename): #read configuration from the configuration file and prepare a preferences dict
	cfg = configparser.ConfigParser()
	cfg.optionxform=str
	cfg.read(filename)
	orte = {}
	Orte.objects.all().delete()
	for ortsname in cfg:
		if (ortsname != 'DEFAULT'):
			strassenname = {}
			print(ortsname)
			o = Orte(ort=ortsname)
			o.save()
			for name, value in cfg.items(ortsname):
				strassenname[name] = value
				print('   '+name)
				s = Strassen(ort=o, strasse=name)
				s.save()
			orte[ortsname] = strassenname
	return orte

read_names('Strassennamen.txt')