import datetime
import logging

from django_cron import CronJobBase, Schedule

from Einsatztage.utils import (BuerotageSchreiben, FahrplanBackup,
                               FahrtageSchreiben)

logger = logging.getLogger(__name__)

class EinsatztageCronJob(CronJobBase):
    ALLOW_PARALLEL_RUNS = True
    RUN_EVERY_MINS = 720  # every 12h

    schedule = Schedule(run_every_mins = RUN_EVERY_MINS)
    code = __name__

    def do(self):
        FahrtageSchreiben()
        logger.info("{}: Fahrtage updated".format(__name__))
        BuerotageSchreiben()
        logger.info("{}: Buerotage updated".format(__name__))

class BackupCronJob(CronJobBase):
    ALLOW_PARALLEL_RUNS = True
    RUN_AT_TIMES = ['23:00']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = __name__

    def do(self):
        FahrplanBackup()
        logger.info("{}: FahrplanBackup sent".format(__name__))       
