from celery import Celery
from celery.signals import beat_init, worker_process_init
from cassandra.cqlengine.connection import register_connection, set_default_connection, cluster as connection_cluster, session as connection_session
from cassandra.cqlengine.management import sync_table

from .config import get_settings
from .db import get_cluster
from .models import Product, ProductScrapeEvent

settings = get_settings()
celery_app = Celery(__name__)

REDIS_URL = settings.redis_url
celery_app.conf.broker_url = REDIS_URL
celery_app.conf.result_backend = REDIS_URL


def celery_on_startup(*args, **kwargs):
    if connection_cluster is not None:
        connection_cluster.shutdown()
    if connection_session is not None:
        connection_session.shutdown()

    cluster = get_cluster()
    session = cluster.connect()
    register_connection(str(session), session=session)
    set_default_connection(str(session))

    sync_table(Product)
    sync_table(ProductScrapeEvent)


beat_init.connect(celery_on_startup)
worker_process_init.connect(celery_on_startup)


@celery_app.task
def random_task(name):
    print(f"Who throws a shoe? Like honestly {name}")


@celery_app.task
def list_products():
    print(list(Product.objects().all().values_list("asin", flat=True)))
