from typing import List

from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import _DoesNotExist
from fastapi import FastAPI, HTTPException, status

from .config import get_settings
from .crud import add_scrape_event
from .db import get_session
from .models import Product, ProductScrapeEvent
from .schema import ProductListSchema, ProductScrapeEventDetailSchema

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
    return list(Product.objects.all())


@app.post("/events/scrape")
def event_scrape_view(data: ProductListSchema):
    product, _ = add_scrape_event(data.model_dump())
    return product


@app.get("/products/{asin}")
def products_detail_view(asin: str):
    try:
        data = dict(Product.objects.get(asin=asin))
        events = list(ProductScrapeEvent.objects().filter(asin=asin).limit(5))
        events = [ProductScrapeEventDetailSchema(**event) for event in events]

        data["events"] = events
        data["events_url"] = f"/product/{asin}/events"

        return data
    except _DoesNotExist as e:
        print(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {asin} not found"
        )


@app.get("/products/{asin}/events", response_model=List[ProductListSchema])
def products_scrapes_list_view(asin: str):
    return list(ProductScrapeEvent.objects().filter(asin=asin))
