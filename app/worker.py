from cassandra.cqlengine.connection import (
    register_connection,
    set_default_connection,
    cluster as connection_cluster,
    session as connection_session
)
from cassandra.cqlengine.management import sync_table
from celery import Celery
from celery.schedules import crontab
from celery.signals import beat_init, worker_process_init

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


@celery_app.on_after_configure.connect
def setup_periodic_task(sender, *args, **kwargs):
    # sender.add_periodic_task(1, random_task.s("Hello"), expires=10)
    #
    # sender.add_periodic_task(
    #     crontab(hour=8, minute=0, day_of_week=2),
    #     random_task.s("Hello"), expires=10
    # )

    sender.add_periodic_task(
        crontab(minutes="*/5"),
        scrape_products.s()
    )


@celery_app.task
def random_task(name):
    print(f"Who throws a shoe? Like honestly {name}")


@celery_app.task
def list_products():
    print(list(Product.objects().all().values_list("asin", flat=True)))


@celery_app.task
def scrape_asin(asin):
    print(f"Asin: {asin}")


@celery_app.task
def scrape_products():
    print("Scraping in progress...")

    q = list(Product.objects().all().values_list("asin", flat=True))
    for asin in q:
        scrape_asin.applly_async(asin)
