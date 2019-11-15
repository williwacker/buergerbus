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
			data = self._split(m.group(1))
			if data != None:
				result.append(data) 	
		return result
	
	def _split(self, match):
		entry_dict = {}
		for entry in match.split('&'):
			entry_dict.update([tuple(entry.split('=',1))])
		if entry_dict:
			data_dict  = {}
			typ = entry_dict.get('at','2')
			na = urllib.parse.unquote(entry_dict.get('na',''))
			data_dict['na']  = na.replace('+',', ',1).replace('+',' ') if typ == '1' else na.replace('+',' ')
			data_dict['st']  = urllib.parse.unquote(entry_dict.get('st','')).replace('+',' ')
			data_dict['ci']  = urllib.parse.unquote(entry_dict.get('ci','')).replace('+',' ')
			data_dict['pc']  = entry_dict.get('pc','')
			data_dict['ph']  = entry_dict.get('ph','').replace('+','-',1).replace('+','')
			data_dict['mph'] = entry_dict.get('mph','').replace('+','-',1).replace('+','')
			data_dict['hn']  = entry_dict.get('hn','').replace('+','')
			# ignore entries without street name or zip
			if data_dict['pc'] and data_dict['st']:
				return data_dict

