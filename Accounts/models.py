#import datetime
import logging

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

#import os


logger = logging.getLogger(__name__)


class MyUser(User):
    class Meta:
        proxy = True
        verbose_name = 'Benutzer'
        verbose_name_plural = 'Benutzer'

    def __str__(self):
        return ', '.join([self.last_name, self.first_name])

    def user(self):
        return ', '.join([self.last_name, self.first_name])		


class MyGroup(Group):
    class Meta:
        proxy = True
        verbose_name = 'Gruppe'
        verbose_name_plural = 'Gruppen'


class Profile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, verbose_name='Benutzer')
    telefon = models.CharField(max_length=30, blank=True, help_text="01234-1111")
    mobil = models.CharField(max_length=30, blank=True, null=True, help_text="0150-1111")

    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profile'


@receiver(post_save, sender=MyUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=MyUser)
def save_user_profile(sender, instance, **kwargs):
    if not Profile.objects.filter(user=instance).exists():
        Profile.objects.create(user=instance)
    else:
    	instance.profile.save()
