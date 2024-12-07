from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from backend.src.models.event import Event
from backend.src.models.user import User
from backend.src.utils.constants import TIMEZONE
import logging

logger = logging.getLogger("backend")


def cleanup_unactivated_accounts():
    """
    Delete unactivated user accounts that exceed activation time limit.

    This scheduled task runs daily at midnight and performs:
    1. Calculates 48-hour deadline from current time
    2. Finds all unactivated accounts that:
        - Have is_active=False
        - Have a confirmation token (registered but not activated)
        - Token creation time is older than 48 hours
    3. Deletes found accounts to maintain database cleanliness

    Note:
        - Uses UTC time for consistent datetime comparison
        - Performs bulk deletion for efficiency
        - Safe for concurrent execution

    Logs:
        - DEBUG: Start of cleanup process and when no accounts found
        - INFO: Number of accounts deleted if any found
    """
    # Find deadline time (48 hours ago)
    deadline = datetime.utcnow() - timedelta(hours=48)

    # Find and delete unactivated accounts with expired tokens
    logger.debug(f"Starting cleanup of unactivated accounts older than {deadline}")
    # Find accounts that:
    # - Are not active
    # - Have confirmation token (created through registration)
    # - Token is older than 48 hours
    old_unactivated = User.objects(
        is_active=False,
        email_confirmation_token__ne=None,
        email_confirmation_token_created__lte=deadline
    )

    deletion_count = old_unactivated.count()

    if deletion_count:
        old_unactivated.delete()
        logger.info(
            f"Cleaned up {deletion_count} unactivated accounts. "
            f"Deadline was {deadline}"
        )
    else:
        logger.debug("No unactivated accounts to clean up.")


def deactivate_past_events():
    """
    Deactivate events that have already ended.

    This scheduled task runs daily at midnight and performs:
    1. Gets current time in application timezone (Asia/Jerusalem)
    2. Finds all active events where:
        - end_date is in the past
        - is_active is True
    3. Sets their is_active status to False

    Note:
        - Uses configured TIMEZONE from constants
        - Performs bulk update for efficiency
        - Safe for concurrent execution

    Logs:
        - DEBUG: Start of deactivation process
        - INFO: Number of events deactivated if any found
    """
    current_time = datetime.now(TIMEZONE)

    logger.debug(f"Starting deactivation check for past events at {current_time}")
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
        logger.info(
            f"Automatically deactivated {update_count} past events. "
            f"Current time was {current_time}"
        )
    else:
        logger.debug("No past events found for deactivation.")


def init_scheduler(app):
    """
    Initialize and start the application background scheduler.

    Sets up scheduled tasks for automatic maintenance:
    1. Event deactivation - runs daily at midnight
    2. Account cleanup - runs daily at midnight

    Args:
        app: Flask application instance to store scheduler

    Note:
        - Uses BackgroundScheduler for non-blocking execution
        - Tasks run in local timezone (Asia/Jerusalem)
        - Scheduler instance is stored in app context for lifecycle management

    Logs:
        - INFO: Successful scheduler initialization
    """
    scheduler = BackgroundScheduler()

    # Add job to run every day at midnight
    scheduler.add_job(
        deactivate_past_events,
        trigger=CronTrigger(hour=0, minute=0, timezone="Asia/Jerusalem"),
        name="deactivate_past_events",
        id="deactivate_past_events"
    )

    scheduler.start()
    logger.info("Background scheduler started successfully with all maintenance jobs")
    app.scheduler = scheduler  # Store scheduler instance in app context
