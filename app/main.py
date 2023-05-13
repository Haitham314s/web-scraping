from typing import List
from cassandra.cqlengine.management import sync_table
from fastapi import FastAPI

from .config import get_settings
from .db import get_session
from .models import Product, ProductScrapeEvent
from .schema import ProductListSchema

app = FastAPI()

settings = get_settings()
session = None


@app.on_event("startup")
def on_startup():
    global session
    session = get_session()

    sync_table(Product)
    sync_table(ProductScrapeEvent)


@app.get("/")
def read_index():
    return {"Hello": "FastAPI", "name": settings.name}


@app.get("/products", response_model=List[ProductListSchema])
def product_list_view():
    return {"results": list(Product.objects.all())}


@app.get("/product/{asin}")
def product_detail_view(asin: str):
    data = dict(Product.objects.get(asin=asin))
    events = list(ProductScrapeEvent.objects().filter(asin=asin))
    events = [ProductListSchema(**x) for x in events]
    data["events"] = events

    return data

