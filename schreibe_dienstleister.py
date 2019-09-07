#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Lese die csv Datei der Dienstleister schreibe sie in die Klienten SQL Tabelle

@Werner Kuehn - Use at your own risk
11,08.2019 WK Initial version

"""

import configparser
import os, re
os.environ.setdefault('DJANGO_SETTINGS_MODULE','buergerbus.settings')

import django
django.setup()

from Klienten.models import Klienten, Orte, Strassen

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
#		o = list(Orte.objects.values_list('ort', flat=True))
		for name, values in csv_dict.items():
			print(name)
			try:
				o = Orte.objects.get(ort=values['Ort'].strip())
			except:
				print('{} hat keinen bekannten Ortsnamen: {}'.format(name,values['Ort']))
				exit()
			print(o)
#			ort_id = Instance(Orte.objects.filter(ort=values['Ort']).values_list('id', flat=True))[0]
			# Strasse und Hausnr aufsplitten
			z = re.match("(.+)\s(\d+-*\d*)$",values['Strasse'])
			[strasse, hausnr] = z.groups()
#			s = list(Strassen.objects.filter(ort=o).values_list('strasse', flat=True))
			try:
				s = Strassen.objects.get(ort=o,strasse=strasse.strip())
#				s.index(strasse)
			except:
				print('{} hat keinen bekannten Strassennamen: {}'.format(name,strasse))
				exit()
#			strassen_id = list(Strassen.objects.filter(ort=o, strasse=strasse).values_list('id', flat=True))[0]
#			name = name.replace(' ',', ',1)			
			print(s)
			k = Klienten(name=name, ort=o, strasse=s, hausnr=hausnr, kategorie=values['Kategorie'], bemerkung=values['Sparte'], dsgvo='99', typ="D", telefon='-'.join([values['Vorwahl'],values['Tel.Nr.']]))
#			k.save()
			
#AddKlienten('Dienstleister.csv')
AddKlienten('Apotheke.csv')
