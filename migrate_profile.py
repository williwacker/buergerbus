#!/usr/bin/env python
# -*- coding: utf-8 -*-


import configparser
import os
import re

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','buergerbus.settings')
django.setup()

from Team.models import Fahrer, Koordinator
from Accounts.models import Profile

class Migrate():

	def __init__(self,model):
		self.migrate_model(model)

	def migrate_model(self,model):
		qs = model.objects.order_by('benutzer').distinct().values_list('benutzer','telefon','mobil')
		for old_item in qs:
			new_item = Profile.objects.filter(user=old_item[0]).first()
			if not new_item:
				new_item = Profile(user=old_item[0], telefon=old_item[1], mobil=old_item[2])
			if not new_item.telefon:
				new_item.telefon = old_item[1]
			if not new_item.mobil:
				new_item.mobil = old_item[2]
			print(new_item.user, new_item.telefon, new_item.mobil)
			new_item.save()

Migrate(Fahrer)
Migrate(Koordinator)
