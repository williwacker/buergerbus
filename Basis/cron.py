import datetime
import logging

from django_cron import CronJobBase, Schedule

from Einsatztage.utils import (BuerotageSchreiben, FahrplanBackup,
                               FahrtageSchreiben)

logger = logging.getLogger(__name__)

class EinsatztageCronJob(CronJobBase):
    RUN_EVERY_MINS = 720  # every 12h

    schedule = Schedule(run_every_mins = RUN_EVERY_MINS)
    code = __name__

    def do(self):
        FahrtageSchreiben()
        logger.info("{}: Fahrtage updated".format(__name__))
        BuerotageSchreiben()
        logger.info("{}: Buerotage updated".format(__name__))

class BackupCronJob(CronJobBase):
    RUN_EVERY_MINS = 1440  # every 24h

    schedule = Schedule(run_every_mins = RUN_EVERY_MINS)
    code = __name__

    def do(self):
        FahrplanBackup()
        logger.info("{}: FahrplanBackup sent".format(__name__))       
