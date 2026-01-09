import psycopg2
import os

def get_connection():
    database_url = os.environ.get("DATABASE_PUBLIC_URL")

    if not database_url:
        raise Exception("DATABASE_PUBLIC_URL no está definida")

    return psycopg2.connect(database_url)
