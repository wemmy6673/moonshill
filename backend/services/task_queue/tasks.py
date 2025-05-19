from .tkq import broker
from services.logging import init_logger
from config.settings import get_settings
from services.emailing.dispatch import EmailService
from schemas.enums import EmailTemplate

settings = get_settings()
logger = init_logger()

email_service = EmailService()


@broker.task(max_retries=3, retry_delay=10)
async def send_email(email_to: str, email_type: EmailTemplate, email_data: dict):
    await email_service.send_email(email_to, email_type, email_data)
