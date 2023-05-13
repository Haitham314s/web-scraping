from celery import Celery
from .config import get_settings

settings = get_settings()
celery_app = Celery(__name__)

REDIS_URL = settings.redis_url
celery_app.conf.broker_url = REDIS_URL
celery_app.conf.result_backend = REDIS_URL



@celery_app.task
def random_task(name):
    print(f"Who throws a shoe? Like honestly {name}")