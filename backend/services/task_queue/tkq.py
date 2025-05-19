import taskiq_fastapi
from taskiq import InMemoryBroker
from config.settings import get_settings
from services.logging import init_logger
from taskiq_redis import RedisAsyncResultBackend
from taskiq.schedule_sources import LabelScheduleSource
from taskiq import TaskiqScheduler

settings = get_settings()
logger = init_logger()


in_memory_broker = InMemoryBroker()
redis_backend_broker = RedisAsyncResultBackend(settings.redis_url)


if settings.debug:
    broker = in_memory_broker
else:
    broker = redis_backend_broker


scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)


taskiq_fastapi.init(broker, "backend.main:app")
