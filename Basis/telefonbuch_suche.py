#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Search the phone book (DasTelefonbuch.de) for the given name / city and return the result as dict

@Werner Kuehn - Use at your own risk
07.11.2019 0.0.1 WK  Initial version

"""

__version__ = '0.0.1'

import urllib3
import urllib.parse
import certifi
import re

class Telefonbuch():
	def __init__(self):
		self.http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())

	def dastelefonbuch(self,name,city,typ):
		searchArg = 'Suche'
		if typ and len(typ) == 1:
			if typ == 'F':
				searchArg = 'Personen'
			elif typ == 'D':
				searchArg = 'Firmen'

		lurl = self.http.request('GET', 'https://www.dastelefonbuch.de/{}/{}/{}'.format(searchArg,name,city))
		line = lurl.data.decode("utf-8","ignore")
		result = []
		for m in re.finditer('data-entry-data=\"(.*?)\"', line):
			data_dict = {}
			data = urllib.parse.unquote(m.group(1))
			entry_dict = {}
			for entry in data.split('&'):
				entry_dict.update([tuple(entry.split('='))])
			if entry_dict:
				data_dict['na'] = ''
				if 'na' in entry_dict:
					data_dict['na'] = entry_dict['na'].replace('+',', ',1).replace('+',' ')
				data_dict['st'] = ''
				if 'st' in entry_dict:
					data_dict['st'] = entry_dict['st'].replace('+',' ')
				data_dict['ci'] = ''
				if 'ci' in entry_dict:
					data_dict['ci'] = entry_dict['ci'].replace('+',' ')
				data_dict['ph'] = ''
				if 'ph' in entry_dict:
					data_dict['ph'] = entry_dict['ph'].replace('+','-',1).replace('+','')
				data_dict['mph'] = ''
				if 'mph' in entry_dict:
					data_dict['mph'] = entry_dict['mph'].replace('+','-',1).replace('+','')
				data_dict['hn'] = ''
				if 'hn' in entry_dict:
					data_dict['hn'] = entry_dict['hn'].replace('+','')								
				result.append(data_dict)
		return result