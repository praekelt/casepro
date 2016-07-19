from __future__ import unicode_literals

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def squash_counts():
    """
    Task to squash all daily counts
    """
    from .models import TotalCount, DailyCount

    TotalCount.squash()
    DailyCount.squash()


@shared_task
def daily_count_export(export_id):
    from .models import DailyCountExport

    logger.info("Starting daily count export #%d..." % export_id)

    DailyCountExport.objects.get(pk=export_id).do_export()