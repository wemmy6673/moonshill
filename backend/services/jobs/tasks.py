from app.config.settings import get_settings
from app.utils.logging import init_logger

settings = get_settings()
logger = init_logger()


async def job_ping(ctx):
    logger.info("PING")
    return "PONG"
