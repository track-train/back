from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from src.container import container
from src.adapters.sqlalchemy.repositories.notification import SqlAlchemyNotificationRepository
from src.domain.services.notification import NotificationService

logger = logging.getLogger("apscheduler")

def start_daily_notification_scheduler():
    scheduler = AsyncIOScheduler()
    trigger = CronTrigger(hour=0, minute=0)
    print(f"Daily notification scheduler started 🚀 at {trigger}")

    async def job():
        print("Running daily notification job...")
        try:
            async with container.SessionFactory() as session:
                repo = SqlAlchemyNotificationRepository(session)
                notification_service = NotificationService(repo)
                notifications = await notification_service.create_daily_notifications_for_all_users()
                logger.info(f"[Scheduler] {len(notifications)} daily notifications created successfully")
        except Exception as e:
            logger.error(f"[Scheduler] Error creating daily notifications: {e}")

    scheduler.add_job(job, trigger)
    scheduler.start()