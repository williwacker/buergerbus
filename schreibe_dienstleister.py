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
		with open(filename) as f:
			csv_list = [[val.strip() for val in r.split(";")] for r in f.readlines()]

		(_, *header), *data = csv_list
		csv_dict = {}
		for row in data:
			key, *values = row
			csv_dict[key] = {key: value for key, value in zip(header, values)}
		return csv_dict

	def write_clients(self,csv_dict):
		o = list(Orte.objects.values_list('ort', flat=True))
		for name, values in csv_dict.items():
			try:
				o.index(values['Ort'])
			except:
				print('{} hat keinen bekannten Ortsnamen: {}'.format(name,values['Ort']))
				exit()
			ort_id = list(Orte.objects.filter(ort=values['Ort']).values_list('id', flat=True))[0]
			# Strasse und Hausnr aufsplitten
			z = re.match("(.+)\s(\d+-*\d*)$",values['Strasse'])
			[strasse, hausnr] = z.groups()
			s = list(Strassen.objects.filter(ort=ort_id).values_list('strasse', flat=True))
			try:
				s.index(strasse)
			except:
				print('{} hat keinen bekannten Strassennamen: {}'.format(name,strasse))
				exit()
			strassen_id = list(Strassen.objects.filter(ort=ort_id, strasse=strasse).values_list('id', flat=True))[0]
			print(strassen_id)
			name = name.replace(' ',', ',1)
			print(name)
			k = Klienten(name=name, ort=ort_id, strasse=strassen_id, hausnr=hausnr, bemerkung=values['Sparte'], dsgvo='99', typ="D", telefon='-'.join([values['Vorwahl'],values['telefon']]))
			
AddKlienten('Dienstleister.csv')
