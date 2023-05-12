from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine.connection import register_connection, set_default_connection
import pathlib
import os
from dotenv import load_dotenv

load_dotenv()
ASTRA_DB_CLIENT_ID = os.getenv("ASTRA_DB_CLIENT_ID")
ASTRA_DB_CLIENT_SECRET= os.get_env("ASTRA_DB_CLIENT_SECRET")

BASE_DIR = pathlib.Path(__file__).parent
CLUSTER_BUNDLE = str(BASE_DIR / "ignored" / "connect.zip")


def get_cluster():
    cloud_config = {
        'secure_connect_bundle': CLUSTER_BUNDLE
    }
    auth_provider = PlainTextAuthProvider(ASTRA_DB_CLIENT_ID, ASTRA_DB_CLIENT_SECRET)
    return Cluster(cloud=cloud_config, auth_provider=auth_provider)


def get_session():
    cluster = get_cluster()
    session = cluster.connect()

    register_connection(str(session), session=session)
    set_default_connection(str(session))
    return session


session = get_session()
if row := session.execute("select release_version from system.local").one():
    print(row[0])
else:
    print("An error occurred.")
