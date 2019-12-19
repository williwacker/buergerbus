import datetime
import logging

from django_cron import CronJobBase, Schedule

from Einsatztage.utils import (BuerotageSchreiben, FahrplanBackup,
                               FahrtageSchreiben)

logger = logging.getLogger(__name__)

class EinsatztageCronJob(CronJobBase):
    ALLOW_PARALLEL_RUNS = True
    RUN_AT_TIMES = ['01:00']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = __name__

    def do(self):
        FahrtageSchreiben()
        logger.info("{}: Fahrtage updated".format(__name__))
        BuerotageSchreiben()
        logger.info("{}: Buerotage updated".format(__name__))

class BackupCronJob(CronJobBase):
    ALLOW_PARALLEL_RUNS = True
    RUN_AT_TIMES = ['02:00']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = __name__

    def do(self):
        FahrplanBackup()
        logger.info("FahrplanBackup sent")
        FaqNotification()
        logger.info("FaqNotification sent")
