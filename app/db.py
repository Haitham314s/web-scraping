import pathlib

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.cqlengine.connection import register_connection, set_default_connection

from .config import get_settings

settings = get_settings()

BASE_DIR = pathlib.Path(__file__).parent
CLUSTER_BUNDLE = str(BASE_DIR / "ignored" / "connect.zip")


def get_cluster():
    cloud_config = {
        'secure_connect_bundle': CLUSTER_BUNDLE
    }
    auth_provider = PlainTextAuthProvider(settings.db_client_id, settings.db_client_secret)
    return Cluster(cloud=cloud_config, auth_provider=auth_provider)


def get_session():
    cluster = get_cluster()
    session = cluster.connect()

    register_connection(str(session), session=session)
    set_default_connection(str(session))
    return session

