from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from backend.src.models.event import Event
from backend.src.utils.constants import TIMEZONE
import logging

logger = logging.getLogger('backend')


def deactivate_past_events():
    """
    Check and deactivate events that have ended.
    Updates is_active status to False for events where:
    - end_date is in the past
    - is_active is currently True
    """
    current_time = datetime.now(TIMEZONE)

    logger.debug("Looking for past events.")
    # Find active events that have ended
    past_events = Event.objects(
        end_date__lt=current_time,
        is_active=True
    )

    # Update their status
    update_count = past_events.update(
        is_active=False
    )

    if update_count:
        logger.info(f"Automatically deactivated {update_count} past events.")


def init_scheduler(app):
    """
    Initialize and start the background scheduler
    """
    scheduler = BackgroundScheduler()

    # Add job to run every day at midnight
    scheduler.add_job(
        deactivate_past_events,
        trigger=CronTrigger(hour=0, minute=0, timezone='Asia/Jerusalem'),
        name='deactivate_past_events',
        id='deactivate_past_events'
    )

    scheduler.start()
    logger.info("Event scheduler started.")
    app.scheduler = scheduler  # Store scheduler instance in app context
