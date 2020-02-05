#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Search the phone book (DasTelefonbuch.de) for the given name / city and return the result as dict

@Werner Kuehn - Use at your own risk
07.11.2019 0.0.1 WK  Initial version

"""

__version__ = '0.0.1'

import logging
import re
import urllib.parse

import certifi
import urllib3

logger = logging.getLogger(__name__)

class Telefonbuch():
	def __init__(self):
		self.http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
		self.transTable = {'zip':'pc', 'na':'na', 'ci':'ci', 'st':'st', 'hn':'hn', 'ph':'ph', 'mph':'mph', 'recuid':'recuid'}

	def dasoertliche(self,name,city,typ):
		lurl = self.http.request('GET', 'https://www.dasoertliche.de/?kgs=07331020&choose=true&page=0&context=0&action=43&buc=22&topKw=0&form_name=search_nat&kw={}&ci={}'.format(name,city))
		line = lurl.data.decode("utf-8","ignore").replace('\t','').replace('\n','').replace('\r','').replace('&nbsp;',' ')
		result = []
		try:
			if line.find('Die Suche wurde automatisch auf') > 0:
				return result
			# list with phone numbers
			itemData    = eval(re.search('itemData\s*=\s*(.*?)]];', line).group(1)+']]')
			# list with address info
			handlerData = eval(re.search('handlerData\s*=\s*(.*?);', line).group(1))
			# item list matching to address list 
			itemList    = re.search('var item = {(.*?)};', line).group(1).split(',')
			for m in range(len(handlerData)):
				data_dict = self._init_dict()
				for singleItem in itemList:
					item = singleItem.split(':',1)
					if item[0].strip() in self.transTable:
						id = self.transTable[item[0].strip()]
						data_dict[id] = eval(item[1])
				phone = itemData[m][10][0].replace('(','').replace(')','-').replace(' ','')
				if phone[:3] in ('015','016','017'):
					data_dict['mph'] = phone
				else:
					data_dict['ph'] = phone
				if data_dict['st'] == '0':
					self.dasoertliche_gewerbe(line, data_dict)
				if data_dict['pc'] and re.match("[\d]5",data_dict['pc']) and data_dict['ci'] and data_dict['st'] and data_dict['hn']:
					result.append(data_dict)
		except:
			pass
		logger.info("{}: {},{},{} Count:{}".format(__name__, name, city, typ, len(result)))
		return result

	def dasoertliche_gewerbe(self, line, data_dict):
		handlerData = re.search('recuid='+data_dict['recuid']+'.*?<address>(.*?)\s+([0-9]+.*?),.*?([\s0-9]+).*?<span.*?>(.*?)</span>', line).group(1,2,3,4)
		data_dict['st'] = handlerData[0]
		data_dict['hn'] = handlerData[1]
		data_dict['pc'] = handlerData[2].strip()
		data_dict['ci'] = handlerData[3]
		return

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
		try:
			if line.find("Wir konnten zu Ihrer Eingabe keine Eintr&auml;ge finden, daher wurde Ihre Suche ge&auml;ndert.") > 0:
				return result
			for m in re.finditer('data-entry-data=\"(.*?)\"', line):
				data = self._split_das_telefonbuch(m.group(1))
				if data != None:
					result.append(data)
		except:
			pass	
		logger.info("{}: {},{},{} Count:{}".format(__name__, name, city, typ, len(result)))
		return result

	def _init_dict(self):
		data_dict = {}
		for key in self.transTable:
			data_dict[self.transTable[key]] = ''
		return data_dict
	
	def _split_das_telefonbuch(self, match):
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
			if data_dict['pc'] and data_dict['ci'] and data_dict['st'] and data_dict['hn']:
				return data_dict
