from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns

data = {
    "asin": "AMZNNUMBER",
    "title": "Mark 1"
}


class Product(Model):
    __keyspace__ = "scraper_app"
    asin = columns.Text(primary_key=True, required=True)
    title = columns.Text()
