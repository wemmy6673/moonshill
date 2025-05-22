from .tkq import broker
from services.logging import init_logger
from config.settings import get_settings
from services.emailing.dispatch import EmailService
from schemas.enums import EmailTemplate
from services.campaign_manager import CampaignManager
from taskiq import TaskiqDepends
from routes.deps import get_db
from sqlalchemy.orm import Session
settings = get_settings()
logger = init_logger()

email_service = EmailService()


# Email Service

@broker.task(max_retries=3, retry_delay=10)
async def send_email(email_to: str, email_type: EmailTemplate, email_data: dict):
    await email_service.send_email(email_to, email_type, email_data)


# Shilling Scheduler
@broker.task(schedule=[{"cron": "*/1 * * * *"}])
async def shilling_scheduler(db: Session = TaskiqDepends(get_db)):
    campaign_manager = CampaignManager(db)

    eligible_campaigns = await campaign_manager.process_eligible_campaigns()
    for campaign in eligible_campaigns:
        logger.info(f"Campaign {campaign.campaign_name} ({campaign.id}) is eligible for shilling, queuing task")
        await run_campaign_shilling.kiq(campaign.id)


# Run campaign shilling

@broker.task(max_retries=3, retry_delay=10)
async def run_campaign_shilling(campaign_id: int, db: Session = TaskiqDepends(get_db)):
    campaign_manager = CampaignManager(db)
    await campaign_manager.process_campaign(campaign_id)
