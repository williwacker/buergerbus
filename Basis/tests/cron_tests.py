from django.test import TestCase

from django.core.management import call_command

class CronTestCase(TestCase):

    def test_cron(self):
        call_command('runcrons')