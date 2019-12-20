import datetime
import logging

from django_cron import CronJobBase, Schedule

from Einsatztage.utils import (BuerotageSchreiben, FahrplanBackup,
                               FahrtageSchreiben)
from Faq.utils import FaqNotification
from Tour.utils import TourArchive

logger = logging.getLogger(__name__)

class EinsatztageCronJob(CronJobBase):
    ALLOW_PARALLEL_RUNS = True
    RUN_AT_TIMES = ['01:00']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = __name__

    def do(self):
        FahrtageSchreiben()
        logger.info("Fahrtage updated")
        BuerotageSchreiben()
        logger.info("Buerotage updated")
        TourArchive()
        logger.info("Touren archiviert")

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
