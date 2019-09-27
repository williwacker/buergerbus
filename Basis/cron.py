import datetime
from django_cron import CronJobBase, Schedule
from Einsatztage.utils import FahrtageSchreiben, BuerotageSchreiben

class EinsatztageCronJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins = RUN_EVERY_MINS)
    code = 'Basis.cron.EinsatztageCronJob'

    def do(self):
        print('EinsatztageCronJob')
        FahrtageSchreiben(None)
        print('Fahrtage updated '+str(datetime.datetime.today()))
        BuerotageSchreiben(None)
        print('Buerotage updated '+str(datetime.datetime.today()))