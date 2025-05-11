from arq.connections import RedisSettings
from arq import create_pool, cron
from app.core.database import SessionLocal
from app.utils.helpers import get_redis_instance
from app.config.settings import get_settings
from app.config.constants import REDIS_SETTINGS
from .tasks import job_ping

settings = get_settings()


async def startup(ctx):
    ctx["arq"] = await create_pool(REDIS_SETTINGS)
    ctx["db"] = SessionLocal()
    ctx["redis"] = get_redis_instance()


async def shutdown(ctx):
    ctx["db"].close()
    ctx["redis"].close()
    await ctx["arq"].aclose()


class WorkerSettings:
    functions = [
        job_ping
    ]

    cron_jobs = [



    ]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = REDIS_SETTINGS
