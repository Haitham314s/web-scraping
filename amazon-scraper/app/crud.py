import copy
from uuid import uuid1

from .models import Product, ProductScrapeEvent


def create_entry(data: dict):
    return Product.create(**data)


def create_scrape_entry(data: dict):
    data["uuid"] = uuid1()
    return ProductScrapeEvent.create(**data)


def add_scrape_event(data: dict, fresh=False):
    if fresh:
        data = copy.deepcopy(data)

    product = create_entry(data)
    scrape_event = create_scrape_entry(data)
    return product, scrape_event
