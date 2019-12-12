#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Lese die csv Datei der Dienstleister schreibe sie in die Klienten SQL Tabelle

@Werner Kuehn - Use at your own risk
11,08.2019 WK Initial version

"""

import configparser
import os
import re

import django

from Klienten.models import Klienten, Orte, Strassen
from Klienten.utils import GeoLocation

os.environ.setdefault('DJANGO_SETTINGS_MODULE','buergerbus.settings')

django.setup()


class AddKlienten():

	def __init__(self,filename):
		self.write_clients(self.read_csv(filename))

	def read_csv(self,filename):
		with open(filename, encoding='utf-8') as f:
			csv_list = [[val.strip() for val in r.split(";")] for r in f.readlines()]

		(_, *header), *data = csv_list
		csv_dict = {}
		for row in data:
			key, *values = row
			csv_dict[key] = {key: value for key, value in zip(header, values)}
		return csv_dict

	def write_clients(self,csv_dict):
		for name, values in csv_dict.items():
			print(name)
			try:
				o = Orte.objects.get(ort=values['Ort'].strip())
			except:
				print('{} hat keinen bekannten Ortsnamen: {}'.format(name,values['Ort']))
				exit()
			print(o)
			# Strasse und Hausnr aufsplitten
			z = re.match("(.+)\s(\d+-*\d*)$",values['Strasse'])
			[strasse, hausnr] = z.groups()
			try:
				s = Strassen.objects.get(ort=o,strasse=strasse.strip())
			except:
				print('{} hat keinen bekannten Strassennamen: {}'.format(name,strasse))
				exit()
			print(s)

			instance = Klienten(name=name, ort=o, strasse=s, hausnr=hausnr, kategorie=values['Kategorie'], bemerkung=values['Sparte'], dsgvo='99', typ="D", telefon='-'.join([values['Vorwahl'],values['Tel.Nr.']]))
			GeoLocation().getLocation(instance)
			instance.save()

AddKlienten('Friseur.csv')
AddKlienten('Apotheke.csv')
